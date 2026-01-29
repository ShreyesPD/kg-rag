"""
Quick test script to verify KG-RAG setup
"""
import os
import sys

print("=" * 60)
print("KG-RAG Setup Verification")
print("=" * 60)
print()

# Test 1: Check config loading
print("✓ Testing configuration loading...")
try:
    from kg_rag.utility import config_data
    print(f"  ✓ Config loaded successfully")
    print(f"  ✓ Vector DB path: {config_data['VECTOR_DB_PATH']}")
except Exception as e:
    print(f"  ✗ Error loading config: {e}")
    sys.exit(1)

# Test 2: Check vector database
print()
print("✓ Checking vector database...")
if os.path.exists(config_data['VECTOR_DB_PATH']):
    print(f"  ✓ Vector database exists")
else:
    print(f"  ✗ Vector database not found")

# Test 3: Check API key configuration
print()
print("✓ Checking API key configuration...")
gpt_config_file = config_data['GPT_CONFIG_FILE']
if os.path.exists(gpt_config_file):
    print(f"  ✓ GPT config file exists: {gpt_config_file}")
    with open(gpt_config_file, 'r') as f:
        content = f.read()
        if 'your-api-key-here' in content:
            print(f"  ⚠️  WARNING: You need to add your OpenAI API key!")
            print(f"  ⚠️  Edit {gpt_config_file} and replace 'your-api-key-here'")
        elif 'OPENAI_API_KEY' in content or 'API_KEY' in content:
            print(f"  ✓ API key configuration looks good")
else:
    print(f"  ✗ GPT config file not found: {gpt_config_file}")

# Test 4: Check required data files
print()
print("✓ Checking required data files...")
required_files = [
    config_data['VECTOR_DB_DISEASE_ENTITY_PATH'],
    config_data['NODE_CONTEXT_PATH']
]
for file_path in required_files:
    if os.path.exists(file_path):
        print(f"  ✓ {os.path.basename(file_path)}")
    else:
        print(f"  ✗ Missing: {file_path}")

# Test 5: Test imports
print()
print("✓ Testing critical imports...")
try:
    import openai
    print(f"  ✓ openai")
except:
    print(f"  ✗ openai")

try:
    from langchain_community.vectorstores import Chroma
    print(f"  ✓ langchain_community")
except:
    print(f"  ✗ langchain_community")

try:
    from sentence_transformers import SentenceTransformer
    print(f"  ✓ sentence_transformers")
except:
    print(f"  ✗ sentence_transformers")

print()
print("=" * 60)
print("Setup verification complete!")
print("=" * 60)
print()
print("Next steps:")
print("1. Add your OpenAI API key to the .gpt_config.env file")
print("2. Run: python -m kg_rag.rag_based_generation.GPT.text_generation -g gpt-4")
print()
