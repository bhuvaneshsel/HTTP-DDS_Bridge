from flask import Flask, request, jsonify
import sys
import os
import time
import json

#gets the directory for the ddspython build and tells the system to look there for files in general
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(base_dir, "../dds/build"))

#the c++ code wrapped in PYBIND11
import ddspython


app = Flask(__name__)


@app.route('/DDS-read', methods=['GET'])
def DDS_read():
    sub = ddspython.BSubscriber()
    sub.init()
    sub = ddspython.BSubscriber()
    if not sub.init():
        print("FAILED")
        return jsonify({"error": "Subscriber failed to initialize"}), 500

    sub.run()
    data = sub.get_json_data()
    print("DDS-read received:", data)
    return jsonify(data)


@app.route("/DDS-write", methods=["POST"])
def DDS_write():
    pub = ddspython.BPublisher()
    if not pub.init():
        return jsonify({"error": "Publisher failed to initialize"}), 500
    try:
        data = request.get_json()
        pub.set_data(data)
        success = pub.publish()
        if success:
            return jsonify({"status": "Published successfully"})
        else:
            return jsonify({"status": "No subscribers matched"}), 202
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

