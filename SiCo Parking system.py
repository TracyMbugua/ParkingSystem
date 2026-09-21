import time
from datetime import datetime, timedelta
import random # Needed for payment simulation

# --- CONFIGURATION (The Rules) ---
class ParkingConfig:
    """ Holds all the system rules and numbers. """
    # Grace period: 30 minutes free
    FREE_TIME_GRACE_PERIOD = timedelta(minutes=30)

    # Pricing: {Max Time: Fee}
    PRICING_TIERS = {
        "Tier1": {"max_hours": 2, "fee": 50.00},
        "Tier2": {"max_hours": 4, "fee": 100.00},
        "Tier3": {"max_hours": 6, "fee": 300.00},
        "Tier4": {"max_hours": float('inf'), "fee": 500.00} # > 6 hours
    }

    TOTAL_SLOTS = 50

# ======================================================================
# 1. DATABASE SIMULATION (The Storage)
# ======================================================================

class ParkingDatabase:
    """ Simulates the database tables using simple Python tools. """
    def __init__(self):
        # Available spots counter
        self.slots_available = ParkingConfig.TOTAL_SLOTS 

        # Active sessions (using a dictionary for super fast lookups)
        self.active_sessions = {} 

        # History log (just a list for saved records)
        self.history_log = [] 

        print(" DB setup done.")

# ======================================================================
# 2. SYSTEM MANAGER (The Logic Brain)
# ======================================================================

class ParkingSystemManager:
    """ Manages all the modules: entry, exit, display, payments. """
    def __init__(self):
        self.db = ParkingDatabase()
        self.config = ParkingConfig()

    # --- Module 1: Slot Display ---
    def get_slot_status(self):
        """ Shows how many spots are free (for the driver display). """
        available = self.db.slots_available
        print(f"\n---  DISPLAY ---")
        print(f"Slots Available: {available} / {self.config.TOTAL_SLOTS}")
        print("------------------\n")
        return available

    # --- Module 2: Entry Logic ---
    def register_entry(self, vehicle_id: str) -> bool:
        """ Logs the car on arrival. Adds to slot count. """
        if self.db.slots_available <= 0:
            print(f" FULL: Lot is full.")
            return False

        if vehicle_id in self.db.active_sessions:
            print(f" ALREADY HERE: {vehicle_id} is logged in.")
            return False

        # Setup the session data
        session = {
            "vehicle_id": vehicle_id,
            "time_in": datetime.now(),
            "time_out": None,
            "status": "Active",
            "total_fee": 0.0
        }

        # Store and update count
        self.db.active_sessions[vehicle_id] = session
        self.db.slots_available -= 1

        print(f" ENTRY OK: {vehicle_id} recorded at {datetime.now().strftime('%H:%M:%S')}.")
        return True

    # --- Module 3 & 4: Exit & Payment Logic ---
    def process_exit(self, vehicle_id: str) -> tuple[float, bool]:
        """ Calculates time/fee, simulates payment, opens gate. """
        if vehicle_id not in self.db.active_sessions:
            print(f" NOT FOUND: {vehicle_id} isn't in the active list.")
            return 0.0, False

        session = self.db.active_sessions[vehicle_id]

        # 1. Calculate Time
        time_out = datetime.now()
        duration = time_out - session["time_in"]

        # 2. Calculate Fee (Call helper function)
        total_fee = self._calculate_fare(duration)

        # 3. Update Session (Move to history)
        session["time_out"] = time_out
        session["total_fee"] = total_fee
        session["status"] = "Completed"

        # Update DB state
        self.db.slots_available += 1
        del self.db.active_sessions[vehicle_id] 
        self.db.history_log.append(session)

        print(f"\n--- EXIT REPORT for {vehicle_id} ---")
        print(f"Time Spent: {duration}")
        print(f"Fee Due: ${total_fee:.2f}")
        print("------------------------------------")

        # 4. Payment & Barrier Control
        payment_successful = self._simulate_payment(total_fee)

        if payment_successful:
            print(" PAYMENT OK: Barrier OPEN.")
            return total_fee, True
        else:
            print("PAYMENT FAIL: Barrier STAYS CLOSED.")
            return total_fee, False

    # --- Helper: Fare Calculator ---
    def _calculate_fare(self, duration: timedelta) -> float:
        """ Checks rules sequentially to find the correct price. """
        # 1. Check grace period first (Simplest check)
        time_past_free = max(0, duration - self.config.FREE_TIME_GRACE_PERIOD)

        if time_past_free.total_seconds() <= 0:
            print("( Free time used!)")
            return 0.0

        hours_spent = time_past_free.total_seconds() / 3600.0

        # 2. Iterate through tiers to find the right price bracket
        for name, tier_data in self.config.PRICING_TIERS.items():
            if name == "Tier4" or hours_spent <= tier_data['max_hours']:
                return tier_data['fee']

        return 0.0 # Should not happen

    # --- Helper: Payment Simulator ---
    def _simulate_payment(self, amount_due: float) -> bool:
        """ Fakes the payment gateway connection. """
        if amount_due == 0.0:
            return True # Free means instant success

        # Random chance of success for the simulation
        return random.random() < 0.9 # 90% success rate

# ======================================================================
# RUNNER (Testing the System)
# ======================================================================

def run_parking_simulation():
    """ Runs the whole system demo loop. """
    print("==============================================")
    print("     STARTING PARKING SYSTEM DEMO    ")
    print("==============================================")

    manager = ParkingSystemManager()

    # 1. Show initial status
    manager.get_slot_status()

    # --- TEST CASE 1: Short Stay (Should be free) ---
    print("\n--- RUNNING TEST 1: Quick Car (Should be free) ---")
    car_a = "XYZ-123"
    manager.register_entry(car_a)
    time.sleep(timedelta(minutes=10).total_seconds()) 

    manager.get_slot_status() 
    fee_a, success_a = manager.process_exit(car_a)
    print(f"TEST 1 RESULT: Paid ${fee_a:.2f} | Gate: {'Open' if success_a else 'Closed'}")

    # --- TEST CASE 2: Long Stay (Should hit the high tier) ---
    print("\n--- RUNNING TEST 2: Long Car (Should hit Tier 4 - $500) ---")
    car_b = "ABC-789"
    manager.register_entry(car_b)
    time.sleep(timedelta(hours=7)) # More than 6 hours

    manager.get_slot_status()
    fee_b, success_b = manager.process_exit(car_b)
    print(f"TEST 2 RESULT: Paid ${fee_b:.2f} | Gate: {'Open' if success_b else 'Closed'}")

    # --- TEST CASE 3: Error Case (Car not found) ---
    print("\n--- RUNNING TEST 3: Bad Car ID ---")
    manager.process_exit("GARBAGE-ID")

    print("\n==============================================")
    print("SYSTEM DEMO FINISHED.")
    print("==============================================")

if __name__ == "__main__":
    run_parking_simulation()