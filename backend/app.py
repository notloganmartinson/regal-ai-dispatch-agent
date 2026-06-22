import os
import logging
from fastapi import FastAPI, Request, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.database import get_db, Truck, Warehouse, FAQKnowledgeBase
from twilio.rest import Client
from dotenv import load_dotenv
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- TWILIO SETUP ---
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN) if TWILIO_ACCOUNT_SID else None

class FAQQuery(BaseModel):
    query: str

def send_dispatch_sms(driver_phone: str, truck_id: str, hub_name: str, real_address: str, maps_url: str):
    """Fires a synchronous SMS through Twilio. We run this in a FastAPI Background Task."""
    if not twilio_client:
        print("[WARNING] Twilio client not configured. Skipping SMS.")
        return
        
    message_body = f"URGENT DISPATCH: Truck {truck_id} rerouted to {hub_name}. Address: {real_address}. Route: {maps_url}"
    try:
        message = twilio_client.messages.create(
            body=message_body,
            from_=TWILIO_PHONE_NUMBER,
            to=driver_phone
        )
        print(f"[SMS SUCCESS] Sent to {driver_phone}. Message SID: {message.sid}")
    except Exception as e:
        print(f"[SMS ERROR] Failed to send SMS: {e}")


app = FastAPI(title="J.B. Hunt Chaos Reroute Dispatch API")

# --- API ROUTES ---
@app.get("/")
async def root():
    return {"status": "online", "system": "J.B. Hunt Dispatch Automation Backend"}

@app.post("/api/v1/dispatch/search_faqs")
async def search_dispatch_faqs(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.json()
    logger.info(f"DEBUG: Incoming Vapi Payload: {payload}")
    
    # 1. Inspect structure
    if "message" in payload:
        logger.info(f"DEBUG: Message structure: {payload['message'].keys()}")
        if "toolCallList" in payload["message"]:
             logger.info(f"DEBUG: toolCallList found. Count: {len(payload['message']['toolCallList'])}")
    
    # Handle Vapi's official tool-call format
    if "message" in payload and (payload["message"].get("type") == "tool-calls" or "toolCallList" in payload["message"]):
        results = []
        # Support both 'toolCallList' or 'toolWithToolCallList' based on previous logs/experience
        tool_calls = payload["message"].get("toolCallList") or payload["message"].get("toolWithToolCallList") or []
        
        for tool_call in tool_calls:
            # Normalize to handle variations in Vapi payloads
            tc_data = tool_call.get("toolCall") if "toolCall" in tool_call else tool_call
            
            tool_call_id = tc_data.get("id")
            function_data = tc_data.get("function", {})
            arguments = function_data.get("arguments", {})
            
            logger.info(f"DEBUG: Processing tool call: {tool_call_id}, args: {arguments}")
            
            # Arguments might be a string (JSON) or a dict depending on Vapi configuration.
            import json
            if isinstance(arguments, str):
                try:
                    arguments = json.loads(arguments)
                except json.JSONDecodeError:
                    pass
            
            driver_query = arguments.get("query")
            
            # Vector Search
            if driver_query:
                embedding = model.encode(driver_query).tolist()
                stmt = select(FAQKnowledgeBase).order_by(FAQKnowledgeBase.embedding.cosine_distance(embedding)).limit(1)
                db_res = await db.execute(stmt)
                faq = db_res.scalar_one_or_none()
                raw_answer = faq.answer if faq else "I am sorry, I could not find a relevant answer in the FAQ."
            else:
                raw_answer = "I could not understand your query."
                
            safe_answer = raw_answer.replace("\n", " ").strip()
            
            results.append({
                "toolCallId": tool_call_id,
                "result": {"answer": safe_answer}
            })
            
        vapi_response = {"results": results}
        logger.info(f"Outgoing Vapi Response: {vapi_response}")
        return vapi_response

    # 2. Fallback: Local testing
    driver_query = payload.get("query")
    if driver_query:
        embedding = model.encode(driver_query).tolist() 
        stmt = select(FAQKnowledgeBase).order_by(FAQKnowledgeBase.embedding.cosine_distance(embedding)).limit(1)
        db_res = await db.execute(stmt)
        faq = db_res.scalar_one_or_none()
        raw_answer = faq.answer if faq else "I am sorry, I could not find a relevant answer in the FAQ."
        return {"answer": raw_answer}

    return {"results": []}

@app.post("/api/v1/dispatch/triage")
async def triage_dispatch(request: Request, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    # 1. Catch the dynamic payload from Vapi
    payload = await request.json()
    print(f"\n[RAW VAPI PAYLOAD] {payload}\n")

    # 2. Extract variables securely from Vapi's webhook schema
    message = payload.get("message", {})
    tool_calls = message.get("toolWithToolCallList", [])
    
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
    
    # --- FIRE THE OMNICHANNEL SMS ---
    background_tasks.add_task(
        send_dispatch_sms,
        driver_phone=truck.driver_phone_number,
        truck_id=truck.truck_id,
        hub_name=reroute_plan.hub_name,
        real_address=reroute_plan.real_address,
        maps_url=reroute_plan.maps_url
    )
    
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

    if tool_call_id:
        return {"results": [{"toolCallId": tool_call_id, "result": result_payload}]}
    
    return result_payload
