# J.B. Hunt Chaos Reroute Dispatch API

This is the backend service for managing fleet telemetry and automated emergency rerouting of freight shipments, utilizing a persistent PostgreSQL database.

## Overview

The API processes triage requests for trucks experiencing emergency situations (e.g., cargo temperature issues, mechanical failures). It validates the truck manifest against a PostgreSQL database, determines an alternative warehouse hub based on the reported location, and provides a reroute plan to the driver.

## Project Structure

- `backend/app.py`: FastAPI application, endpoint handler, and business logic.
- `backend/database.py`: SQLAlchemy 2.0 ORM models and asynchronous database session management.
- `backend/seed_db.py`: Initialization script to create schema and populate initial test data.
- `backend/requirements.txt`: Python dependencies.
- `.env`: Environment variables for database configuration (not committed to version control).

## API Endpoints

### POST /api/v1/dispatch/triage

Processes a dispatch triage request.

**Request Payload (Example):**

```json
{
  "message": {
    "toolWithToolCallList": [
      {
        "toolCall": {
          "id": "call_123",
          "function": {
            "arguments": {
              "truck_id": "402",
              "location": "Route 80 East",
              "crisis_type": "Engine Overheat"
            }
          }
        }
      }
    ]
  }
}
```

## Setup

1. **Environment Setup:**
   Ensure PostgreSQL is running. Create a `.env` file in the project root:
   ```env
   DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dispatch_db
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
