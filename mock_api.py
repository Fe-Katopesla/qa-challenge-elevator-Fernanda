from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/elevator-data", methods=["POST"])
def receive_data():
    data = request.json
    if not all(k in data for k in ("position", "door_status", "weight")):
        return jsonify({"error": "Missing fields"}), 400
    if not isinstance(data["position"], int) or not (1 <= data["position"] <= 10):
        return jsonify({"error": "Invalid position"}), 400
    return jsonify({"message": "Data received"}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)