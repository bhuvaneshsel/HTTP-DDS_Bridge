import sys
sys.path.append("./build")  # Adjust path if needed

import ddspython

pub = ddspython.APublisher()
if pub.init():
    print("INITIALIZED")
    pub.set_data()  # placeholder
    if pub.publish():
        print("Published")
    else:
        print("No subscribers matched")
else:
    print("Failed to initialize publisher")