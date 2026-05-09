# Sentiment Analyzer (Mistral)

A simple AI application that uses the Mistral model via Ollama to classify text
sentiment as Positive, Negative, or Neutral.

## Features
- FastAPI backend
- Streamlit frontend
- Local inference using Ollama-hosted Mistral

## Run Locally
1. Clone the repository
2. Pull the model:
   ollama pull mistral
3. Start backend:
   uvicorn backend.main:app --reload
4. Start frontend:
   streamlit run frontend/app.py