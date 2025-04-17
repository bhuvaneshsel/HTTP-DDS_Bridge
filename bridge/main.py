from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/DDS-write", methods=["POST"])
def DDS_write():
    data = request.get_json()
    
    return jsonify(data), 201

@app.route("/DDS-read")
def DDS_read():
    user_data = {
        "name": "John",
        "email": "john@example.com",
    }

    print("DDS READ")
    return jsonify(user_data), 200


if __name__ == "__main__":
    app.run(debug=True)


