# HTTP-DDS_Bridge 
Andrew Chen, Kevin Hu, Bhuvanesh Selvaraj

HTTP-DDS_Bridge is a bridge application that converts JSON data from an HTTP client to a DDS pub-sub application and vise versa. The application utilizes generated code based on IDL definitions of data types.
- can convert HTTP POST to DDS write
- can convert HTTP GET to DDS read

# Set Up Guide
## 1. Open docker desktop

## 2. Make sure submodules are up to date
In root of project:
>git submodule update --init --recursive

## 3. Open these files in VSCode and in the bottom right change it from CRLF to LF (for Windows only)
extern/fastddsgen/gradlew <br/>
Dockerfile <br/>
extern/fastddsgen/scripts/fastddsgen <br/>

## 4. Build Docker container:**
In root of project run:
>docker-compose up --build

*If something goes wrong with build and you want to start fresh:* <br/>
>docker-compose build --no-cache <br/>
>docker-compose up --build <br/>

In another terminal, in root of project run: <br/>
>docker-compose exec dds bash <br/>

## 5 Set up project in container and virtual environment
>tmux <br/>

Make sure you are in /workspace directory: <br/>

>python3 -m venv .venv <br/>
>source .venv/bin/activate <br/>
>pip install -r requirements.txt <br/>

*Note that everytime you open up a new tmux pane you have to reactive the virtual environment <br/>

Build fastddsgen: <br/>
>cd extern/fastddsgen <br/>
>./gradlew assemble <br/>


>cd /workspace/bridge-src <br/>
>python3 generate_code.py <br/>
>cd ../bridge-build <br/>
>cmake .. <br/>
>cmake --build . <br/>
>python3 main.py <br/>

In another pane in tmux: <br/>
>cd demo-pub-sub/demo-build <br/>
>cmake .. <br/>
>cmake --build . <br/>
>./DemoSubscriber OR ./DemoPublisher <br/>

Use postman. For GET requests, run ./DemoPublisher. For POST requests, run ./DemoSubscriber <br/>

## TMUX Controls 
Ctrl + B followed by % to open a new vertical pane <br/>
Ctrl + B followed by " to open up a new horizontal pane <br/>
Ctrl + B followed by arrow keys to switch between panes <br/>
