"""
Medical Chatbot Web Application - Flask Backend
Integrates KG-RAG GPT interactive flow with web interface
"""
from flask import Flask, render_template, request, jsonify, session, Response, stream_with_context
from flask_cors import CORS
import sys
import os
import json
import time

# Add parent directory to path to import kg_rag modules
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
from kg_rag.config_loader import config_data
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
app.secret_key = 'medical-kg-rag-chatbot-secret-key-2026'
CORS(app)

# Initialize models and vectorstore
print("Loading models and vector database...")
SENTENCE_EMBEDDING_MODEL = config_data["VECTOR_DB_SENTENCE_EMBEDDING_MODEL"]
SENTENCE_EMBEDDING_MODEL_FOR_CONTEXT = config_data["SENTENCE_EMBEDDING_MODEL_FOR_CONTEXT_RETRIEVAL"]
VECTOR_DB_PATH = config_data["VECTOR_DB_PATH"]

embedding_function = load_sentence_transformer(SENTENCE_EMBEDDING_MODEL)
embedding_function_for_context = load_sentence_transformer(SENTENCE_EMBEDDING_MODEL_FOR_CONTEXT)
vectorstore = load_chroma(VECTOR_DB_PATH, SENTENCE_EMBEDDING_MODEL)

print("Models loaded successfully!")

def generate_interactive_stream(question):
    """
    Generator function that yields step-by-step updates as they happen
    Mimics the terminal interactive flow
    """
    try:
        # Initialize graph data structure
        graph_data = {
            'nodes': [],
            'edges': []
        }
        
        # Add question node
        graph_data['nodes'].append({
            'id': 'question',
            'label': question[:50] + '...' if len(question) > 50 else question,
            'type': 'question',
            'fullText': question
        })
        
        # Step 1: Disease entity extraction
        yield json.dumps({
            'type': 'step_start',
            'step': 1,
            'name': 'Disease Entity Extraction',
            'description': 'Extracting disease entities using GPT-3.5-Turbo...'
        }) + '\n'
        
        time.sleep(0.5)  # Small delay for visual effect
        
        entities = disease_entity_extractor_v2(question)
        
        if not entities:
            yield json.dumps({
                'type': 'step_complete',
                'step': 1,
                'status': 'warning',
                'result': 'No specific disease entities found. Using general search.'
            }) + '\n'
            entities = []
        else:
            # Add entity nodes to graph
            for i, entity in enumerate(entities):
                entity_id = f'entity_{i}'
                graph_data['nodes'].append({
                    'id': entity_id,
                    'label': entity,
                    'type': 'entity'
                })
                graph_data['edges'].append({
                    'source': 'question',
                    'target': entity_id,
                    'label': 'extracted_entity'
                })
            
            yield json.dumps({
                'type': 'step_complete',
                'step': 1,
                'status': 'completed',
                'result': f"Extracted entities: {', '.join(entities)}",
                'data': {'entities': entities}
            }) + '\n'
        
        # Step 2: Match entities to SPOKE nodes
        yield json.dumps({
            'type': 'step_start',
            'step': 2,
            'name': 'Entity Matching to SPOKE',
            'description': 'Finding vector similarity in knowledge graph...'
        }) + '\n'
        
        time.sleep(0.5)
        
        node_hits = []
        if entities:
            for i, entity in enumerate(entities):
                node_search_result = vectorstore.similarity_search_with_score(entity, k=1)
                node_name = node_search_result[0][0].page_content
                node_hits.append(node_name)
                
                # Add SPOKE node to graph
                node_id = f'spoke_node_{i}'
                graph_data['nodes'].append({
                    'id': node_id,
                    'label': node_name,
                    'type': 'spoke_node'
                })
                graph_data['edges'].append({
                    'source': f'entity_{i}',
                    'target': node_id,
                    'label': 'matched_to'
                })
        else:
            node_search_results = vectorstore.similarity_search_with_score(question, k=3)
            node_hits = [result[0].page_content for result in node_search_results]
            
            # Add SPOKE nodes to graph for general search
            for i, node_name in enumerate(node_hits):
                node_id = f'spoke_node_{i}'
                graph_data['nodes'].append({
                    'id': node_id,
                    'label': node_name,
                    'type': 'spoke_node'
                })
                graph_data['edges'].append({
                    'source': 'question',
                    'target': node_id,
                    'label': 'similar_to'
                })
        
        yield json.dumps({
            'type': 'step_complete',
            'step': 2,
            'status': 'completed',
            'result': f"Matched SPOKE nodes: {', '.join(node_hits)}",
            'data': {'nodes': node_hits}
        }) + '\n'
        
        # Step 3: Context extraction from SPOKE
        yield json.dumps({
            'type': 'step_start',
            'step': 3,
            'name': 'Context Extraction',
            'description': 'Retrieving biomedical context from SPOKE knowledge graph...'
        }) + '\n'
        
        time.sleep(0.5)
        
        node_contexts = []
        for i, node_name in enumerate(node_hits):
            context, context_table = get_context_using_spoke_api(node_name)
            node_contexts.append({'node': node_name, 'context': context, 'table': context_table, 'index': i})
            
            # Add context relationships to graph
            if context_table is not None and len(context_table) > 0:
                # Add sample of related entities from context
                unique_targets = context_table['target'].unique()[:5]  # Limit to 5 for visualization
                for j, target in enumerate(unique_targets):
                    context_node_id = f'context_{i}_{j}'
                    if target != node_name:  # Avoid self-loops
                        graph_data['nodes'].append({
                            'id': context_node_id,
                            'label': target[:30] + '...' if len(target) > 30 else target,
                            'type': 'context_entity'
                        })
                        graph_data['edges'].append({
                            'source': f'spoke_node_{i}',
                            'target': context_node_id,
                            'label': 'related_to'
                        })
        
        # Prepare context preview (show full context, will be scrollable in UI)
        context_preview = []
        for nc in node_contexts:
            context_preview.append({
                'node': nc['node'],
                'snippet': nc['context'],  # Show full context
                'total_length': len(nc['context'])
            })
        
        yield json.dumps({
            'type': 'step_complete',
            'step': 3,
            'status': 'completed',
            'result': f"Retrieved context from {len(node_hits)} knowledge graph nodes",
            'data': {'contexts': context_preview}
        }) + '\n'
        
        # Step 4: Context pruning
        yield json.dumps({
            'type': 'step_start',
            'step': 4,
            'name': 'Context Pruning',
            'description': 'Filtering most relevant context using semantic similarity...'
        }) + '\n'
        
        time.sleep(0.5)
        
        question_embedding = embedding_function_for_context.embed_query(question)
        node_context_extracted = ""
        pruned_context_count = 0
        
        max_contexts_per_node = int(config_data["CONTEXT_VOLUME"] / max(len(node_hits), 1))
        
        for nc in node_contexts:
            node_context = nc['context']
            node_context_list = node_context.split(". ")
            
            if len(node_context_list) > 1:
                node_context_embeddings = embedding_function_for_context.embed_documents(node_context_list)
                similarities = [
                    cosine_similarity(
                        np.array(question_embedding).reshape(1, -1),
                        np.array(node_context_embedding).reshape(1, -1)
                    )[0][0]
                    for node_context_embedding in node_context_embeddings
                ]
                
                percentile_threshold = np.percentile(
                    similarities,
                    config_data["QUESTION_VS_CONTEXT_SIMILARITY_PERCENTILE_THRESHOLD"]
                )
                
                high_similarity_indices = [
                    i for i, sim in enumerate(similarities)
                    if sim > percentile_threshold and sim > config_data["QUESTION_VS_CONTEXT_MINIMUM_SIMILARITY"]
                ]
                
                if len(high_similarity_indices) > max_contexts_per_node:
                    high_similarity_indices = high_similarity_indices[:max_contexts_per_node]
                
                high_similarity_context = [node_context_list[i] for i in high_similarity_indices]
                node_context_extracted += ". ".join(high_similarity_context) + ". "
                pruned_context_count += len(high_similarity_context)
            else:
                node_context_extracted += node_context + ". "
                pruned_context_count += 1
        
        # Prepare pruned context preview (full content, UI handles scrolling)
        pruned_preview = node_context_extracted.strip()

        yield json.dumps({
            'type': 'step_complete',
            'step': 4,
            'status': 'completed',
            'result': f'Pruned to {pruned_context_count} most relevant context statements',
            'data': {
                'count': pruned_context_count,
                'preview': pruned_preview,
                'total_length': len(node_context_extracted)
            }
        }) + '\n'
        
        # Step 5: LLM prompting
        yield json.dumps({
            'type': 'step_start',
            'step': 5,
            'name': 'GPT Response Generation',
            'description': 'Generating answer using GPT-3.5-Turbo with knowledge graph context...'
        }) + '\n'
        
        time.sleep(0.5)
        
        enriched_prompt = "Context: " + node_context_extracted + "\n\nQuestion: " + question
        
        chat_model_id = 'gpt-3.5-turbo'
        chat_deployment_id = None
        
        answer = get_GPT_response(
            enriched_prompt,
            system_prompts["KG_RAG_BASED_TEXT_GENERATION"],
            chat_model_id,
            chat_deployment_id,
            temperature=config_data["LLM_TEMPERATURE"]
        )
        
        # Add answer node to graph
        graph_data['nodes'].append({
            'id': 'answer',
            'label': answer[:50] + '...' if len(answer) > 50 else answer,
            'type': 'answer',
            'fullText': answer
        })
        
        # Connect SPOKE nodes to answer
        for i in range(len(node_hits)):
            graph_data['edges'].append({
                'source': f'spoke_node_{i}',
                'target': 'answer',
                'label': 'contributes_to'
            })
        
        yield json.dumps({
            'type': 'step_complete',
            'step': 5,
            'status': 'completed',
            'result': 'Answer generated successfully'
        }) + '\n'
        
        # Send graph data
        yield json.dumps({
            'type': 'graph_data',
            'graph': graph_data
        }) + '\n'
        
        # Send final answer
        yield json.dumps({
            'type': 'answer',
            'answer': answer
        }) + '\n'
        
        yield json.dumps({
            'type': 'complete'
        }) + '\n'
        
    except Exception as e:
        yield json.dumps({
            'type': 'error',
            'error': str(e)
        }) + '\n'

@app.route('/')
def index():
    """Serve the main chatbot interface"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat requests with streaming"""
    data = request.json
    question = data.get('question', '').strip()
    
    if not question:
        return jsonify({'error': 'No question provided'}), 400
    
    # Return streaming response
    return Response(
        stream_with_context(generate_interactive_stream(question)),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'models_loaded': True,
        'vectorstore_ready': True
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("Medical KG-RAG Chatbot Server Starting...")
    print("="*60)
    print("\nAccess the chatbot at: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
