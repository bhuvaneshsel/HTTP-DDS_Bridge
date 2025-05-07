import sys
import threading
import asyncio
import json


sys.path.append("./bridge-build")  # Adjust path if needed

#import subscriber pybind file?
import ddspython



pub = ddspython.BPublisher()
if pub.init():
    print("INITIALIZED")

    json_b = '''
    {
    "aVal": { "x": 1.23e4, "y": true },
    "b": [4, 5, 6],
    "c": ["foo", "bar"]
    }
    '''
    dict_b = json.loads(json_b)


    pub.set_data(dict_b)  
    if pub.publish():
        print("Published")
    else:
        print("No subscribers matched")
else:
    print("Failed to initialize publisher")
#-------------------------------------------------------------------------------------------------------------------------------------------------

#@app.route('/get_json_data', methods=['GET'])
async def get_json_data():
    #Makes a thread if not async (allows other http requests to be received?)
    #Makes subscriber, runs subscriber. 
        #subscriber then blocks? until data is received? --> once receive JSON data is made.

    #Call get JSON data.

    #return json data.
    pass