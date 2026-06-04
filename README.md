# J.B. Hunt Chaos Reroute Dispatch API

This is the backend service for managing fleet telemetry and automated emergency rerouting of freight shipments, utilizing a persistent PostgreSQL database.

## Overview

The API processes triage requests for trucks experiencing emergency situations (e.g., cargo temperature issues, mechanical failures). It validates the truck manifest against a PostgreSQL database, determines an alternative warehouse hub based on the reported location, and provides a reroute plan to the driver.

## Project Structure

- `backend/app.py`: FastAPI application, endpoint handler, and business logic.
- `backend/database.py`: SQLAlchemy 2.0 ORM models and asynchronous database session management.
- `backend/seed_db.py`: Initialization script to create schema and populate initial test data.
- `backend/requirements.txt`: Python dependencies.
- `.env`: Environment variables for database and Twilio configuration (not committed to version control).

## API Endpoints

### POST /api/v1/dispatch/triage

Processes a dispatch triage request.

## Setup

1. **Environment Setup:**
   Ensure PostgreSQL is running. Create a `.env` file in the project root:
   ```env
   DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dispatch_db
   TWILIO_ACCOUNT_SID='your_sid'
   TWILIO_SECRET_KEY='your_key'
   ```

2. **Dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Database Initialization:**
   ```bash
   export PYTHONPATH=$PYTHONPATH:.
   python3 backend/seed_db.py
   ```

4. **Running the Application:**
   ```bash
   export PYTHONPATH=$PYTHONPATH:.
   uvicorn backend.app:app --reload
   ```

## Troubleshooting

- **SMS Failures:** If you encounter issues sending SMS messages via Twilio, ensure your Twilio account has completed the **A2P 10DLC (Application-to-Person 10-Digit Long Code)** registration process. Twilio may block messages from unregistered numbers.
