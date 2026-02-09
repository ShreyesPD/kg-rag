# Deploying KG-RAG Medical Chatbot to Render

This guide explains how to deploy the KG-RAG Medical Chatbot to Render.

## Prerequisites

1. **Render Account**: Sign up at [render.com](https://render.com)
2. **OpenAI API Key**: Get an API key from [OpenAI](https://platform.openai.com/api-keys)
3. **Git Repository**: Your code should be in a Git repository accessible to Render

## Deployment Steps

### 1. Prepare Your Repository

Ensure your repository contains:
- `render.yaml` (deployment configuration)
- `requirements.txt` (Python dependencies)
- `medical_chatbot_webapp/app.py` (Flask application)
- `config.yaml` (application configuration)
- `data/` directory with required data files
- `.env.example` (environment variable template)

### 2. Deploy to Render

#### Option A: Using Render's Dashboard

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New" → "Blueprint"
3. Connect your Git repository
4. Render will automatically detect the `render.yaml` file
5. Configure environment variables (see below)
6. Click "Create Blueprint"

#### Option B: Using Render CLI

```bash
# Install Render CLI
npm install -g @render/cli

# Deploy
render blueprint launch
```

### 3. Environment Variables

Set the following environment variables in your Render service:

| Variable | Value | Required |
|----------|--------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | Yes |
| `FLASK_ENV` | `production` | No (defaults to production) |

### 4. Persistent Storage

The deployment includes a 10GB persistent disk mounted at `/opt/render/project/src/data` for storing the vector database. This ensures the vector database persists across deployments.

### 5. Build Process

The build process will:
1. Install Python dependencies from `requirements.txt`
2. Run `python setup_vectordb.py` to create the vector database (this may take several minutes)

### 6. Health Check

Once deployed, you can check the health of your service at:
```
https://your-service-name.onrender.com/api/health
```

## Troubleshooting

### Common Issues

1. **Build Timeout**: The vector database creation might take time. If the build times out, consider:
   - Pre-building the vector database locally and committing it to your repository
   - Increasing Render's build timeout (contact Render support)

2. **Memory Issues**: The application requires significant memory. Consider upgrading to a higher plan.

3. **API Key Issues**: Ensure your OpenAI API key has sufficient credits and permissions.

### Logs

Check Render service logs for debugging information:
- Go to your service dashboard
- Click on "Logs" tab

## Post-Deployment

1. **Update DNS**: If using a custom domain, configure it in Render
2. **SSL Certificate**: Render provides automatic SSL certificates
3. **Monitoring**: Set up monitoring and alerts as needed
4. **Scaling**: Adjust instance type based on usage

## Cost Considerations

- **Free Tier**: Suitable for testing (750 hours/month)
- **Paid Plans**: Required for production use
- **Persistent Disk**: $5/month for 10GB storage
- **OpenAI API**: Costs depend on usage

## Security Notes

- Never commit API keys to your repository
- Use environment variables for sensitive configuration
- Keep dependencies updated for security patches
