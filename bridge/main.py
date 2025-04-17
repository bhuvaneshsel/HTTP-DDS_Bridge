from flask import Flask, request, jsonify
import sys
import os
import time

#gets the directory for the ddspython build and tells the system to look there for files in general
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(base_dir, "../dds/build"))

#the c++ code wrapped in PYBIND11
import ddspython

# Create the publisher instance
pub = ddspython.TestPublisher()

if pub.init():
    print("DDS publisher initialized.")
else:
    print("DDS publisher initialization failed.")
    

app = Flask(__name__)

@app.route("/DDS-write", methods=["POST"])
def DDS_write():
    data = request.get_json();

    index = data.get("index", 0)
    message = data.get("message", "")

    #sets data of message that will be sent
    pub.set_data(index, message)

    #publishes data
    if pub.publish():  
        return jsonify({"status": "published"}), 200
    else:
        return jsonify({"status": "no subscriber matched"}), 503

if __name__ == "__main__":
    app.run(debug=True)

