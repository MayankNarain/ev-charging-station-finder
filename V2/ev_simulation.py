import math
import random
import matplotlib.pyplot as plt

# =====================================================================
# AAAI EV Congestion Scalability Framework
# Description: Tests algorithm degradation under increasing network load.
# =====================================================================

class ChargingStation:
    def __init__(self, station_id, x, y, plugs, mu):
        self.id = station_id
        self.x = x
        self.y = y
        self.plugs = plugs          # Number of parallel servers (plugs)
        self.mu = mu                # Service rate (charge progress per tick)
        
        self.queue = []             # EVs physically waiting
        self.charging = []          # EVs currently plugged in
        self.inbound_count = 0      # EVs currently driving towards this station

    def get_expected_wait_time(self):
        """M/M/c Deterministic fluid approximation for expected wait."""
        total_load = len(self.queue) + len(self.charging) + self.inbound_count
        if total_load < self.plugs:
            return 0.0
        return (total_load - self.plugs + 1) / (self.plugs * self.mu)

    def tick(self):
        for ev in self.charging[:]:
            ev.charge_needed -= self.mu
            if ev.charge_needed <= 0:
                ev.state = "done"
                self.charging.remove(ev)
        
        while len(self.charging) < self.plugs and len(self.queue) > 0:
            next_ev = self.queue.pop(0)
            next_ev.state = "charging"
            self.charging.append(next_ev)


class EVAgent:
    def __init__(self, ev_id, x, y, charge_needed):
        self.id = ev_id
        self.x = x
        self.y = y
        self.charge_needed = charge_needed
        self.target_station = None
        self.travel_time_remaining = 0
        self.total_wait_time = 0
        self.total_travel_time = 0
        self.state = "routing" 

    def select_station(self, stations, algorithm, speed):
        best_station = None
        best_cost = float('inf')

        for station in stations:
            dist = math.hypot(self.x - station.x, self.y - station.y)
            travel_time = dist / speed

            if algorithm == "nearest":
                cost = travel_time
            elif algorithm == "smart":
                expected_wait = station.get_expected_wait_time()
                cost = travel_time + expected_wait

            if cost < best_cost:
                best_cost = cost
                best_station = station
                self.travel_time_remaining = travel_time

        self.target_station = best_station
        self.target_station.inbound_count += 1
        self.total_travel_time = self.travel_time_remaining
        self.state = "driving"

    def tick(self):
        if self.state == "driving":
            self.travel_time_remaining -= 1
            if self.travel_time_remaining <= 0:
                self.state = "waiting"
                self.target_station.inbound_count -= 1
                self.target_station.queue.append(self)
        elif self.state == "waiting":
            self.total_wait_time += 1


class EVSimulation:
    def __init__(self, num_stations, num_evs, algorithm, seed=42):
        self.time = 0
        self.algorithm = algorithm
        self.speed = 1.0 
        random.seed(seed)
        
        # Keep station configurations consistent across runs
        self.stations = [
            ChargingStation(i, random.uniform(0, 100), random.uniform(0, 100), 
                            plugs=random.randint(2, 6), mu=random.uniform(0.5, 1.5)) 
            for i in range(num_stations)
        ]
        
        self.evs = [
            EVAgent(i, random.uniform(0, 100), random.uniform(0, 100), charge_needed=random.uniform(20, 60))
            for i in range(num_evs)
        ]
        
        for ev in self.evs:
            ev.select_station(self.stations, self.algorithm, self.speed)

    def run(self):
        while any(ev.state != "done" for ev in self.evs):
            self.time += 1
            for station in self.stations:
                station.tick()
            for ev in self.evs:
                ev.tick()
            
            if self.time > 15000: # Failsafe
                break
        
        avg_wait = sum(ev.total_wait_time for ev in self.evs) / len(self.evs)
        return avg_wait

# ==========================================
# SCALABILITY EXPERIMENT RUNNER
# ==========================================
if __name__ == "__main__":
    print("Initializing Scalability Framework...")
    NUM_STATIONS = 10
    SEED = 101
    
    # We will test the network with 50, 100, 150, 200, 250, and 300 cars.
    ev_counts = [50, 100, 150, 200, 250,300]
    
    baseline_waits = []
    smart_waits = []

    print(f"{'EV Count':<10} | {'Baseline Wait':<15} | {'Smart Wait':<15}")
    print("-" * 45)

    for count in ev_counts:
        # Run Baseline
        sim_base = EVSimulation(NUM_STATIONS, count, algorithm="nearest", seed=SEED)
        base_wait = sim_base.run()
        baseline_waits.append(base_wait)

        # Run Smart Alg
        sim_smart = EVSimulation(NUM_STATIONS, count, algorithm="smart", seed=SEED)
        smart_wait = sim_smart.run()
        smart_waits.append(smart_wait)
        
        # Print progress to terminal
        print(f"{count:<10} | {base_wait:<15.2f} | {smart_wait:<15.2f}")

    # --- GENERATE LINE GRAPH ARTIFACT ---
    plt.figure(figsize=(10, 6))
    
    # Plotting the lines
    plt.plot(ev_counts, baseline_waits, marker='o', color='#e74c3c', linewidth=2, label='Baseline (Nearest Station)')
    plt.plot(ev_counts, smart_waits, marker='s', color='#2ecc71', linewidth=2, label='Proposed (Smart Routing)')
    
    # Formatting the graph to look academic
    plt.title('Algorithm Scalability: Average Wait Time vs. Fleet Size', fontsize=14, pad=15)
    plt.xlabel('Number of Active EVs in Network', fontsize=12)
    plt.ylabel('Average Wait Time (Minutes)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=12)
    
    # Save the output
    plt.savefig('scalability_benchmark.png', dpi=300, bbox_inches='tight')
    print("\nSimulation complete. High-resolution graph saved as 'scalability_benchmark.png'.")