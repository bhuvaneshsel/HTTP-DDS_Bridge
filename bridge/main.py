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


@app.route('/DDS-read/<dds_topic>', methods=['GET'])
def DDS_read(dds_topic):

    #Extra parameters received from URL are put into a dictionary here. Anything after any question marks: ?extraInfo1?extraInfo2.
    #extraInformation = request.args

    #Creates subscriber instance.
    #sub = ddspython.TestSubscriber()
    #Set topic for sub
    #sub.set_topic(dds_topic)

    #if sub.init():
       # print("Activated Subscriber.")
    #else:
       # print("Failed to activate subscriber.")
      #  return

    #Gets the data from the subscriber once connected, should be synchronous, awaits for data.
        #If data takes too long (start timer), then return an exception.
    #dds_object = sub.get_data()

    dds_object = {
        "dds_name": "temporary",
        "data": "some data",
        "extra_info": "extraInformation",
    }

    #jsonfiy --> jsonfies a dictionary in to a JSON object.
    return jsonify(dds_object)


@app.route("/DDS-write", methods=["POST"])
def DDS_write():
    try:
        data = request.get_json(force=True)
    except Exception as e:
        return jsonify({"error": "Invalid JSON", "details": str(e)}), 400

    if "index" not in data or "message" not in data:
        return jsonify({"error": "Missing 'index' or 'message' field"}), 400

    #sets data of message that will be sent

    index = data["index"]
    message = data["message"]
    
    pub.set_data(index, message)

    #publishes data
    if pub.publish():  
        return jsonify({"status": "published"}), 200
    else:
        return jsonify({"status": "no subscriber matched"}), 503

if __name__ == "__main__":
    app.run(debug=True)

