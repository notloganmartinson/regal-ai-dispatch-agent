# J.B. Hunt Chaos Reroute Dispatch API

This is the backend service for managing fleet telemetry and automated emergency rerouting of freight shipments.

## Overview

The API processes triage requests for trucks experiencing emergency situations (e.g., cargo temperature issues, mechanical failures). It validates the truck manifest, determines an alternative warehouse hub based on the reported location, and provides a reroute plan to the driver.

## Project Structure

- `backend/app.py`: The FastAPI application entry point and endpoint handler for Vapi-based dispatch triage.
- `backend/mock_db.py`: The in-memory data store containing truck telemetry and warehouse reroute configurations.
- `backend/requirements.txt`: Python dependencies.

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

**Response:**

Returns a structured reroute plan if the truck and location are recognized.

## Setup

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. Run the application:
   ```bash
   uvicorn backend.app:app --reload
   ```
