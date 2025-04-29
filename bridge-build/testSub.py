import sys
import threading
import asyncio
import json
import time

sys.path.append("./bridge-build")  # Adjust path if needed


import ddspython


#Simple documentation how to run sub code.



sub = ddspython.BSubscriber()





#sub.init(): creates the subscriber and all its components. 
if sub.init():
    #sub.run(): runs the subscriber and listens for publisher then listens for any data.
    sub.run()

    #calls the method to get json_data: SHOULD return JSON if matches publisher AND publisher sends data.
        #If don't match publisher OR publisher doesn't send data, should send {"Data": "None"}, however doesn't work I think.
    print(sub.get_json_data())
else:
    print("Didn't initialize subscriber.")

