# Neo4j Clinical Trials Integration - Setup Guide

This guide will help you set up and use the Neo4j clinical trials database alongside the existing SPOKE knowledge graph.

## Prerequisites

- ✅ Neo4j Community Edition installed (Desktop or CLI)
- ✅ Python environment with KG-RAG dependencies
- ✅ Clinical trial CSV data

## Step 1: Verify Neo4j Installation

Make sure Neo4j is running:

```bash
# Check if Neo4j is running
# For Neo4j Desktop: Start the database from the UI
# For Neo4j CLI: 
neo4j status
```

Default connection:
- **URI**: `bolt://localhost:7687`
- **Username**: `neo4j`
- **Password**: Set during first-time setup

## Step 2: Configure Environment Variables

Your `.env` file should already have Neo4j credentials:

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here
```

## Step 3: Verify Configuration

Check `config.yaml` has the Neo4j settings:

```yaml
# Neo4j Configuration
NEO4J_URI : 'bolt://localhost:7687'
NEO4J_USER : 'neo4j'
NEO4J_DATABASE : 'neo4j'

# Clinical Trials Data Configuration
CLINICAL_TRIALS_CSV_PATH : 'jazz_data/NCT06695845 (1).csv'
CLINICAL_TRIALS_VECTOR_DB_PATH : 'data/vectorDB/clinical_trials_db'

# Query Routing Configuration
ENABLE_NEO4J : True
DEFAULT_DATABASE_MODE : 'both'  # Options: 'spoke', 'neo4j', 'both'
```

## Step 4: Ingest Clinical Trial Data

Run the ingestion script to load your CSV data into Neo4j:

```bash
# From the KG_RAG root directory
python scripts/ingest_clinical_trials.py
```

**Options:**
- `--csv-path`: Specify a different CSV file
- `--clear`: Clear existing data before ingestion
- `--stats`: Show database statistics only

**Example with options:**
```bash
python scripts/ingest_clinical_trials.py --csv-path jazz_data/NCT06695845\ \(1\).csv --clear
```

**Expected output:**
```
Connecting to Neo4j...
Successfully connected to Neo4j at bolt://localhost:7687
Initializing graph schema...
Created constraint: ...
Building graph from CSV: jazz_data/NCT06695845 (1).csv
Loaded 1 clinical trials from ...
Building graph for trial NCT06695845
Successfully built graph for trial NCT06695845
Graph building complete!

Database statistics:
  ['ClinicalTrial']: 1 nodes
  ['Condition']: X nodes
  ['Intervention']: X nodes
  ['Sponsor']: X nodes
  ...
```

## Step 5: Verify Data Ingestion

Check the database statistics:

```bash
python scripts/ingest_clinical_trials.py --stats
```

Or use Neo4j Browser (http://localhost:7474):

```cypher
// Count all nodes by type
MATCH (n)
RETURN labels(n) AS label, count(*) AS count
ORDER BY count DESC

// View a sample clinical trial
MATCH (ct:ClinicalTrial)
RETURN ct
LIMIT 1

// View trial with relationships
MATCH (ct:ClinicalTrial)-[r]->(n)
RETURN ct, r, n
LIMIT 25
```

## Step 6: Test the Integration

### Option A: Command Line (Dual Database)

```bash
python -m kg_rag.rag_based_generation.GPT.text_generation_dual_db -g gpt-3.5-turbo -d both
```

**Database mode options:**
- `-d spoke`: SPOKE only
- `-d neo4j`: Neo4j only
- `-d both`: Both databases (default)

**Interactive mode:**
```bash
python -m kg_rag.rag_based_generation.GPT.text_generation_dual_db -g gpt-3.5-turbo -i True
```

### Option B: Web Interface

```bash
python medical_chatbot_webapp/app_dual_db.py
```

Then open: http://localhost:5000

The web interface allows you to:
- Select database source (SPOKE/Neo4j/Both)
- View step-by-step processing
- Visualize knowledge graph relationships

## Graph Schema

The Neo4j database uses the following schema:

### Node Types
- **ClinicalTrial**: Core trial information
- **Condition**: Diseases/conditions being studied
- **Intervention**: Drugs/treatments
- **Sponsor**: Organizations funding trials
- **Location**: Geographic trial sites
- **OutcomeMeasure**: Primary/secondary outcomes

### Relationship Types
- `(ClinicalTrial)-[:STUDIES]->(Condition)`
- `(ClinicalTrial)-[:USES_INTERVENTION]->(Intervention)`
- `(ClinicalTrial)-[:SPONSORED_BY]->(Sponsor)`
- `(ClinicalTrial)-[:CONDUCTED_AT]->(Location)`
- `(ClinicalTrial)-[:MEASURES]->(OutcomeMeasure)`
- `(Intervention)-[:TREATS]->(Condition)`

## Sample Questions

Try these questions to test the dual-database system:

**Neo4j-focused questions:**
1. "What is Zanidatamab used for?"
2. "Tell me about clinical trial NCT06695845"
3. "What trials are studying HER2-expressing tumors?"
4. "What are the primary outcomes for breast cancer trials?"

**SPOKE-focused questions:**
1. "What genes are associated with Alzheimer's disease?"
2. "How does metformin work?"
3. "What proteins interact with TP53?"

**Dual-database questions:**
1. "What clinical trials exist for HER2-positive breast cancer and what is known about HER2?"
2. "Tell me about Zanidatamab and its mechanism of action"

## Troubleshooting

### Connection Error: "Failed to connect to Neo4j"

**Solution:**
1. Verify Neo4j is running: `neo4j status`
2. Check credentials in `.env` file
3. Test connection in Neo4j Browser: http://localhost:7474

### Import Error: "No module named 'neo4j'"

**Solution:**
```bash
pip install neo4j
```

### Data Not Found

**Solution:**
1. Re-run ingestion: `python scripts/ingest_clinical_trials.py --clear`
2. Check CSV path in `config.yaml`

### Web App Shows "Neo4j: Disabled"

**Solution:**
1. Set `ENABLE_NEO4J: True` in `config.yaml`
2. Verify Neo4j connection
3. Restart the web app

## Adding More Clinical Trial Data

To add additional CSV files:

1. Place CSV in `jazz_data/` directory
2. Run ingestion (without `--clear` to preserve existing data):
   ```bash
   python scripts/ingest_clinical_trials.py --csv-path jazz_data/new_trials.csv
   ```

## Performance Tips

1. **Indexes**: Automatically created during ingestion
2. **Batch Size**: Modify in `graph_builder.py` if needed
3. **Context Volume**: Adjust `CONTEXT_VOLUME` in `config.yaml`

## Next Steps

- Explore the graph in Neo4j Browser
- Try different database modes
- Add more clinical trial data
- Customize the graph schema for your needs
