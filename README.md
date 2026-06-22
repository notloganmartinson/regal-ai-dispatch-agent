# J.B. Hunt Chaos Reroute Dispatch API

This is the backend service for managing fleet telemetry, automated emergency rerouting, and intelligent FAQ retrieval using vector search.

## Overview

The API processes triage requests for trucks experiencing emergency situations and provides RAG-based FAQ answers using PostgreSQL (pgvector) and Google Gemini embeddings.

## Project Structure

- `backend/app.py`: FastAPI application, endpoints (triage, search_faqs), and business logic.
- `backend/database.py`: SQLAlchemy 2.0 ORM models (Truck, Warehouse, FAQKnowledgeBase) and asynchronous database session management.
- `backend/seed_db.py`: Initialization script to create schema and populate truck/warehouse data.
- `backend/seed_faq.py`: Script to generate embeddings for FAQs using Gemini and populate the vector database.
- `backend/requirements.txt`: Python dependencies.
- `.env`: Environment variables (DATABASE_URL, GEMINI_API_KEY, TWILIO credentials).

## API Endpoints

### POST /api/v1/dispatch/triage
Processes a dispatch triage request from Vapi.

### POST /api/v1/dispatch/search_faqs
Performs a semantic vector search for FAQ answers based on a user query.

## Setup

1. **Environment Setup:**
   Ensure PostgreSQL (with pgvector extension) is running. Create a `.env` file:
   ```env
   DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dispatch_db
   GEMINI_API_KEY='your_gemini_key'
   TWILIO_ACCOUNT_SID='your_sid'
   TWILIO_AUTH_TOKEN='your_key'
   TWILIO_PHONE_NUMBER='+1...'
   ```

2. **Dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Database Initialization:**
   ```bash
   export PYTHONPATH=$PYTHONPATH:.
   # Create schema and seed basic data
   python3 backend/init_db.py
   python3 backend/seed_db.py
   # Generate embeddings and seed FAQs
   python3 backend/seed_faq.py
   ```

4. **Running the Application:**
   ```bash
   export PYTHONPATH=$PYTHONPATH:.
   uvicorn backend.app:app --reload
   ```

## Troubleshooting

- **SMS Failures:** Ensure your Twilio account has completed the **A2P 10DLC** registration.
- **Vector Search Failures:** Verify the `pgvector` extension is enabled in your database and that the `FAQKnowledgeBase` embedding dimension (3072) matches the model output.
