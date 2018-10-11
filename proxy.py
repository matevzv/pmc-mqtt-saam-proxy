#!/usr/bin/env python3

import json
import paho.mqtt.client as mqtt

pmcs = [("pmc/1670020454100061004aa000a0000005",0),("pmc/16700204541000610066a000a00000c1",0)]
counters = {"1670020454100061004aa000a0000005": 0, "16700204541000610066a000a00000c1": 0}

saam_msg = {}
url_sub = "193.2.205.66"

url_pub = "localhost"
mqtts = mqtt.Client()
mqtts.username_pw_set("user", "pass")
mqtts.connect(url_pub)

def on_connect(mqttc, userdata, flags, rc):
    global pmcs
    print("Connected with result code "+str(rc))
    mqttc.subscribe(pmcs)

def on_message(mqttc, userdata, msg):
    global saam_msg
    global counters

    data = json.loads(msg.payload.decode('utf-8'))
    node_id = data["node_id"]

    if counters[node_id] == 20:
        sid = saam_msg[node_id]["node_id"]
        del saam_msg[node_id]["node_id"]
        
        for field in saam_msg[node_id]:
            mqtts.publish("saam_data/"+sid+"/"+field, json.dumps(saam_msg[node_id][field]))
        del saam_msg[node_id]
        counters[node_id] = 0
    else:
        counters[node_id] = counters[node_id] + 1

    saam_id = node_id
    ts = data["ts"]
    del data["node_id"]
    del data["ts"]
    del data["input_1_status"]
    del data["input_2_status"]
    del data["input_3_status"]

    if node_id not in saam_msg:
        saam_msg[node_id] = {"node_id": saam_id}

    for i,field in enumerate(data):
        source_id = field
        if source_id not in saam_msg[node_id]:
            saam_msg[node_id][source_id] = {"timestamp": ts, "period": 500, "measurements": []}
        saam_msg[node_id][source_id]["measurements"].append(float(data[field]))

mqttc = mqtt.Client()
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.connect(url_sub)

mqttc.loop_forever()
