import math
import random
import matplotlib.pyplot as plt

def calculate_mmc_wait(arrival_rate, service_rate, num_plugs):
    if num_plugs == 0: return 999
    # Traffic intensity (rho)
    rho = arrival_rate / (num_plugs * service_rate)
    if rho >= 0.99: return 50.0  # Cap for visualization
    # Probability of waiting (Simplified Erlang-C)
    pw = (rho ** num_plugs) 
    expected_wait = pw / (num_plugs * service_rate * (1 - rho))
    return max(0, expected_wait)

def run_stress_test(total_users):
    """
    Simulates a charging hub with 4 plugs and observes system behavior.
    """
    num_plugs = 4
    avg_charge_time = 40.0 # Minutes
    mu = 1.0 / avg_charge_time
    
    # Data containers for the graph
    user_indices = []
    wait_times = []
    collision_counts = []
    current_collisions = 0

    print(f"\n[!] Starting simulation for {total_users} users...")

    for i in range(1, total_users + 1):
        # Dynamically scale arrival rate as users increase
        arrival_rate = (i / 60.0) * 0.15 
        
        # Calculate Stochastic Wait
        wait = calculate_mmc_wait(arrival_rate, mu, num_plugs)
        
        # Simulate Herding Mitigation (Anti-clustering logic)
        # If user is NOT mitigated, they add to the 'collision' count at Station A
        is_mitigated = random.random() > 0.75
        if not is_mitigated and i > num_plugs:
            current_collisions += 1
        
        user_indices.append(i)
        wait_times.append(wait)
        collision_counts.append(current_collisions)

    # --- PLOTTING THE RESULTS ---
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Plot Wait Time (Exponential Growth)
    color = 'tab:red'
    ax1.set_xlabel('Total Simulated Users')
    ax1.set_ylabel('Predicted Wait Time (Min)', color=color, fontweight='bold')
    ax1.plot(user_indices, wait_times, color=color, linewidth=2, label='M/M/c Wait Time')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(True, linestyle='--', alpha=0.6)

    # Create a second y-axis for Collisions
    ax2 = ax1.twinx()
    color = 'tab:blue'
    ax2.set_ylabel('Mitigated System Collisions', color=color, fontweight='bold')
    ax2.fill_between(user_indices, collision_counts, color=color, alpha=0.2, label='Collisions')
    ax2.tick_params(axis='y', labelcolor=color)

    plt.title(f'Algorithm Stress Test: {total_users} Concurrent Users', fontweight='bold')
    fig.tight_layout()
    
    print("[+] Simulation complete. Generating graph...")
    plt.show()

if __name__ == "__main__":
    try:
        val = int(input("Enter the number of users to simulate (e.g., 100, 500, 1000): "))
        if val > 0:
            run_stress_test(val)
        else:
            print("Please enter a positive integer.")
    except ValueError:
        print("Invalid input. Please enter a number.")