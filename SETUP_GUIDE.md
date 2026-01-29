# KG-RAG Setup Guide for Windows

## ✅ Setup Completed!

The KG-RAG project has been successfully set up on your Windows machine. Here's what was done:

### 1. Virtual Environment
- Created Python virtual environment at: `kg_rag_env/`
- Installed all required dependencies (with Windows-compatible adjustments)

### 2. Configuration Files Updated
- **config.yaml**: Updated all file paths to use Windows-compatible absolute paths
- **GPT API Type**: Set to 'openai' (instead of Azure)
- **Vector Database**: Created successfully at `data/vectorDB/disease_nodes_db`

### 3. API Configuration
- Created `.gpt_config.env` at: `c:/Users/ShreyesPrabhuDesai/.gpt_config.env`
- **⚠️ IMPORTANT**: You need to add your OpenAI API key to this file!

## 🔑 Next Step: Add Your OpenAI API Key

Edit the file: `c:/Users/ShreyesPrabhuDesai/.gpt_config.env`

Replace `your-api-key-here` with your actual OpenAI API key:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

Get your API key from: https://platform.openai.com/api-keys

## 🚀 How to Run KG-RAG

### Activate the Virtual Environment
```powershell
.\kg_rag_env\Scripts\Activate.ps1
```

### Run KG-RAG with GPT-4
```powershell
python -m kg_rag.rag_based_generation.GPT.text_generation -g gpt-4
```

### Run KG-RAG with GPT-3.5-turbo
```powershell
python -m kg_rag.rag_based_generation.GPT.text_generation -g gpt-3.5-turbo
```

### Run in Interactive Mode (Step-by-step)
```powershell
python -m kg_rag.rag_based_generation.GPT.text_generation -i True -g gpt-4
```

### Show Evidence from Knowledge Graph
```powershell
python -m kg_rag.rag_based_generation.GPT.text_generation -e True -g gpt-4
```

## 📝 Example Questions to Try

Once you have your API key configured, you can ask biomedical questions like:
- "What are the symptoms of Bardet-Biedl Syndrome?"
- "What drugs are approved for treating multiple sclerosis?"
- "What genes are associated with Alzheimer's disease?"

## 📁 Project Structure

```
KG_RAG/
├── kg_rag_env/              # Virtual environment
├── data/                     # Data files and vector database
│   ├── vectorDB/            # Disease vector database (✅ created)
│   ├── benchmark_data/      # Test questions
│   └── *.csv, *.pickle      # Disease and context data
├── kg_rag/                  # Main source code
├── config.yaml              # Configuration (✅ updated)
└── .gpt_config.env          # API credentials (⚠️ needs your key)
```

## 🔧 Troubleshooting

### If you get "No module named 'X'" errors:
```powershell
.\kg_rag_env\Scripts\python.exe -m pip install <missing-package>
```

### If you get API key errors:
- Make sure you've added your OpenAI API key to `.gpt_config.env`
- Ensure the key starts with `sk-`
- Check that the file is saved properly

### If you get path errors:
- All paths in `config.yaml` have been set to absolute Windows paths
- If you move the project, update the paths in `config.yaml`

## 📚 Additional Resources

- Original README: `README.md`
- System Prompts: `system_prompts.yaml`
- Example Notebooks: `notebooks/`
- BiomixQA Dataset: https://huggingface.co/datasets/kg-rag/BiomixQA

## ⚙️ What Was Modified

The following adjustments were made for Windows compatibility:
1. Commented out platform-specific packages (appnope, triton, uvloop)
2. Updated langchain imports to use `langchain_community`
3. Fixed HOME environment variable handling for Windows
4. Set all paths to Windows-compatible format
5. Changed GPT API type from Azure to OpenAI

## 🎯 Ready to Use!

Once you add your OpenAI API key, you're ready to run KG-RAG and explore biomedical knowledge graph-enhanced prompting!
