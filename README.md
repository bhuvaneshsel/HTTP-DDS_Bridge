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
extern/fastddsgen/gradlew
Dockerfile
extern/fastddsgen/scripts/fastddsgen

## 4. Build Docker container:**
In root of project run:
>docker-compose up --build

*If something goes wrong with build and you want to start fresh:*
*>docker-compose build --no-cache*
*>docker-compose up --build*

In another terminal, in root of project run:
>docker-compose exec dds bash

## 5 Set up project in container and virtual environment
>tmux
Make sure you are in /workspace directory:
>python3 -m venv .venv
>source .venv/bin/activate
>pip install -r requirements.txt

*Note that everytime you open up a new tmux pane you have to reactive the virtual environment

Build fastddsgen:
>cd extern/fastddsgen
>./gradlew assemble


>cd /workspace/bridge-src
>python3 generate_code.py
>cd ../bridge-build
>cmake ..
>cmake --build .
>python3 main.py

In another pane in tmux:
>cd demo-pub-sub/demo-build
>cmake ..
>cmake --build .
>./DemoSubscriber OR ./DemoPublisher

Use postman. For GET requests, run ./DemoPublisher. For POST requests, run ./DemoSubscriber

## TMUX Controls
Ctrl + B followed by % to open a new vertical pane
Ctrl + B followed by " to open up a new horizontal pane
Ctrl + B followed by arrow keys to switch between panes
