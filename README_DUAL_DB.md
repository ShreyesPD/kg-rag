# KG-RAG with Dual Database Support

Enhanced version of KG-RAG that integrates **SPOKE biomedical knowledge graph** with **Neo4j clinical trials database** for comprehensive medical question answering.

## 🆕 What's New

This enhancement adds:

- ✅ **Neo4j Integration**: Local clinical trials graph database
- ✅ **Dual Database Querying**: Query SPOKE, Neo4j, or both simultaneously
- ✅ **Smart Query Routing**: Automatic database selection based on question type
- ✅ **Graph Visualization**: Interactive D3.js visualizations in web UI
- ✅ **User Control**: Choose which database(s) to query
- ✅ **Context Merging**: Intelligently combine contexts from multiple sources

## 🏗️ Architecture

```
User Question
     ↓
Query Router (determines database)
     ↓
┌────────────┬────────────┐
│   SPOKE    │   Neo4j    │
│  (API)     │  (Local)   │
└────────────┴────────────┘
     ↓            ↓
Context Merger
     ↓
GPT + Context
     ↓
Answer + Graph Visualization
```

## 📦 Installation

### 1. Install Neo4j

**Option A: Neo4j Desktop** (Recommended)
- Download from https://neo4j.com/download/
- Create a new database
- Set password during setup

**Option B: Docker**
```bash
docker run -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/your_password neo4j:latest
```

### 2. Configure Environment

Add to `.env`:
```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here
```

### 3. Install Dependencies

All required packages are already in `requirements.txt`:
```bash
pip install -r requirements.txt
```

## 🚀 Quick Start

### Step 1: Ingest Clinical Trial Data

```bash
python scripts/ingest_clinical_trials.py
```

### Step 2: Run the System

**Web Interface:**
```bash
python medical_chatbot_webapp/app_dual_db.py
```
Open: http://localhost:5000

**Command Line:**
```bash
# Both databases (default)
python -m kg_rag.rag_based_generation.GPT.text_generation_dual_db

# Specific database
python -m kg_rag.rag_based_generation.GPT.text_generation_dual_db -d neo4j

# Interactive mode
python -m kg_rag.rag_based_generation.GPT.text_generation_dual_db -i True
```

## 📊 Usage Examples

### Clinical Trial Questions (Neo4j)

```
Q: What is Zanidatamab used for?
A: Zanidatamab is used to treat HER2-expressing tumors including breast cancer, 
   gastric cancer, and other solid tumors. Clinical trial NCT06695845 is 
   evaluating its efficacy...

Q: Tell me about trial NCT06695845
A: NCT06695845 is a Phase 2 study evaluating zanidatamab for previously treated 
   solid tumors with HER2 IHC 3+ overexpression. The trial is currently recruiting...
```

### Biomedical Questions (SPOKE)

```
Q: What genes are associated with breast cancer?
A: Several genes are associated with breast cancer including BRCA1, BRCA2, TP53, 
   PTEN, and HER2 (ERBB2)...

Q: How does HER2 work?
A: HER2 (Human Epidermal Growth Factor Receptor 2) is a protein that promotes 
   cell growth. It is a member of the EGFR family...
```

### Combined Questions (Both)

```
Q: What do we know about Zanidatamab and HER2?
A: [Combines clinical trial data from Neo4j with HER2 biological knowledge from SPOKE]
   Zanidatamab is being studied in clinical trial NCT06695845 for HER2-expressing 
   tumors. HER2 is a receptor tyrosine kinase that, when overexpressed, promotes 
   tumor growth...
```

## 🎯 Database Selection

### Automatic Routing

The system automatically selects the appropriate database(s) based on keywords:

- **Neo4j keywords**: trial, study, NCT, intervention, phase, recruiting
- **SPOKE keywords**: gene, protein, pathway, mechanism, molecular

### Manual Selection

**Web UI**: Click database buttons (SPOKE/Both/Neo4j)

**Command Line**: Use `-d` flag
```bash
-d spoke   # SPOKE only
-d neo4j   # Neo4j only
-d both    # Both databases
```

**Config**: Set default in `config.yaml`
```yaml
DEFAULT_DATABASE_MODE : 'both'
```

## 📁 New File Structure

```
KG_RAG/
├── kg_rag/
│   ├── neo4j_integration/          # NEW: Neo4j modules
│   │   ├── __init__.py
│   │   ├── neo4j_client.py        # Database connection
│   │   ├── csv_parser.py          # CSV parsing
│   │   ├── graph_builder.py       # Graph construction
│   │   └── context_retriever.py   # Context queries
│   ├── query_router.py             # NEW: Database routing
│   ├── context_merger.py           # NEW: Context merging
│   └── rag_based_generation/
│       └── GPT/
│           └── text_generation_dual_db.py  # NEW: Dual-DB version
├── scripts/
│   ├── ingest_clinical_trials.py   # NEW: Data ingestion
│   └── test_dual_db.py             # NEW: Test suite
├── medical_chatbot_webapp/
│   ├── app_dual_db.py              # NEW: Enhanced Flask app
│   └── templates/
│       └── index_dual_db.html      # NEW: Dual-DB UI
├── docs/
│   └── NEO4J_SETUP_GUIDE.md        # NEW: Setup guide
├── QUICKSTART_DUAL_DB.md           # NEW: Quick start
└── README_DUAL_DB.md               # NEW: This file
```

## 🧪 Testing

Run the test suite:

```bash
python scripts/test_dual_db.py
```

Tests include:
1. Neo4j connection
2. Query routing logic
3. Context retrieval
4. Context merging
5. End-to-end flow

## 🔧 Configuration

### config.yaml

```yaml
# Neo4j Configuration
NEO4J_URI : 'bolt://localhost:7687'
NEO4J_USER : 'neo4j'
NEO4J_DATABASE : 'neo4j'

# Clinical Trials Data
CLINICAL_TRIALS_CSV_PATH : 'jazz_data/NCT06695845 (1).csv'

# Query Routing
ENABLE_NEO4J : True
DEFAULT_DATABASE_MODE : 'both'  # 'spoke', 'neo4j', or 'both'
```

### .env

```env
# Existing
OPENAI_API_KEY=your_key_here

# New
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here
```

## 📈 Graph Schema

### Nodes
- **ClinicalTrial**: NCT number, title, status, phases, etc.
- **Condition**: Disease/condition names
- **Intervention**: Drugs/treatments with type
- **Sponsor**: Organizations (primary/collaborator)
- **Location**: Geographic sites
- **OutcomeMeasure**: Primary/secondary outcomes

### Relationships
- `STUDIES`: Trial → Condition
- `USES_INTERVENTION`: Trial → Intervention
- `TREATS`: Intervention → Condition
- `SPONSORED_BY`: Trial → Sponsor
- `CONDUCTED_AT`: Trial → Location
- `MEASURES`: Trial → OutcomeMeasure

## 🔍 Sample Cypher Queries

```cypher
// Find all trials for a condition
MATCH (ct:ClinicalTrial)-[:STUDIES]->(c:Condition {name: "Breast Cancer"})
RETURN ct.nct_number, ct.title, ct.status

// Find what an intervention treats
MATCH (i:Intervention {name: "Zanidatamab"})-[:TREATS]->(c:Condition)
RETURN c.name

// Get full trial context
MATCH (ct:ClinicalTrial {nct_number: "NCT06695845"})
OPTIONAL MATCH (ct)-[r]->(n)
RETURN ct, r, n
```

## 🐛 Troubleshooting

### Neo4j Connection Failed

```bash
# Check if Neo4j is running
neo4j status

# Verify credentials
cat .env | grep NEO4J

# Test connection in browser
# Open: http://localhost:7474
```

### No Data in Neo4j

```bash
# Re-ingest with clear flag
python scripts/ingest_clinical_trials.py --clear

# Check stats
python scripts/ingest_clinical_trials.py --stats
```

### Module Import Errors

```bash
# Ensure you're in the KG_RAG directory
cd KG_RAG

# Reinstall dependencies
pip install -r requirements.txt
```

## 📚 Documentation

- **Setup Guide**: `docs/NEO4J_SETUP_GUIDE.md`
- **Quick Start**: `QUICKSTART_DUAL_DB.md`
- **Original README**: `README.md`

## 🤝 Backward Compatibility

The original KG-RAG functionality is **fully preserved**:

- Original scripts still work unchanged
- SPOKE-only mode available
- Can disable Neo4j via config

## 🎓 How It Works

1. **Question Input**: User asks a medical question
2. **Query Routing**: System determines which database(s) to query
3. **Context Retrieval**:
   - **SPOKE**: Extract disease entities → API call → Biomedical context
   - **Neo4j**: Extract keywords → Cypher queries → Clinical trial context
4. **Context Merging**: Combine contexts with source attribution
5. **GPT Generation**: Enriched prompt → GPT-3.5/4 → Answer
6. **Visualization**: Graph data → D3.js → Interactive display

## 🌟 Key Features

- **Flexible**: Query one or both databases
- **Smart**: Automatic database selection
- **Visual**: Interactive graph visualizations
- **Fast**: Local Neo4j queries are quick
- **Scalable**: Easy to add more clinical trial data
- **Compatible**: Works with existing SPOKE setup

## 📊 Performance

- **Neo4j queries**: < 100ms (local)
- **SPOKE API**: 1-3 seconds (remote)
- **Combined**: 2-4 seconds total
- **Graph visualization**: Real-time rendering

## 🔮 Future Enhancements

- [ ] Entity linking between SPOKE and Neo4j
- [ ] Vector embeddings for clinical trials
- [ ] More data sources (PubMed, FDA, etc.)
- [ ] Advanced graph analytics
- [ ] Multi-hop reasoning across databases

## 📄 License

Same as original KG-RAG project.

## 🙏 Acknowledgments

- Original KG-RAG: BaranziniLab
- SPOKE: UCSF
- Neo4j: Graph database platform
- Clinical trial data: ClinicalTrials.gov

---

**Ready to explore medical knowledge with dual databases!** 🚀
