"""
Enhanced text generation with dual-database support (SPOKE + Neo4j)
Command line arguments:
    -g: GPT model selection (default: gpt-35-turbo)
    -i: Interactive mode flag (default: False)
    -e: Show evidence flag (default: False)
    -d: Database mode - 'spoke', 'neo4j', or 'both' (default: from config)
"""

from kg_rag.utility import *
from kg_rag.query_router import QueryRouter
from kg_rag.context_merger import ContextMerger
from kg_rag.neo4j_integration import Neo4jClient, Neo4jContextRetriever
import argparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument('-g', type=str, default='gpt-35-turbo', help='GPT model selection')
parser.add_argument('-i', type=bool, default=False, help='Flag for interactive mode')
parser.add_argument('-e', type=bool, default=False, help='Flag for showing evidence of association from the graph')
parser.add_argument('-d', type=str, default=None, help='Database mode: spoke, neo4j, or both')
args = parser.parse_args()

CHAT_MODEL_ID = args.g
INTERACTIVE = args.i
EDGE_EVIDENCE = bool(args.e)
DATABASE_MODE = args.d or config_data.get("DEFAULT_DATABASE_MODE", "both")

SYSTEM_PROMPT = system_prompts["KG_RAG_BASED_TEXT_GENERATION"]
CONTEXT_VOLUME = int(config_data["CONTEXT_VOLUME"])
QUESTION_VS_CONTEXT_SIMILARITY_PERCENTILE_THRESHOLD = float(config_data["QUESTION_VS_CONTEXT_SIMILARITY_PERCENTILE_THRESHOLD"])
QUESTION_VS_CONTEXT_MINIMUM_SIMILARITY = float(config_data["QUESTION_VS_CONTEXT_MINIMUM_SIMILARITY"])
VECTOR_DB_PATH = config_data["VECTOR_DB_PATH"]
NODE_CONTEXT_PATH = config_data["NODE_CONTEXT_PATH"]
SENTENCE_EMBEDDING_MODEL_FOR_NODE_RETRIEVAL = config_data["SENTENCE_EMBEDDING_MODEL_FOR_NODE_RETRIEVAL"]
SENTENCE_EMBEDDING_MODEL_FOR_CONTEXT_RETRIEVAL = config_data["SENTENCE_EMBEDDING_MODEL_FOR_CONTEXT_RETRIEVAL"]
TEMPERATURE = config_data["LLM_TEMPERATURE"]
ENABLE_NEO4J = config_data.get("ENABLE_NEO4J", False)

CHAT_DEPLOYMENT_ID = CHAT_MODEL_ID if openai.api_type == "azure" else None

vectorstore = load_chroma(VECTOR_DB_PATH, SENTENCE_EMBEDDING_MODEL_FOR_NODE_RETRIEVAL)
embedding_function_for_context_retrieval = load_sentence_transformer(SENTENCE_EMBEDDING_MODEL_FOR_CONTEXT_RETRIEVAL)
node_context_df = pd.read_csv(NODE_CONTEXT_PATH)

query_router = QueryRouter(default_mode=DATABASE_MODE)
context_merger = ContextMerger()

neo4j_client = None
neo4j_retriever = None

if ENABLE_NEO4J:
    try:
        neo4j_client = Neo4jClient()
        neo4j_retriever = Neo4jContextRetriever(neo4j_client)
        logger.info("Neo4j connection established")
    except Exception as e:
        logger.warning(f"Failed to connect to Neo4j: {str(e)}. Falling back to SPOKE only.")
        ENABLE_NEO4J = False

def get_neo4j_context(question: str) -> str:
    """
    Retrieve context from Neo4j clinical trials database
    """
    if not neo4j_retriever:
        return ""
    
    try:
        entities = query_router.extract_entities(question)
        
        if entities['nct_numbers']:
            context = neo4j_retriever.search_by_nct_number(entities['nct_numbers'][0])
            return context
        
        question_lower = question.lower()
        
        if any(kw in question_lower for kw in ['zanidatamab', 'drug', 'intervention', 'treatment', 'medication']):
            for keyword in entities['keywords']:
                if len(keyword) > 5:
                    context = neo4j_retriever.search_by_intervention(keyword, limit=3)
                    if "No clinical trials found" not in context:
                        return context
        
        if any(kw in question_lower for kw in ['condition', 'disease', 'cancer', 'tumor']):
            for keyword in entities['keywords']:
                if len(keyword) > 5:
                    context = neo4j_retriever.search_by_condition(keyword, limit=3)
                    if "No" not in context:
                        return context
        
        context = neo4j_retriever.search_by_keywords(entities['keywords'][:3], limit=3)
        return context
        
    except Exception as e:
        logger.error(f"Error retrieving Neo4j context: {str(e)}")
        return ""

def get_dual_database_context(question: str, db_mode: str = None) -> str:
    """
    Retrieve context from both SPOKE and Neo4j based on routing
    """
    if db_mode is None:
        db_mode = query_router.route_query(question, user_preference=DATABASE_MODE)
    
    spoke_context = None
    neo4j_context = None
    
    if db_mode in ['spoke', 'both']:
        try:
            logger.info("Retrieving context from SPOKE...")
            spoke_context = retrieve_context(
                question, 
                vectorstore, 
                embedding_function_for_context_retrieval, 
                node_context_df, 
                CONTEXT_VOLUME, 
                QUESTION_VS_CONTEXT_SIMILARITY_PERCENTILE_THRESHOLD, 
                QUESTION_VS_CONTEXT_MINIMUM_SIMILARITY, 
                EDGE_EVIDENCE
            )
        except Exception as e:
            logger.error(f"Error retrieving SPOKE context: {str(e)}")
    
    if db_mode in ['neo4j', 'both'] and ENABLE_NEO4J:
        try:
            logger.info("Retrieving context from Neo4j...")
            neo4j_context = get_neo4j_context(question)
        except Exception as e:
            logger.error(f"Error retrieving Neo4j context: {str(e)}")
    
    merged_context = context_merger.merge_contexts(
        spoke_context=spoke_context,
        neo4j_context=neo4j_context,
        prioritize=db_mode
    )
    
    return merged_context

def main():
    print("\n" + "="*60)
    print("KG-RAG with Dual Database Support")
    print(f"Database Mode: {DATABASE_MODE}")
    print(f"Neo4j Enabled: {ENABLE_NEO4J}")
    print("="*60 + "\n")
    
    question = input("Enter your question: ")
    
    if not INTERACTIVE:
        print(f"\nRetrieving context (mode: {DATABASE_MODE})...")
        context = get_dual_database_context(question)
        
        print("\nGenerating answer...")
        enriched_prompt = "Context: " + context + "\n" + "Question: " + question
        output = get_GPT_response(enriched_prompt, SYSTEM_PROMPT, CHAT_MODEL_ID, CHAT_DEPLOYMENT_ID, temperature=TEMPERATURE)
        
        print("\n" + "="*60)
        print("ANSWER:")
        print("="*60)
        stream_out(output)
    else:
        interactive_dual_db(question)

def interactive_dual_db(question: str):
    """
    Interactive mode with database selection
    """
    print("\n" + "="*60)
    print("INTERACTIVE MODE - Dual Database")
    print("="*60)
    
    print("\nSelect database source:")
    print("1. SPOKE only")
    print("2. Neo4j only")
    print("3. Both (default)")
    
    choice = input("\nEnter choice (1/2/3) [3]: ").strip()
    
    db_mode_map = {'1': 'spoke', '2': 'neo4j', '3': 'both', '': 'both'}
    selected_mode = db_mode_map.get(choice, 'both')
    
    print(f"\nUsing database mode: {selected_mode}")
    print("\nRetrieving context...")
    
    context = get_dual_database_context(question, db_mode=selected_mode)
    
    print("\n" + "="*60)
    print("RETRIEVED CONTEXT:")
    print("="*60)
    print(context)
    
    proceed = input("\n\nProceed with this context? (y/n) [y]: ").strip().lower()
    
    if proceed == 'n':
        print("Context retrieval cancelled.")
        return
    
    print("\nGenerating answer...")
    enriched_prompt = "Context: " + context + "\n" + "Question: " + question
    output = get_GPT_response(enriched_prompt, SYSTEM_PROMPT, CHAT_MODEL_ID, CHAT_DEPLOYMENT_ID, temperature=TEMPERATURE)
    
    print("\n" + "="*60)
    print("ANSWER:")
    print("="*60)
    stream_out(output)

if __name__ == "__main__":
    try:
        main()
    finally:
        if neo4j_client:
            neo4j_client.close()
            logger.info("Neo4j connection closed")
