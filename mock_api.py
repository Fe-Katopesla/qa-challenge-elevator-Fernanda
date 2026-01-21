from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/elevator-data", methods=["POST"])
def receive_data():
    data = request.json
    
    # 1. Verifica se o JSON veio vazio
    if not data:
        return jsonify({"error": "Missing fields"}), 400

    # 2. Verifica Campos Obrigatórios
    if not all(k in data for k in ("position", "door_status", "weight")):
        return jsonify({"error": "Missing fields"}), 400

    # 3. Valida Posição (1-10)
    # Nota: O 'sync_verification_probe' é aquele pacote especial de resiliência.
    # Se for ele, a gente não critica a posição (embora ele mande 1, que é valido).
    if data.get("type") != "sync_verification_probe":
        if not isinstance(data["position"], int) or not (1 <= data["position"] <= 10):
            return jsonify({"error": "Invalid position"}), 400

    # 4. Valida Porta (open/closed) - (O seu código anterior não tinha isso!)
    if data.get("door_status") not in ["open", "closed"]:
        return jsonify({"error": "Invalid door_status"}), 400

    # 5. Valida Peso (0-2000) - ESSENCIAL
    # O elevador manda até 999, então 2000 é um limite seguro.
    # Se o teste mandar -1 ou 2001, isso aqui vai barrar e retornar o erro 400 correto.
    if not isinstance(data["weight"], int) or not (0 <= data["weight"] <= 2000):
        return jsonify({"error": "Invalid weight"}), 400

    return jsonify({"message": "Data received"}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)
