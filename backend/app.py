# app.py
from fastapi import FastAPI, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.database import get_db, Truck, Warehouse

app = FastAPI(title="J.B. Hunt Chaos Reroute Dispatch API")

# --- API ROUTES ---
@app.get("/")
async def root():
    return {"status": "online", "system": "J.B. Hunt Dispatch Automation Backend"}

@app.post("/api/v1/dispatch/triage")
async def triage_dispatch(request: Request, db: AsyncSession = Depends(get_db)):
    # 1. Catch the dynamic payload from Vapi
    payload = await request.json()
    print(f"\n[RAW VAPI PAYLOAD] {payload}\n")

    # 2. Extract variables securely from Vapi's webhook schema
    message = payload.get("message", {})
    tool_calls = message.get("toolWithToolCallList", [])
    
    # Default empty variables
    truck_id, location, crisis_type, tool_call_id = None, None, None, None

    if tool_calls:
        try:
            call_data = tool_calls[0].get("toolCall", {})
            arguments = call_data.get("function", {}).get("arguments", {})
            truck_id = arguments.get("truck_id")
            location = arguments.get("location")
            crisis_type = arguments.get("crisis_type")
            tool_call_id = call_data.get("id")
        except Exception as e:
            print(f"[PARSE ERROR] {e}")
    else:
        # Fallback for flat JSON just in case Vapi shifts formats again
        truck_id = payload.get("truck_id")
        location = payload.get("location")
        crisis_type = payload.get("crisis_type")
        tool_call_id = payload.get("toolCallId")

    print(f"[EXTRACTED] Truck ID: {truck_id} | Location: {location} | Crisis: {crisis_type}")

    # 3. Process the backend logic using SQLAlchemy
    result = await db.execute(select(Truck).where(Truck.truck_id == str(truck_id)))
    truck = result.scalar_one_or_none()

    if not truck:
        error_msg = f"Truck ID {truck_id} is not recognized. Please ask the driver to clarify."
        print(f"[ERROR] {error_msg}")
        result_payload = {"filled": False, "message": error_msg}
        return {"results": [{"toolCallId": tool_call_id, "result": result_payload}]} if tool_call_id else result_payload
        
    result = await db.execute(select(Warehouse).where(Warehouse.location_code == str(location)))
    reroute_plan = result.scalar_one_or_none()
    
    if not reroute_plan:
        forward_msg = f"I see your manifest, {truck.driver_name}. I don't have an automated reroute configuration ready for {location}. I am escalating your line to a live regional supervisor immediately."
        print(f"[FORWARD] {forward_msg}")
        result_payload = {"filled": True, "message": forward_msg}
        return {"results": [{"toolCallId": tool_call_id, "result": result_payload}]} if tool_call_id else result_payload
        
    # Update truck status
    truck.status = f"Rerouted to {reroute_plan.hub_name}"
    await db.commit()
    print(f"[SUCCESS] {truck.driver_name} reassigned to {reroute_plan.hub_name}.")
    
    # 4. Construct final deterministic response
    success_msg = f"Manifest verified, {truck.driver_name}. Since you are hauling {truck.cargo}, I have logged your {crisis_type} status. Please divert immediately to the {reroute_plan.hub_name}, {reroute_plan.dock_number}. Your updated arrival window adds {reroute_plan.eta_adjustment} to your original timeline."
    
    result_payload = {
        "filled": True,
        "message": success_msg,
        "driver_name": truck.driver_name,
        "cargo": truck.cargo,
        "alternative_hub": reroute_plan.hub_name,
        "dock_number": reroute_plan.dock_number
    }

    # Vapi strict requirement: map the result to the specific toolCallId it sent
    if tool_call_id:
        return {"results": [{"toolCallId": tool_call_id, "result": result_payload}]}
    
    return result_payload
