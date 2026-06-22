# J.B. Hunt Demo Script: Crisis Reroute & FAQ

Use these questions to demonstrate the AI's ability to handle real-time telemetry (Truck/Warehouse data) and RAG-based knowledge retrieval (FAQ Knowledge Base).

---

## Phase 1: Identity & Telemetry (The "Crisis" Call)
*These questions demonstrate that the AI can look up specific driver data and cargo status from the PostgreSQL database.*

1. **"I'm Marcus Vance in truck 402. There's a major accident blocking the road and I'm hauling refrigerated salmon. What's the plan?"**
   - **What to look for:** The AI should confirm it knows he is carrying **Premium Refrigerated Salmon** and suggest a reroute to the **Aurora Logistics Center** (Dock 4).

2. **"This is Sarah Jenkins (Truck 502). I'm carrying a load of avocados and the road ahead is closed. Where is the nearest terminal?"**
   - **What to look for:** The AI should identify her and suggest the **Joliet Terminal Hub** on I-55 North (Dock B12).

---

## Phase 2: Compensation & Logistics (The RAG Test)
*These questions test the semantic vector search (pgvector) against the seeded FAQ knowledge base.*

3. **"Am I going to be compensated for the time I'm stuck here in this traffic jam?"**
   - **Expected Info:** Mention of **Mechanical Breakdown/Rail Delay Pay** ($20.00 - $23.00 per hour).

4. **"If the reroute warehouse takes forever to unload me, do I get extra pay for the wait?"**
   - **Expected Info:** Mention of **Detention Pay** ($20.00 - $33.00 per hour) kicking in after the first hour.

5. **"Where am I allowed to fuel up on this new route?"**
   - **Expected Info:** Must name the preferred network: **Pilot Flying J, Love's Travel Stops, and TA/Petro**.

---

## Phase 3: Compliance & Safety (The "Policy" Test)
*These questions show the AI can handle high-stakes regulatory and safety advice.*

6. **"I'm worried about my ELD hours. This delay is going to put me over my limit. Can I keep driving to the new stop?"**
   - **Expected Info:** Guidance on the **"Adverse Driving Conditions"** exception and the requirement to pull over if hours are fully exhausted.

7. **"I just had a minor fender-bender while trying to navigate the detour. What do I do?"**
   - **Expected Info:** The 4-step protocol: **Safety First**, **Report Instantly (800-723-0422)**, **Don't Admit Fault**, and **Document with Photos**.

8. **"My DRIVE app is frozen and I can't see my new map. Is there a tech support number?"**
   - **Expected Info:** Provide the Technical Service Desk number: **800-723-0421**.
