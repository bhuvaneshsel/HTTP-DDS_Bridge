import sys
sys.path.append("./bridge-build")  # Adjust path if needed

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