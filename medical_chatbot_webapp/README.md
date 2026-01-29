# Medical KG-RAG Chatbot Web Application

A medical-themed web chatbot interface with Skeuomorphic design that integrates the KG-RAG GPT interactive flow.

## Features

- **Medical-Themed Skeuomorphic UI**: Beautiful, realistic design inspired by medical devices and charts
- **Interactive KG-RAG Pipeline**: Shows all 5 steps of the knowledge graph retrieval process
- **Real-time Processing**: Step-by-step visualization of:
  1. Disease Entity Extraction using GPT-3.5-Turbo
  2. Entity Matching to SPOKE Knowledge Graph
  3. Context Extraction from Biomedical Knowledge Graph
  4. Context Pruning using Semantic Similarity
  5. GPT Response Generation with Knowledge Graph Context
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Example Questions**: Pre-loaded biomedical questions to get started quickly

## Architecture

### Backend (Flask)
- **app.py**: Flask server that integrates KG-RAG pipeline
- Exposes REST API endpoints for chat and health checks
- Processes queries through the complete KG-RAG interactive flow

### Frontend (HTML/CSS/JavaScript)
- **templates/index.html**: Single-page application with medical Skeuomorphic design
- Real-time chat interface with step-by-step processing visualization
- Smooth animations and transitions

## How to Run

1. Make sure you're in the KG_RAG project directory with the virtual environment activated:
```powershell
cd c:\Users\ShreyesPrabhuDesai\PersProjects\KG_RAG
.\kg_rag_env\Scripts\Activate.ps1
```

2. Start the Flask server:
```powershell
python medical_chatbot_webapp\app.py
```

3. Open your web browser and navigate to:
```
http://localhost:5000
```

4. Start asking biomedical questions!

## API Endpoints

### POST /api/chat
Send a question and receive the complete KG-RAG pipeline response.

**Request:**
```json
{
  "question": "What are the symptoms of Bardet-Biedl syndrome?"
}
```

**Response:**
```json
{
  "success": true,
  "question": "What are the symptoms of Bardet-Biedl syndrome?",
  "steps": [
    {
      "step": 1,
      "name": "Disease Entity Extraction",
      "status": "completed",
      "result": "Extracted entities: Bardet-Biedl syndrome"
    },
    ...
  ],
  "answer": "The generated answer with knowledge graph context"
}
```

### GET /api/health
Check if the server and models are ready.

**Response:**
```json
{
  "status": "healthy",
  "models_loaded": true,
  "vectorstore_ready": true
}
```

## Design Philosophy

The UI follows **Skeuomorphic design principles** with a medical theme:

- **Realistic Textures**: Paper-like background, embossed buttons, and shadows
- **Medical Color Palette**: Blues, greens, and whites inspired by medical equipment
- **Depth and Dimension**: Gradients, shadows, and borders create a 3D effect
- **Familiar Metaphors**: Medical icons, status indicators, and card-like message bubbles

## Technologies Used

- **Backend**: Flask, Flask-CORS
- **AI/ML**: OpenAI GPT-3.5-Turbo, LangChain, Sentence Transformers
- **Knowledge Graph**: SPOKE API
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Fonts**: Google Fonts (Roboto, Roboto Slab)

## Example Questions

- "What are the symptoms of Bardet-Biedl syndrome?"
- "What drugs are used to treat multiple sclerosis?"
- "What genes are associated with Alzheimer's disease?"
- "What is the relationship between diabetes and obesity?"

## Notes

- The application uses the same KG-RAG configuration from `config.yaml`
- OpenAI API key must be configured in `.gpt_config.env`
- The vector database must be created before running (already done in setup)
- All processing happens server-side for security and performance
