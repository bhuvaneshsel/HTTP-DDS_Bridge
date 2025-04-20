# HTTP-DDS_Bridge 
Andrew Chen, Kevin Hu, Bhuvanesh Selvaraj

HTTP-DDS_Bridge is a bridge application that converts JSON data from an HTTP client to a DDS pub-sub application and vise versa. The application utilizes generated code based on IDL definitions of data types.
- can convert HTTP POST to DDS write
- can convert HTTP GET to DDS read

# Set Up Guide
## 1. Build the DDS App
  1. Create a folder called build inside the dds folder.
  2. Change directory into the build folder and run the commands:
      >cmake .. <br/>
      >cmake --build . <br/>
    *This is for Mac, it might vary for Windows/Linux
## 2. Build the Bridge App
  1. Change directory into the bridge folder and create a virtual environment:
     >Windows: py -3 -m venv .venv  <br/>
     >Windows: .venv\Scripts\activate  <br/>
    
     >Mac: python3 -m venv .venv  <br/>
     >Mac: source .venv/bin/activate  <br/>
  *Note that for Windows, you might run into an error where you don't have permissions to activate the Virtual Environment if you are using the VSCode terminal. In that case, use     command prompt instead.
  2. Install from requirements.txt:<br>
     >Make sure your virtual environment is active<br/>
     >pip install -r requirements.txt<br/>
## 3. Run Both Apps
  1. In the bridge folder with your virtual environment active, run:
     >python main.py
  2. In a different terminal, in your build folder, run:
     >./DDSTestSubscriber
  This will start the Publisher and Subscriber.
## 4. Use PostMan/curl to test
  1. JSON should be in the format
    {
      "index": 10,
      "message": "Test message"
    }
