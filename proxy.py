#!/usr/bin/env python3

import json
import paho.mqtt.client as mqtt

url_sub = "localhost"
pmcs = [("pmc/16700204541000610066a000a00000c1",0), 
        ("pmc/1670020454100061004aa000a0000005",0),
        ("pmc/16700204541000610088a000a0000045",0),
        ("pmc/16700204541000610080a000a000007d",0)]

url_pub = "localhost"
mqtts = mqtt.Client()
mqtts.username_pw_set("user", "pass")
mqtts.connect(url_pub)
mqtts.loop_start()

saam_msg = {}
counters = {"16700204541000610066a000a00000c1": 0,
            "1670020454100061004aa000a0000005": 0,
            "16700204541000610088a000a0000045": 0,
            "16700204541000610080a000a000007d": 0}

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
        sid = saam_msg["node_id"]
        del saam_msg["node_id"]
        
        for field in saam_msg:
            mqtts.publish("saam/"+sid+"/"+field, json.dumps(saam_msg[field]))
        saam_msg = {}
        counters[node_id] = 0

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
            saam_msg[source_id] = {"timestamp": ts, "period": 500, "measurements": []}
        saam_msg[source_id]["measurements"].append(float(data[field]))

    counters[node_id] = counters[node_id] + 1

mqttc = mqtt.Client()
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.connect(url_sub)

mqttc.loop_forever()
