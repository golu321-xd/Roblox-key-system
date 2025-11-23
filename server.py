from flask import Flask, request, jsonify
import json, random, string, time

app = Flask(__name__)

DATA_FILE = "data.json"

def load_data():
    try:
        return json.load(open(DATA_FILE, "r"))
    except:
        return {"keys": {}}

def save_data(data):
    json.dump(data, open(DATA_FILE, "w"))

def generate_key():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=25))

@app.route("/createkey", methods=["POST"])
def create_key():
    data = load_data()
    key = generate_key()
    data["keys"][key] = {
        "hwid": None,
        "created": time.time(),
        "valid": 86400  # 24 hours
    }
    save_data(data)
    return jsonify({"key": key})

@app.route("/lockkey", methods=["POST"])
def lock_key():
    body = request.json
    key = body.get("key")
    hwid = body.get("hwid")

    data = load_data()
    if key not in data["keys"]:
        return jsonify({"error": "Key not found"}), 404

    data["keys"][key]["hwid"] = hwid
    save_data(data)
    return jsonify({"status": "locked"})

@app.route("/verify", methods=["POST"])
def verify():
    body = request.json
    key = body.get("key")
    hwid = body.get("hwid")

    data = load_data()
    if key not in data["keys"]:
        return jsonify({"result": "invalid"})

    k = data["keys"][key]

    if time.time() - k["created"] > k["valid"]:
        return jsonify({"result": "expired"})

    if k["hwid"] != hwid:
        return jsonify({"result": "hwid_mismatch"})

    return jsonify({"result": "success"})
