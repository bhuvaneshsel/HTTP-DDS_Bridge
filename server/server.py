from flask import Flask, request, jsonify
from fastdds import DomainParticipantFactory, DomainParticipant, Publisher, Topic, DataWriter



app = Flask(__name__)
    #https://www.youtube.com/watch?v=zsYIw6RXjfM
    #WE can use webhooks that instantly receives data on HTTP post (so whenever we send data). Event base (on action do this) instead of request and response based.
        #Issue: how do we get info from publisher constantly when HTTP is request and reponse based? We use even base (web hooks).
            #If we don't then use queue to store then send data.


#Make it faster, only does HTTTP post from DDS side if HTTP CLIENT needs to GET.



#Use a HashMap that is key = dds_topic, value = dds_data received JSON to get 
    #Only thing to keep in mind is whether or not if key-value pair hasn't been used in a while.
    #DDS publisher should send data to HTTP client, newest data should be saved whenever called? But could store outdated info?
dds_map = {}


#Project 3 rule: synchronous, so do await.
#Project 4 rule: new subscribers should get newest data right after it was made. wait for publish instead of hashmap val.
    #Only receives data once publisher updates.
    #Fast DDS should be able to send data in http requests.


# Setup DDS participant and writer
participant = DomainParticipantFactory.get_instance().create_participant(0)
publisher = participant.create_publisher()
topic = participant.create_topic("ControlTopic", "MyCommandType", ...)
writer = publisher.create_datawriter(topic, ...)


# A simple GET endpoint
# Usually defaulted to get request.
    #Should probably specify type dds_item.
@app.route('/getDDS/<dds_item>', methods=['GET'])
def hello(dds_item):

    #Extra parameters received from URL are put into a dictionary here. Anything after any question marks: ?extraInfo1?extraInfo2.
    extraInformation = request.args

    dds_object = {
        "dds_name": "temporary",
        "data": "some data",
        "extra_info": extraInformation
    }

    #jsonfiy --> jsonfies a dictionary in to a JSON object.
    return jsonify(dds_object)



# A simple POST endpoint that receives JSON data then sends it to DDS pub-sub.
@app.route('/sendDDS/<dds_item>', methods=['POST'])
def echo(dds_item):

    #data received from post request.
    data = request.get_json()

    #Sends to DDS_Write
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)




# 42 functions
    #one function for HTTP send data (have publisher + topic within function)
    #one function to receive HTTP data(so have a callback, webhook to receive data using subscriber)
