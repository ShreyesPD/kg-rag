"""
Medical Chatbot Web Application - Enhanced with Dual Database Support
Integrates SPOKE API and Neo4j Clinical Trials with graph visualization
"""
from flask import Flask, render_template, request, jsonify, session, Response, stream_with_context
from flask_cors import CORS
import sys
import os
import json
import time
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from kg_rag.utility import (
    disease_entity_extractor_v2,
    load_sentence_transformer,
    load_chroma,
    get_context_using_spoke_api,
    get_GPT_response,
    config_data,
    system_prompts
)
from kg_rag.query_router import QueryRouter
from kg_rag.context_merger import ContextMerger
from kg_rag.neo4j_integration import Neo4jClient, Neo4jContextRetriever
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'medical-kg-rag-chatbot-dual-db-2026'
CORS(app)

print("Loading models and databases...")
SENTENCE_EMBEDDING_MODEL = config_data["VECTOR_DB_SENTENCE_EMBEDDING_MODEL"]
SENTENCE_EMBEDDING_MODEL_FOR_CONTEXT = config_data["SENTENCE_EMBEDDING_MODEL_FOR_CONTEXT_RETRIEVAL"]
VECTOR_DB_PATH = config_data["VECTOR_DB_PATH"]
ENABLE_NEO4J = config_data.get("ENABLE_NEO4J", False)
DEFAULT_DB_MODE = config_data.get("DEFAULT_DATABASE_MODE", "both")

embedding_function = load_sentence_transformer(SENTENCE_EMBEDDING_MODEL)
embedding_function_for_context = load_sentence_transformer(SENTENCE_EMBEDDING_MODEL_FOR_CONTEXT)
vectorstore = load_chroma(VECTOR_DB_PATH, SENTENCE_EMBEDDING_MODEL)

query_router = QueryRouter(default_mode=DEFAULT_DB_MODE)
context_merger = ContextMerger()

neo4j_client = None
neo4j_retriever = None

if ENABLE_NEO4J:
    try:
        neo4j_client = Neo4jClient()
        neo4j_retriever = Neo4jContextRetriever(neo4j_client)
        logger.info("Neo4j connection established")
    except Exception as e:
        logger.warning(f"Failed to connect to Neo4j: {str(e)}")
        ENABLE_NEO4J = False

print("Models and databases loaded successfully!")

def get_neo4j_context_and_graph(question: str):
    """Get context from Neo4j and return graph data for visualization"""
    if not neo4j_retriever:
        return "", {'nodes': [], 'edges': []}
    
    try:
        entities = query_router.extract_entities(question)
        context = ""
        graph_data = {'nodes': [], 'edges': []}
        
        if entities['nct_numbers']:
            nct = entities['nct_numbers'][0]
            context = neo4j_retriever.search_by_nct_number(nct)
            
            query = """
            MATCH (ct:ClinicalTrial {nct_number: $nct})
            OPTIONAL MATCH (ct)-[r1:STUDIES]->(c:Condition)
            OPTIONAL MATCH (ct)-[r2:USES_INTERVENTION]->(i:Intervention)
            OPTIONAL MATCH (ct)-[r3:SPONSORED_BY]->(s:Sponsor)
            RETURN ct, collect(DISTINCT {type: 'Condition', name: c.name}) as conditions,
                   collect(DISTINCT {type: 'Intervention', name: i.name}) as interventions,
                   collect(DISTINCT {type: 'Sponsor', name: s.name}) as sponsors
            """
            results = neo4j_client.execute_query(query, {'nct': nct})
            
            if results:
                result = results[0]
                graph_data['nodes'].append({
                    'id': nct,
                    'label': nct,
                    'type': 'clinical_trial',
                    'title': result['ct'].get('title', '')
                })
                
                for cond in result['conditions']:
                    if cond['name']:
                        graph_data['nodes'].append({
                            'id': f"cond_{cond['name']}",
                            'label': cond['name'],
                            'type': 'condition'
                        })
                        graph_data['edges'].append({
                            'source': nct,
                            'target': f"cond_{cond['name']}",
                            'label': 'STUDIES'
                        })
                
                for interv in result['interventions']:
                    if interv['name']:
                        graph_data['nodes'].append({
                            'id': f"interv_{interv['name']}",
                            'label': interv['name'],
                            'type': 'intervention'
                        })
                        graph_data['edges'].append({
                            'source': nct,
                            'target': f"interv_{interv['name']}",
                            'label': 'USES'
                        })
        else:
            question_lower = question.lower()
            
            if any(kw in question_lower for kw in ['drug', 'intervention', 'treatment']):
                for keyword in entities['keywords'][:2]:
                    if len(keyword) > 5:
                        context = neo4j_retriever.search_by_intervention(keyword, limit=3)
                        if "No clinical trials found" not in context:
                            break
            elif any(kw in question_lower for kw in ['condition', 'disease', 'cancer']):
                for keyword in entities['keywords'][:2]:
                    if len(keyword) > 5:
                        context = neo4j_retriever.search_by_condition(keyword, limit=3)
                        if "No" not in context:
                            break
            else:
                context = neo4j_retriever.search_by_keywords(entities['keywords'][:3], limit=3)
        
        return context, graph_data
        
    except Exception as e:
        logger.error(f"Error retrieving Neo4j context: {str(e)}")
        return "", {'nodes': [], 'edges': []}

def generate_dual_db_stream(question, db_mode='both'):
    """Generate streaming response with dual database support"""
    try:
        graph_data = {
            'nodes': [],
            'edges': []
        }
        
        graph_data['nodes'].append({
            'id': 'question',
            'label': question[:50] + '...' if len(question) > 50 else question,
            'type': 'question',
            'fullText': question
        })
        
        yield json.dumps({
            'type': 'info',
            'message': f'Database Mode: {db_mode.upper()}'
        }) + '\n'
        
        spoke_context = None
        neo4j_context = None
        neo4j_graph = {'nodes': [], 'edges': []}
        
        if db_mode in ['spoke', 'both']:
            yield json.dumps({
                'type': 'step_start',
                'step': 1,
                'name': 'SPOKE Knowledge Graph',
                'description': 'Extracting entities and retrieving biomedical context...'
            }) + '\n'
            
            time.sleep(0.3)
            
            entities = disease_entity_extractor_v2(question)
            
            if entities:
                node_hits = []
                for entity in entities:
                    result = vectorstore.similarity_search_with_score(entity, k=1)
                    node_hits.append(result[0][0].page_content)
            else:
                results = vectorstore.similarity_search_with_score(question, k=2)
                node_hits = [r[0].page_content for r in results]
            
            node_contexts = []
            for node_name in node_hits:
                context, _ = get_context_using_spoke_api(node_name)
                node_contexts.append(context)
            
            spoke_context = " ".join(node_contexts)
            
            yield json.dumps({
                'type': 'step_complete',
                'step': 1,
                'status': 'completed',
                'result': f'Retrieved context from {len(node_hits)} SPOKE nodes'
            }) + '\n'
        
        if db_mode in ['neo4j', 'both'] and ENABLE_NEO4J:
            yield json.dumps({
                'type': 'step_start',
                'step': 2,
                'name': 'Neo4j Clinical Trials',
                'description': 'Querying clinical trials database...'
            }) + '\n'
            
            time.sleep(0.3)
            
            neo4j_context, neo4j_graph = get_neo4j_context_and_graph(question)
            
            yield json.dumps({
                'type': 'step_complete',
                'step': 2,
                'status': 'completed',
                'result': 'Retrieved clinical trial data'
            }) + '\n'
        
        yield json.dumps({
            'type': 'step_start',
            'step': 3,
            'name': 'Context Merging',
            'description': 'Combining contexts from selected databases...'
        }) + '\n'
        
        time.sleep(0.3)
        
        merged_context = context_merger.merge_contexts(
            spoke_context=spoke_context,
            neo4j_context=neo4j_context,
            prioritize=db_mode
        )
        
        yield json.dumps({
            'type': 'step_complete',
            'step': 3,
            'status': 'completed',
            'result': f'Merged context ({len(merged_context)} characters)',
            'data': {'context_preview': merged_context[:500] + '...'}
        }) + '\n'
        
        yield json.dumps({
            'type': 'step_start',
            'step': 4,
            'name': 'GPT Response Generation',
            'description': 'Generating answer with GPT...'
        }) + '\n'
        
        time.sleep(0.3)
        
        enriched_prompt = "Context: " + merged_context + "\n\nQuestion: " + question
        
        answer = get_GPT_response(
            enriched_prompt,
            system_prompts["KG_RAG_BASED_TEXT_GENERATION"],
            'gpt-3.5-turbo',
            None,
            temperature=config_data["LLM_TEMPERATURE"]
        )
        
        graph_data['nodes'].append({
            'id': 'answer',
            'label': answer[:50] + '...' if len(answer) > 50 else answer,
            'type': 'answer',
            'fullText': answer
        })
        
        yield json.dumps({
            'type': 'step_complete',
            'step': 4,
            'status': 'completed',
            'result': 'Answer generated successfully'
        }) + '\n'
        
        if neo4j_graph['nodes']:
            yield json.dumps({
                'type': 'graph_data',
                'graph': neo4j_graph
            }) + '\n'
        else:
            yield json.dumps({
                'type': 'graph_data',
                'graph': graph_data
            }) + '\n'
        
        yield json.dumps({
            'type': 'answer',
            'answer': answer
        }) + '\n'
        
        yield json.dumps({
            'type': 'complete'
        }) + '\n'
        
    except Exception as e:
        logger.error(f"Error in stream generation: {str(e)}", exc_info=True)
        yield json.dumps({
            'type': 'error',
            'error': str(e)
        }) + '\n'

@app.route('/')
def index():
    return render_template('index_dual_db.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    question = data.get('question', '').strip()
    db_mode = data.get('db_mode', DEFAULT_DB_MODE)
    
    if not question:
        return jsonify({'error': 'No question provided'}), 400
    
    if db_mode not in ['spoke', 'neo4j', 'both']:
        db_mode = DEFAULT_DB_MODE
    
    return Response(
        stream_with_context(generate_dual_db_stream(question, db_mode)),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'spoke_ready': True,
        'neo4j_ready': ENABLE_NEO4J,
        'default_mode': DEFAULT_DB_MODE
    })

@app.route('/api/graph/<nct_number>', methods=['GET'])
def get_trial_graph(nct_number):
    """Get graph visualization data for a specific clinical trial"""
    if not ENABLE_NEO4J or not neo4j_client:
        return jsonify({'error': 'Neo4j not available'}), 503
    
    try:
        query = """
        MATCH (ct:ClinicalTrial {nct_number: $nct})
        OPTIONAL MATCH (ct)-[:STUDIES]->(c:Condition)
        OPTIONAL MATCH (ct)-[:USES_INTERVENTION]->(i:Intervention)
        OPTIONAL MATCH (ct)-[:SPONSORED_BY]->(s:Sponsor)
        OPTIONAL MATCH (i)-[:TREATS]->(tc:Condition)
        RETURN ct,
               collect(DISTINCT {name: c.name}) as conditions,
               collect(DISTINCT {name: i.name, type: i.type}) as interventions,
               collect(DISTINCT {name: s.name}) as sponsors,
               collect(DISTINCT {name: tc.name}) as treats_conditions
        """
        
        results = neo4j_client.execute_query(query, {'nct': nct_number})
        
        if not results:
            return jsonify({'error': 'Trial not found'}), 404
        
        result = results[0]
        ct = result['ct']
        
        graph = {
            'nodes': [
                {
                    'id': nct_number,
                    'label': nct_number,
                    'type': 'clinical_trial',
                    'title': ct.get('title', ''),
                    'status': ct.get('status', '')
                }
            ],
            'edges': []
        }
        
        for cond in result['conditions']:
            if cond['name']:
                graph['nodes'].append({
                    'id': f"cond_{cond['name']}",
                    'label': cond['name'],
                    'type': 'condition'
                })
                graph['edges'].append({
                    'source': nct_number,
                    'target': f"cond_{cond['name']}",
                    'label': 'STUDIES'
                })
        
        for interv in result['interventions']:
            if interv['name']:
                graph['nodes'].append({
                    'id': f"interv_{interv['name']}",
                    'label': interv['name'],
                    'type': 'intervention'
                })
                graph['edges'].append({
                    'source': nct_number,
                    'target': f"interv_{interv['name']}",
                    'label': 'USES'
                })
        
        for sponsor in result['sponsors']:
            if sponsor['name']:
                graph['nodes'].append({
                    'id': f"sponsor_{sponsor['name']}",
                    'label': sponsor['name'],
                    'type': 'sponsor'
                })
                graph['edges'].append({
                    'source': nct_number,
                    'target': f"sponsor_{sponsor['name']}",
                    'label': 'SPONSORED_BY'
                })
        
        return jsonify(graph)
        
    except Exception as e:
        logger.error(f"Error getting trial graph: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    print("\n" + "="*60)
    print("Medical KG-RAG Chatbot (Dual Database) Server Starting...")
    print("="*60)
    print(f"\nSPOKE API: Enabled")
    print(f"Neo4j: {'Enabled' if ENABLE_NEO4J else 'Disabled'}")
    print(f"Default Mode: {DEFAULT_DB_MODE}")
    print(f"\nAccess the chatbot at: http://localhost:{port}")
    print("\nPress Ctrl+C to stop the server\n")
    
    try:
        app.run(debug=debug, host='0.0.0.0', port=port)
    finally:
        if neo4j_client:
            neo4j_client.close()
            logger.info("Neo4j connection closed")
