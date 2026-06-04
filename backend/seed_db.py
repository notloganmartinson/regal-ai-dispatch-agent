import asyncio
from backend.database import engine, Base, Truck, Warehouse, AsyncSessionLocal

async def seed_data():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        truck1 = Truck(
            truck_id="402",
            driver_name="Marcus Vance",
            cargo="Premium Refrigerated Salmon",
            status="In Transit",
            driver_phone_number="+1-555-010-9999"  # PLACEHOLDER
        )
        truck2 = Truck(
            truck_id="502",
            driver_name="Sarah Jenkins",
            cargo="Fresh Produce / Avocados",
            status="In Transit",
            driver_phone_number="+1-555-010-9999"  # PLACEHOLDER
        )
        
        warehouse1 = Warehouse(
            location_code="Route 80 East",
            hub_name="Aurora Logistics Center",
            dock_number="Dock 4",
            eta_adjustment="22 minutes",
            real_address="1001 Enterprise St, Aurora, IL 60505",
            maps_url="https://www.google.com/maps/search/?api=1&query=1001+Enterprise+St+Aurora+IL+60505"
        )
        warehouse2 = Warehouse(
            location_code="I-55 North",
            hub_name="Joliet Terminal Hub",
            dock_number="Dock B12",
            eta_adjustment="15 minutes",
            real_address="2000 W Laraway Rd, Joliet, IL 60433",
            maps_url="https://www.google.com/maps/search/?api=1&query=2000+W+Laraway+Rd+Joliet+IL+60433"
        )
        
        session.add_all([truck1, truck2, warehouse1, warehouse2])
        await session.commit()
        print("Database seeded successfully.")

if __name__ == "__main__":
    asyncio.run(seed_data())
