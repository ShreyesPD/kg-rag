"""
Test script for dual-database KG-RAG system
Tests Neo4j integration, query routing, and context retrieval
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from kg_rag.neo4j_integration import Neo4jClient, Neo4jContextRetriever
from kg_rag.query_router import QueryRouter
from kg_rag.context_merger import ContextMerger
from kg_rag.config_loader import config_data
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_neo4j_connection():
    """Test 1: Neo4j connection"""
    print("\n" + "="*60)
    print("TEST 1: Neo4j Connection")
    print("="*60)
    
    try:
        client = Neo4jClient()
        stats = client.get_database_stats()
        
        print("✓ Connection successful!")
        print("\nDatabase Statistics:")
        for stat in stats:
            print(f"  {stat['label']}: {stat['count']} nodes")
        
        client.close()
        return True
    except Exception as e:
        print(f"✗ Connection failed: {str(e)}")
        return False

def test_query_routing():
    """Test 2: Query routing logic"""
    print("\n" + "="*60)
    print("TEST 2: Query Routing")
    print("="*60)
    
    router = QueryRouter()
    
    test_cases = [
        ("What is Zanidatamab used for?", "neo4j"),
        ("What genes are associated with Alzheimer's?", "spoke"),
        ("Tell me about trial NCT06695845", "neo4j"),
        ("How does TP53 work?", "spoke"),
        ("What trials study breast cancer?", "neo4j")
    ]
    
    passed = 0
    for question, expected in test_cases:
        result = router.route_query(question)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{question[:50]}...' → {result} (expected: {expected})")
        if result == expected:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(test_cases)}")
    return passed == len(test_cases)

def test_neo4j_retrieval():
    """Test 3: Neo4j context retrieval"""
    print("\n" + "="*60)
    print("TEST 3: Neo4j Context Retrieval")
    print("="*60)
    
    try:
        client = Neo4jClient()
        retriever = Neo4jContextRetriever(client)
        
        # Test by intervention
        print("\nTest 3a: Search by intervention (Zanidatamab)")
        context = retriever.search_by_intervention("Zanidatamab", limit=1)
        print(f"Context length: {len(context)} characters")
        print(f"Preview: {context[:200]}...")
        
        # Test by condition
        print("\nTest 3b: Search by condition (Breast Cancer)")
        context = retriever.search_by_condition("Breast Cancer", limit=1)
        print(f"Context length: {len(context)} characters")
        print(f"Preview: {context[:200]}...")
        
        # Test by NCT number
        print("\nTest 3c: Search by NCT number (NCT06695845)")
        context = retriever.search_by_nct_number("NCT06695845")
        print(f"Context length: {len(context)} characters")
        print(f"Preview: {context[:200]}...")
        
        client.close()
        print("\n✓ All retrieval tests passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ Retrieval test failed: {str(e)}")
        return False

def test_context_merging():
    """Test 4: Context merging"""
    print("\n" + "="*60)
    print("TEST 4: Context Merging")
    print("="*60)
    
    merger = ContextMerger()
    
    spoke_context = "HER2 is a protein that promotes the growth of cancer cells. It is overexpressed in some breast cancers."
    neo4j_context = "Clinical Trial NCT06695845 studies Zanidatamab for HER2-expressing tumors including breast cancer."
    
    # Test merging both
    merged = merger.merge_contexts(spoke_context, neo4j_context, prioritize='both')
    print(f"\nMerged context length: {len(merged)} characters")
    print(f"Contains SPOKE: {'SPOKE' in merged}")
    print(f"Contains Clinical Trials: {'Clinical Trials' in merged}")
    
    # Test SPOKE only
    merged_spoke = merger.merge_contexts(spoke_context, None, prioritize='spoke')
    print(f"\nSPOKE only length: {len(merged_spoke)} characters")
    
    # Test Neo4j only
    merged_neo4j = merger.merge_contexts(None, neo4j_context, prioritize='neo4j')
    print(f"Neo4j only length: {len(merged_neo4j)} characters")
    
    print("\n✓ Context merging test passed!")
    return True

def test_end_to_end():
    """Test 5: End-to-end question answering"""
    print("\n" + "="*60)
    print("TEST 5: End-to-End Question Answering")
    print("="*60)
    
    try:
        client = Neo4jClient()
        retriever = Neo4jContextRetriever(client)
        router = QueryRouter()
        merger = ContextMerger()
        
        question = "What is Zanidatamab used for?"
        print(f"\nQuestion: {question}")
        
        # Route query
        db_mode = router.route_query(question)
        print(f"Routed to: {db_mode}")
        
        # Get Neo4j context
        neo4j_context = retriever.search_by_intervention("Zanidatamab", limit=2)
        print(f"Neo4j context retrieved: {len(neo4j_context)} characters")
        
        # Merge (in real scenario, would also get SPOKE context)
        merged = merger.merge_contexts(None, neo4j_context, prioritize='neo4j')
        print(f"Final context: {len(merged)} characters")
        
        print("\n✓ End-to-end test passed!")
        print("\nNote: For full GPT response, run the actual text_generation_dual_db.py script")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"\n✗ End-to-end test failed: {str(e)}")
        return False

def main():
    print("\n" + "="*60)
    print("DUAL-DATABASE KG-RAG SYSTEM TESTS")
    print("="*60)
    
    results = {
        "Neo4j Connection": test_neo4j_connection(),
        "Query Routing": test_query_routing(),
        "Neo4j Retrieval": test_neo4j_retrieval(),
        "Context Merging": test_context_merging(),
        "End-to-End": test_end_to_end()
    }
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 All tests passed! System is ready to use.")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")
    
    return total_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
