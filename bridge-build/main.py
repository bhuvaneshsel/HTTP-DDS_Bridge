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

# no param call, direct user properly
@app.route('/DDS-read', methods=['GET'])
def DDS_read_missing_topic():
    return jsonify({"error": "Missing DDS topic. Use /DDS-read/<dds_topic>"}), 400

@app.route('/DDS-read/<dds_topic>', methods=['GET'])
def DDS_read(dds_topic):
    try:
        subscriber_name = f"{dds_topic}Subscriber"

        SubscriberClass = getattr(ddspython, subscriber_name)

        sub = SubscriberClass()
        
        if not sub.init():
            return jsonify({"error": "Subscriber failed to initialize"}), 500
        
        sub.run()
        # read data
        print(sub.get_json_data())
        raw_json_str = sub.get_json_data()
  
        try:
            json_data = json.loads(raw_json_str)
            return jsonify(json_data), 200
        except Exception as e:
            print("Error decoding JSON:", e)
            return jsonify({"error": f"Invalid JSON format: {str(e)}"}), 500
    
    except AttributeError:
        return jsonify({"error": f"Publisher class for '{dds_topic}' not found"}), 404
    except Exception as e:
        return jsonify({"error": "Failed to read from DDS", "details": str(e)}), 500


# no param call, direct user properly
@app.route('/DDS-write', methods=['POST'])
def DDS_write_missing_topic_name():
    return jsonify({"error": "Missing topic name. Use /DDS-write/<topic_name>"}), 400

@app.route("/DDS-write/<dds_topic>", methods=["POST"])
def DDS_write(dds_topic):
    try:

        publisher_name = f"{dds_topic}Publisher"

        # find corresponding publisher
        PublisherClass = getattr(ddspython, publisher_name)

        # run publisher
        pub = PublisherClass()

        # get and verify data
        data = request.get_json(force=True)

        if data is None:
            return jsonify({"error": "Invalid or missing JSON"}), 400
        
        if not pub.init():
            return jsonify({"error": "Publisher failed to initialize"}), 500
    
        try:
            pub.set_data(data)
        except Exception as e:
            return jsonify({"error": f"Improper formatting for topic: '{dds_topic}'"}), 400
        
        pub.publish()
        
        return jsonify({"status": "success"}), 200
    except AttributeError:
        return jsonify({"error": f"Publisher class for '{dds_topic}' not found"}), 404
    except Exception as e:
        return jsonify({"error": "Failed to publish", "details": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

