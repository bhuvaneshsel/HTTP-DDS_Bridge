import sys
import threading
import asyncio

sys.path.append("./bridge-build")  # Adjust path if needed

#import subscriber pybind file?
import ddspython

pub = ddspython.APublisher()
if pub.init():
    print("INITIALIZED")

    data_dict = {
        "x": 42.5,     # example float
        "y": True      # example boolean
    }

    pub.set_data(data_dict)  
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