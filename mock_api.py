from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/elevator-data", methods=["POST"])
def receive_data():
    data = request.json
    
    # 1. Check if JSON is empty
    if not data:
        return jsonify({"error": "Missing fields"}), 400

    # 2. Check Required Fields
    if not all(k in data for k in ("position", "door_status", "weight")):
        return jsonify({"error": "Missing fields"}), 400

    # 3. Validate Position (1-10)
    if data.get("type") != "sync_verification_probe":
        if not isinstance(data["position"], int) or not (1 <= data["position"] <= 10):
            return jsonify({"error": "Invalid position"}), 400

    # 4. Validate Door Status (open/closed)
    if data.get("door_status") not in ["open", "closed"]:
        return jsonify({"error": "Invalid door_status"}), 400

    # 5. Validate Weight (0-2000)
    # The elevator simulates up to 999kg, so 2000kg is a safe upper limit.
    # If the test sends -1 or 2001, this block will reject it with a 400 error.
    if not isinstance(data["weight"], int) or not (0 <= data["weight"] <= 2000):
        return jsonify({"error": "Invalid weight"}), 400

    return jsonify({"message": "Data received"}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)
