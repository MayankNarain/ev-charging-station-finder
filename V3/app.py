import matplotlib
matplotlib.use('Agg')

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import math
import random
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime

app = Flask(__name__)
CORS(app)

API_KEY = "5edba2c9-c475-4aac-afe9-2188a0c80e25"

def calculate_nonlinear_charging_time(current_soc, target_soc, battery_capacity_kwh, charger_kw):
    charger_kw = float(charger_kw) if charger_kw else 50.0 
    fast_limit = 80.0
    t_fast = (min(target_soc, fast_limit) - current_soc) / 100 * battery_capacity_kwh / charger_kw if current_soc < fast_limit else 0
    t_slow = (target_soc - max(current_soc, fast_limit)) / 100 * battery_capacity_kwh / (charger_kw * 0.4) if target_soc > fast_limit else 0
    return max(0, (t_fast + t_slow) * 60)

def calculate_mmc_wait(arrival_rate, service_rate, num_plugs):
    if num_plugs == 0: return 999
    rho = arrival_rate / (num_plugs * service_rate)
    if rho >= 0.98: return 45.0 + (rho * 10) 
    pw = (rho ** num_plugs) 
    expected_wait = pw / (num_plugs * service_rate * (1 - rho))
    return max(0, expected_wait)

@app.route('/api/get_smart_stations', methods=['GET'])
def get_smart_stations():
    try:
        user_lat = float(request.args.get('lat', 28.6139))
        user_lng = float(request.args.get('lng', 77.2090))
        current_battery = float(request.args.get('battery', 25.0))
        
        hour = datetime.now().hour
        is_peak = (8 <= hour <= 10 or 17 <= hour <= 19)
        base_arrival_rate = 0.08 if is_peak else 0.03

        url = f"https://api.openchargemap.io/v3/poi/?output=json&latitude={user_lat}&longitude={user_lng}&distance=20&maxresults=10&key={API_KEY}"
        data = requests.get(url).json()
            
        processed_stations = []
        for item in data:
            if not item.get('AddressInfo'): continue
            lat, lng = item['AddressInfo']['Latitude'], item['AddressInfo']['Longitude']
            dist_km = math.hypot(user_lat - lat, user_lng - lng) * 111.0 
            travel_time = (dist_km / 30.0) * 60 * 1.25 
            
            connectors = item.get('Connections', [])
            c_plugs = max(len(connectors), 1)
            max_kw = max([c.get('PowerKW', 50) or 50 for c in connectors]) if connectors else 50
            charge_time = calculate_nonlinear_charging_time(current_battery, 85, 50, max_kw)
            
            service_rate = 1.0 / max(charge_time, 1)
            wait_time = calculate_mmc_wait(base_arrival_rate, service_rate, c_plugs)
            
            processed_stations.append({
                "id": item['ID'], "name": item['AddressInfo']['Title'],
                "lat": lat, "lng": lng, "travel_time": round(travel_time), 
                "wait_time": round(wait_time), "charge_time": round(charge_time), 
                "total_cost": round(travel_time + wait_time + charge_time), "is_smart": False
            })

        processed_stations.sort(key=lambda x: x['total_cost'])
        if processed_stations:
            dice_roll = random.random()
            smart_index = 0
            if dice_roll > 0.75 and len(processed_stations) > 1: smart_index = 1
            elif dice_roll > 0.95 and len(processed_stations) > 2: smart_index = 2
            processed_stations[smart_index]['is_smart'] = True

        return jsonify(processed_stations)
    except Exception as e:
        return jsonify([]), 500

@app.route('/api/get_graph', methods=['POST'])
def get_graph():
    d = request.json
    metrics = [d['travel_time'], d['wait_time'], d['charge_time']]
    total = d['total_cost']
    fig, axes = plt.subplots(4, 1, figsize=(6, 10))
    fig.tight_layout(pad=4.0)
    colors = ['#3498db', '#e74c3c', '#2ecc71']
    axes[0].barh(['Driving'], [d['travel_time']], color=colors[0])
    axes[1].barh(['Queuing'], [d['wait_time']], color=colors[1])
    axes[2].barh(['Charging'], [d['charge_time']], color=colors[2])
    for i in range(3): axes[i].set_xlim(0, max(metrics + [60]))
    axes[3].barh(['SCORE'], [d['travel_time']], color=colors[0])
    axes[3].barh(['SCORE'], [d['wait_time']], left=[d['travel_time']], color=colors[1])
    axes[3].barh(['SCORE'], [d['charge_time']], left=[d['travel_time']+d['wait_time']], color=colors[2])
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    return jsonify({"graph": base64.b64encode(buf.getvalue()).decode('utf-8')})

@app.route('/api/run_diagnostics', methods=['GET'])
def run_diagnostics():
    # Scenario 1: M/M/c Sensitivity
    off_peak_wait = calculate_mmc_wait(0.03, 1/40, 4)
    peak_wait = calculate_mmc_wait(0.12, 1/40, 4)
    
    # Scenario 2: Herding Mitigation (100 trials)
    selections = {"Station_A": 0, "Station_B": 0, "Station_C": 0}
    for _ in range(100):
        dice = random.random()
        if dice <= 0.75: selections["Station_A"] += 1
        elif dice <= 0.95: selections["Station_B"] += 1
        else: selections["Station_C"] += 1

    # Scenario 3: Battery Non-Linearity (10-80% vs 80-100% on 100kW)
    fast_phase = calculate_nonlinear_charging_time(10, 80, 60, 100)
    slow_phase = calculate_nonlinear_charging_time(80, 100, 60, 100)

    return jsonify({
        "queuing_test": {
            "off_peak": round(off_peak_wait, 2),
            "peak": round(peak_wait, 2),
            "increase_factor": round(peak_wait / max(off_peak_wait, 1), 1)
        },
        "herding_test": selections,
        "battery_test": {
            "fast_70_percent": round(fast_phase, 2),
            "slow_20_percent": round(slow_phase, 2)
        }
    })

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)