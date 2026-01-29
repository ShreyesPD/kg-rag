# KG-RAG Medical Chatbot - Startup Guide

## 🚀 Quick Start Commands

### Option 1: Run the Web Application (Recommended)

```powershell
# Navigate to project directory
cd c:\Users\ShreyesPrabhuDesai\PersProjects\KG_RAG

# Activate virtual environment
.\kg_rag_env\Scripts\Activate.ps1

# Start the Flask web server
python medical_chatbot_webapp\app.py
```

Then open your browser and go to: **http://localhost:5000**

---

### Option 2: Run Terminal Interactive Mode

```powershell
# Navigate to project directory
cd c:\Users\ShreyesPrabhuDesai\PersProjects\KG_RAG

# Activate virtual environment
.\kg_rag_env\Scripts\Activate.ps1

# Run interactive terminal mode with GPT-3.5-turbo
python -m kg_rag.rag_based_generation.GPT.text_generation -i True -g gpt-3.5-turbo

# Or with GPT-4
python -m kg_rag.rag_based_generation.GPT.text_generation -i True -g gpt-4
```

---

## 📋 Complete Setup (First Time Only)

If you're setting up the project for the first time or on a new machine:

### 1. Create Virtual Environment
```powershell
cd c:\Users\ShreyesPrabhuDesai\PersProjects\KG_RAG
python -m venv kg_rag_env
```

### 2. Activate Virtual Environment
```powershell
.\kg_rag_env\Scripts\Activate.ps1
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
pip install flask flask-cors
```

### 4. Configure API Key
Edit `c:\Users\ShreyesPrabhuDesai\.gpt_config.env` and add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 5. Create Vector Database (One-time setup)
```powershell
python setup_vectordb.py
```

### 6. Start the Application
```powershell
# Web application
python medical_chatbot_webapp\app.py

# OR Terminal interactive mode
python -m kg_rag.rag_based_generation.GPT.text_generation -i True -g gpt-3.5-turbo
```

---

## 🎯 Available Modes

### Web Application (Interactive UI)
- **Command**: `python medical_chatbot_webapp\app.py`
- **Access**: http://localhost:5000
- **Features**: 
  - Medical-themed Skeuomorphic design
  - Real-time step-by-step processing visualization
  - Shows all 5 KG-RAG pipeline steps as they happen
  - Beautiful, responsive interface

### Terminal Interactive Mode
- **Command**: `python -m kg_rag.rag_based_generation.GPT.text_generation -i True -g gpt-3.5-turbo`
- **Features**:
  - Step-by-step terminal output
  - Press Enter to proceed through each step
  - Shows entity extraction, matching, context retrieval, pruning, and GPT response

### Terminal Standard Mode
- **Command**: `python -m kg_rag.rag_based_generation.GPT.text_generation -g gpt-3.5-turbo`
- **Features**:
  - Direct question and answer
  - No step-by-step visualization
  - Faster response time

### Terminal with Evidence
- **Command**: `python -m kg_rag.rag_based_generation.GPT.text_generation -e True -g gpt-3.5-turbo`
- **Features**:
  - Shows detailed evidence from knowledge graph
  - Includes provenance information
  - More detailed context

---

## 🛠️ Troubleshooting

### If the web server doesn't start:
```powershell
# Kill any existing Python processes
taskkill /F /IM python.exe

# Restart the server
python medical_chatbot_webapp\app.py
```

### If you get "Module not found" errors:
```powershell
# Make sure virtual environment is activated
.\kg_rag_env\Scripts\Activate.ps1

# Reinstall missing packages
pip install flask flask-cors
```

### If you get API key errors:
- Check that `.gpt_config.env` has your correct OpenAI API key
- Make sure the key starts with `sk-`
- Verify the file path in `config.yaml` is correct

### If vector database is missing:
```powershell
python setup_vectordb.py
```

---

## 📁 Project Structure

```
KG_RAG/
├── kg_rag_env/                      # Virtual environment
├── medical_chatbot_webapp/          # Web application
│   ├── app.py                       # Flask backend
│   ├── templates/
│   │   └── index.html              # Frontend UI
│   └── README.md                    # Web app documentation
├── kg_rag/                          # Core KG-RAG modules
│   ├── utility.py                   # Main utilities
│   ├── config_loader.py             # Configuration loader
│   └── rag_based_generation/        # Text generation modules
├── data/                            # Data files and vector DB
├── config.yaml                      # Main configuration
├── system_prompts.yaml              # System prompts for GPT
└── .gpt_config.env                  # API credentials (in home dir)
```

---

## 🌐 Access URLs

When the Flask server is running:
- **Local**: http://localhost:5000
- **Network**: http://192.168.20.20:5000 (accessible from other devices on your network)

---

## 💡 Example Questions

Try these biomedical questions:
- "What are the symptoms of Bardet-Biedl syndrome?"
- "What drugs are used to treat multiple sclerosis?"
- "What genes are associated with Alzheimer's disease?"
- "What is the relationship between diabetes and obesity?"
- "What are the side effects of Metformin?"

---

## 🔧 Configuration Files

### config.yaml
Main configuration file with:
- Vector database paths
- LLM settings
- SPOKE API configuration
- File paths for data

### .gpt_config.env
OpenAI API credentials:
```
OPENAI_API_KEY=your-api-key-here
```

### system_prompts.yaml
System prompts for different tasks:
- Disease entity extraction
- KG-RAG based text generation
- Validation prompts

---

## 📊 System Requirements

- **Python**: 3.12 (or compatible version)
- **RAM**: 4GB minimum (8GB recommended)
- **Disk Space**: 2GB for models and data
- **Internet**: Required for OpenAI API and SPOKE knowledge graph access

---

## 🎨 Web Application Features

The medical chatbot web application includes:
- **Skeuomorphic Design**: Realistic medical device aesthetic
- **Real-time Streaming**: See each step process live
- **Interactive Pipeline**: Visual representation of all 5 KG-RAG steps
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Medical Theme**: Blues, greens, and whites inspired by medical equipment
- **Smooth Animations**: Professional transitions and effects

---

## 📝 Notes

- The web application and terminal modes use the same KG-RAG pipeline
- All processing happens server-side for security
- The vector database is created once and reused
- Models are cached locally after first download
- SPOKE API calls are made in real-time for fresh data

---

## 🆘 Support

If you encounter issues:
1. Check that virtual environment is activated
2. Verify API key is configured correctly
3. Ensure vector database exists
4. Check that all dependencies are installed
5. Review error messages in terminal

---

## ✅ Quick Checklist

Before running the application:
- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] OpenAI API key configured
- [ ] Vector database created
- [ ] Config.yaml paths are correct

---

**Ready to use!** Start the web application and begin exploring biomedical knowledge with AI-powered assistance! 🎉
