from flask import Flask, request, jsonify
import sys
import os
import time

#gets the directory for the ddspython build and tells the system to look there for files in general
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(base_dir, "../dds/build"))

#the c++ code wrapped in PYBIND11
import ddspython

# cache pub
publishers = {}
# cache sub
subscribers = {}

app = Flask(__name__)

# no param call, direct user properly
@app.route('/DDS-read', methods=['GET'])
def DDS_read_missing_topic():
    return jsonify({"error": "Missing DDS topic. Use /DDS-read/<dds_topic>"}), 400

@app.route('/DDS-read/<dds_topic>', methods=['GET'])
def DDS_read(dds_topic):
    try:
        # caching
        if dds_topic not in subscribers:
            try:
                sub = ddspython.TestSubscriber()
                sub.set_topics(dds_topic)
                if not sub.init():
                    return jsonify({"error": f"Failed to init subscriber for topic '{dds_topic}'"}), 500
                subscribers[dds_topic] = sub
            except Exception as e:
                return jsonify({"error": f"Failed to create subscriber for topic '{dds_topic}'", "details": str(e)}), 500
        else:
            sub = subscribers[dds_topic]

        # read data
        dds_object = sub.get_json_data()

        return dds_object, 200
    except Exception as e:
        return jsonify({"error": "Failed to read from DDS", "details": str(e)}), 500

# no param call, direct user properly
@app.route('/DDS-write', methods=['POST'])
def DDS_write_missing_topic_name():
    return jsonify({"error": "Missing topic name. Use /DDS-write/<topic_name>"}), 400

@app.route("/DDS-write/<topic_name>", methods=["POST"])
def DDS_write(topic_name):
    # read json
    try:
        data = request.get_json(force=True)
    except Exception as e:
        return jsonify({"error": "Invalid JSON", "details": str(e)}), 400

    # verify required fields, change as needed
    required_fields = {"index", "message"}
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    # caching
    if topic_name not in publishers:
        try:
            pub = ddspython.TestPublisher()
            pub.set_topic(topic_name)
            if not pub.init():
                return jsonify({"error": f"Failed to initialize publisher for topic '{topic_name}'"}), 500
            publishers[topic_name] = pub
        except Exception as e:
            return jsonify({"error": f"Failed to create publisher for topic '{topic_name}'", "details": str(e)}), 500
    else:
        pub = publishers[topic_name]

    # set data in preparation for publishing
    try:
        pub.set_data(data)
    except Exception as e:
        return jsonify({"error": "Failed to set data", "details": str(e)}), 500

    # publishes data
    if pub.publish():  
        return jsonify({"status": "published", "topic": topic_name}), 200
    else:
        return jsonify({"status": "no subscriber matched"}), 503

if __name__ == "__main__":
    app.run(debug=True)
