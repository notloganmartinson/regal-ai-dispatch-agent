# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="J.B. Hunt Chaos Reroute Dispatch API")

# Define what we expect Vapi to send us
class TriageRequest(BaseModel):
    truck_id: str
    location: str
    crisis_type: str

@app.post("/api/v1/dispatch/triage")
async def triage_dispatch(payload: TriageRequest):
    truck_id = payload.truck_id
    location = payload.location
    crisis_type = payload.crisis_type
    
    # 1. Look up the Truck/Driver Profile
    truck = TRUCK_DATABASE.get(truck_id)
    if not truck:
        # If the driver mistyped/misspoke the ID, we tell the LLM securely
        return {"filled": False, "message": f"Truck ID {truck_id} not found in active manifest."}
        
    # 2. Look up the Reroute Solution based on location
    reroute_plan = WAREHOUSE_DATABASE.get(location)
    if not reroute_plan:
        return {
            "filled": True,
            "driver_name": truck["driver_name"],
            "message": "Alternative hubs are full for that specific corridor. Escalating call to regional human supervisor."
        }
        
    # 3. Simulate updating our local database status
    TRUCK_DATABASE[truck_id]["status"] = f"Rerouted to {reroute_plan['alternative_hub']}"
    
    # 4. Return the deterministic structured data back to Vapi
    return {
        "filled": True,
        "driver_name": truck["driver_name"],
        "cargo": truck["cargo"],
        "alternative_hub": reroute_plan["alternative_hub"],
        "dock_number": reroute_plan["dock_number"],
        "eta": reroute_plan["eta_adjustment"],
        "message": f"Divert to the {reroute_plan['alternative_hub']}, {reroute_plan['dock_number']}. ETA is {reroute_plan['eta_adjustment']}."
    }
