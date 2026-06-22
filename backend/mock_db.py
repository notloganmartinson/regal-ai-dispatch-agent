# mock_db.py

# Fleet Telemetry Database
TRUCK_DATABASE = {
    "402": {
        "driver_name": "Marcus Vance",
        "cargo": "Premium Refrigerated Salmon",
        "optimal_temp": "-18°C",
        "destination": "Chicago Distribution Center",
        "status": "In Transit"
    },
    "502": {
        "driver_name": "Sarah Jenkins",
        "cargo": "Fresh Produce / Avocados",
        "optimal_temp": "4°C",
        "destination": "Milwaukee Logistics Hub",
        "status": "In Transit"
    }
}

# ERP Warehouse Roster (Available Loading Docks)
WAREHOUSE_DATABASE = {
    "Route 80 East": {
        "alternative_hub": "Aurora Facility",
        "dock_number": "Dock 4",
        "eta_adjustment": "22 minutes"
    },
    "I-55 North": {
        "alternative_hub": "Joliet Terminal",
        "dock_number": "Dock B12",
        "eta_adjustment": "15 minutes"
    }
}
