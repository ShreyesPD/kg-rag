# Quick Start: Dual Database KG-RAG

Get started with the enhanced KG-RAG system that combines SPOKE biomedical knowledge with Neo4j clinical trials data.

## 🚀 Quick Setup (5 minutes)

### 1. Ensure Neo4j is Running

```bash
# Check Neo4j status
neo4j status

# If not running, start it
neo4j start
```

### 2. Load Clinical Trial Data

```bash
# From KG_RAG root directory
python scripts/ingest_clinical_trials.py
```

Wait for completion message showing database statistics.

### 3. Start the Web Interface

```bash
python medical_chatbot_webapp/app_dual_db.py
```

### 4. Open Browser

Navigate to: **http://localhost:5000**

## 💡 Usage Examples

### Web Interface

1. **Select Database Mode**: Choose SPOKE, Neo4j, or Both
2. **Ask a Question**: Type your medical question
3. **View Results**: See step-by-step processing and graph visualization

### Command Line

```bash
# Both databases (default)
python -m kg_rag.rag_based_generation.GPT.text_generation_dual_db

# SPOKE only
python -m kg_rag.rag_based_generation.GPT.text_generation_dual_db -d spoke

# Neo4j only
python -m kg_rag.rag_based_generation.GPT.text_generation_dual_db -d neo4j

# Interactive mode
python -m kg_rag.rag_based_generation.GPT.text_generation_dual_db -i True
```

## 📊 Sample Questions

**Clinical Trials (Neo4j):**
- "What is Zanidatamab used for?"
- "Tell me about trial NCT06695845"
- "What trials study HER2-expressing tumors?"

**Biomedical Knowledge (SPOKE):**
- "What genes are associated with breast cancer?"
- "How does HER2 work?"
- "What proteins interact with EGFR?"

**Combined (Both):**
- "What do we know about Zanidatamab and HER2?"
- "Clinical trials for breast cancer and genetic associations"

## 🎯 Key Features

✅ **Dual Database Querying**: Access both SPOKE and Neo4j
✅ **Smart Routing**: Automatic database selection based on question
✅ **Graph Visualization**: Interactive D3.js visualizations
✅ **User Control**: Choose which database(s) to query
✅ **Streaming Responses**: Real-time step-by-step updates

## 📁 Project Structure

```
KG_RAG/
├── kg_rag/
│   ├── neo4j_integration/      # Neo4j modules
│   │   ├── neo4j_client.py
│   │   ├── csv_parser.py
│   │   ├── graph_builder.py
│   │   └── context_retriever.py
│   ├── query_router.py         # Database routing logic
│   └── context_merger.py       # Context merging
├── scripts/
│   └── ingest_clinical_trials.py  # Data ingestion CLI
├── medical_chatbot_webapp/
│   ├── app_dual_db.py          # Enhanced Flask app
│   └── templates/
│       └── index_dual_db.html  # Dual-DB UI
└── jazz_data/
    └── NCT06695845 (1).csv     # Clinical trial data
```

## 🔧 Configuration

Edit `config.yaml`:

```yaml
# Enable/disable Neo4j
ENABLE_NEO4J : True

# Default database mode
DEFAULT_DATABASE_MODE : 'both'  # 'spoke', 'neo4j', or 'both'

# Neo4j connection (uses .env credentials)
NEO4J_URI : 'bolt://localhost:7687'
NEO4J_USER : 'neo4j'
NEO4J_DATABASE : 'neo4j'
```

## 🐛 Troubleshooting

**Neo4j not connecting?**
```bash
# Check if running
neo4j status

# Verify credentials in .env
cat .env | grep NEO4J
```

**No data in Neo4j?**
```bash
# Re-ingest with clear flag
python scripts/ingest_clinical_trials.py --clear
```

**Web app shows "Neo4j: Disabled"?**
- Set `ENABLE_NEO4J: True` in `config.yaml`
- Restart the web app

## 📚 Documentation

- **Full Setup Guide**: `docs/NEO4J_SETUP_GUIDE.md`
- **Original README**: `README.md`
- **SPOKE API Docs**: https://spoke.rbvi.ucsf.edu

## 🎓 How It Works

1. **Question Analysis**: Router determines which database(s) to query
2. **Context Retrieval**: 
   - SPOKE: Disease entities → API → Biomedical context
   - Neo4j: Keywords → Cypher queries → Clinical trial context
3. **Context Merging**: Combines contexts from both sources
4. **GPT Generation**: Enriched prompt → GPT → Answer
5. **Visualization**: Graph data → D3.js → Interactive visualization

## 🚦 System Status Check

```bash
# Check Neo4j
python scripts/ingest_clinical_trials.py --stats

# Check web app health
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "spoke_ready": true,
  "neo4j_ready": true,
  "default_mode": "both"
}
```

## 🎉 You're Ready!

Start asking medical questions and explore the dual-database knowledge graph system!
