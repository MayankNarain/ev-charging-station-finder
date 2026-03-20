import matplotlib
matplotlib.use('Agg') # Ensure thread-safe rendering for web server

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import math
import random
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)
CORS(app)

API_KEY = "5edba2c9-c475-4aac-afe9-2188a0c80e25"

def calculate_nonlinear_charging_time(current_soc, target_soc, battery_capacity_kwh, charger_kw):
    charger_kw = float(charger_kw) if charger_kw else 50.0 
    fast_limit = 80.0
    t_fast = (min(target_soc, fast_limit) - current_soc) / 100 * battery_capacity_kwh / charger_kw if current_soc < fast_limit else 0
    t_slow = (target_soc - max(current_soc, fast_limit)) / 100 * battery_capacity_kwh / (charger_kw * 0.4) if target_soc > fast_limit else 0
    return max(0, (t_fast + t_slow) * 60)

@app.route('/api/get_smart_stations', methods=['GET'])
def get_smart_stations():
    user_lat = float(request.args.get('lat'))
    user_lng = float(request.args.get('lng'))
    current_battery = float(request.args.get('battery', 25.0))
    
    url = f"https://api.openchargemap.io/v3/poi/?output=json&latitude={user_lat}&longitude={user_lng}&distance=20&maxresults=10&key={API_KEY}"
    try:
        data = requests.get(url).json()
    except:
        return jsonify({"error": "OCM API Unreachable"}), 500
        
    processed_stations = []
    best_id, min_total = None, float('inf')

    for item in data:
        if not item.get('AddressInfo'): continue
        lat, lng = item['AddressInfo']['Latitude'], item['AddressInfo']['Longitude']
        dist_km = math.hypot(user_lat - lat, user_lng - lng) * 111.0 
        travel_time = (dist_km / 35.0) * 60 
        
        connectors = item.get('Connections', [])
        c_plugs = max(len(connectors), 1)
        max_kw = max([c.get('PowerKW', 50) or 50 for c in connectors]) if connectors else 50
        charge_time = calculate_nonlinear_charging_time(current_battery, 85, 50, max_kw)
        
        inbound = random.randint(0, 4)
        wait_time = (inbound / (c_plugs * (1/40.0))) if inbound > 0 else 0
        total = travel_time + wait_time + charge_time
        
        if total < min_total:
            min_total, best_id = total, item['ID']

        processed_stations.append({
            "id": item['ID'], "name": item['AddressInfo']['Title'],
            "lat": lat, "lng": lng, "travel_time": round(travel_time), 
            "wait_time": round(wait_time), "charge_time": round(charge_time), 
            "total_cost": round(total), "is_smart": False
        })

    for s in processed_stations: s['is_smart'] = (s['id'] == best_id)
    return jsonify(processed_stations)

@app.route('/api/get_graph', methods=['POST'])
def get_graph():
    """Generates a vertical stack of 3 individual metrics + 1 resultant graph."""
    d = request.json
    metrics = [d['travel_time'], d['wait_time'], d['charge_time']]
    total = d['total_cost']
    
    # Create 4 subplots vertically
    fig, axes = plt.subplots(4, 1, figsize=(6, 10))
    fig.tight_layout(pad=4.0)

    # 1. Driving Time
    axes[0].barh(['Driving'], [d['travel_time']], color='#3498db')
    axes[0].set_title("Component 1: Travel Distance Time")
    axes[0].set_xlim(0, max(metrics + [50]))
    axes[0].set_xlabel("Minutes")

    # 2. Wait Time
    axes[1].barh(['Queuing'], [d['wait_time']], color='#e74c3c')
    axes[1].set_title("Component 2: M/M/c Predicted Wait")
    axes[1].set_xlim(0, max(metrics + [50]))
    axes[1].set_xlabel("Minutes")

    # 3. Charge Time
    axes[2].barh(['Charging'], [d['charge_time']], color='#2ecc71')
    axes[2].set_title("Component 3: Non-Linear CC-CV Charge")
    axes[2].set_xlim(0, max(metrics + [50]))
    axes[2].set_xlabel("Minutes")

    # 4. FINAL RESULT (STACKED)
    axes[3].barh(['TOTAL RESULT'], [d['travel_time']], color='#3498db', label='Drive')
    axes[3].barh(['TOTAL RESULT'], [d['wait_time']], left=[d['travel_time']], color='#e74c3c', label='Wait')
    axes[3].barh(['TOTAL RESULT'], [d['charge_time']], left=[d['travel_time']+d['wait_time']], color='#2ecc71', label='Charge')
    axes[3].set_title("Resultant: Integrated Smart Score", fontweight='bold')
    axes[3].set_xlabel(f"Final Committment: {total} Minutes")
    
    # Add a vertical target line on the result
    axes[3].axvline(x=total, color='black', linestyle='--')

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    img_str = base64.b64encode(buf.getvalue()).decode('utf-8')
    return jsonify({"graph": img_str})

if __name__ == '__main__':
    app.run(debug=True, port=5000)