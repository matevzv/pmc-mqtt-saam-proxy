import json
import time
import paho.mqtt.client as mqtt

#url_pub = "localhost"
#mqtts = mqtt.Client()
#mqtts.connect(url_pub)

saam_msg = {}
counters = {"16700204541000610080a000a000007d": 0}

while True:
    msg = b'{"node_id":"16700204541000610080a000a000007d","ts":1537801843459,"phase_1_voltage_rms":234.58,"phase_2_voltage_rms":234.56,"phase_3_voltage_rms":234.16,"phase_1_current_rms":0.93,"phase_2_current_rms":0.99,"phase_3_current_rms":0.26,"n_line_calculated_current_rms":1.99,"phase_1_frequency":50,"phase_2_voltage_phase":0,"phase_3_voltage_phase":119.6,"phase_1_voltage_thd_n":3.97,"phase_2_voltage_thd_n":3.97,"phase_3_voltage_thd_n":5.23,"phase_1_current_thd_n":114.45,"phase_2_current_thd_n":109.35,"phase_3_current_thd_n":11.62,"phase_1_active_power":131,"phase_2_active_power":143,"phase_3_active_power":21,"phase_1_reactive_power":-54,"phase_2_reactive_power":-52,"phase_3_reactive_power":-52,"phase_1_apparent_power":218,"phase_2_apparent_power":231,"phase_3_apparent_power":60,"phase_1_power_factor":0.6,"phase_2_power_factor":0.62,"phase_3_power_factor":0.35,"phase_1_active_fundamental":134,"phase_2_active_fundamental":146,"phase_3_active_fundamental":21,"phase_1_active_harmonic":-3,"phase_2_active_harmonic":-3,"phase_3_active_harmonic":0,"phase_1_forward_active":0.02,"phase_2_forward_active":0.02,"phase_3_forward_active":0,"phase_1_reverse_active":0,"phase_2_reverse_active":0,"phase_3_reverse_active":0,"phase_1_forward_reactive":0,"phase_2_forward_reactive":0,"phase_3_forward_reactive":0,"phase_1_reverse_reactive":0.01,"phase_2_reverse_reactive":0.01,"phase_3_reverse_reactive":0.01,"phase_1_apparent_energy":0.03,"phase_2_apparent_energy":0.03,"phase_3_apparent_energy":0.01,"measured_temperature":35,"input_1_status":0,"input_2_status":0,"input_3_status":0}'

    data = json.loads(msg.decode('utf-8'))
    data["ts"] = int(round(time.time() * 1000))
    node_id = data["node_id"]

    saam_id = node_id
    ts = data["ts"]
    del data["node_id"]
    del data["ts"]
    del data["input_1_status"]
    del data["input_2_status"]
    del data["input_3_status"]

    if not saam_msg:
        saam_msg = {"node_id": saam_id}

    for i,field in enumerate(data):
        source_id = field
        if source_id not in saam_msg:
            saam_msg[source_id] = {"timestamp": ts, "measurements": []}
        saam_msg[source_id]["measurements"].append(float(data[field]))

    if counters[node_id] == 10:
        sid = saam_msg["node_id"]
        del saam_msg["node_id"]
        print(ts)
        for field in saam_msg:
            #client.publish("saam_data/"+sid+"/"+field, json.dumps(saam_msg[field]))
            saam_msg[field]["timestep"] = round((ts - saam_msg[field]["timestamp"]) / 1000, 1)
            print(json.dumps(saam_msg[field]))
        saam_msg = {}
        counters[node_id] = 0
    
    counters[node_id] = counters[node_id] + 1

    #print(json.dumps(saam_msg))
    time.sleep(0.5)