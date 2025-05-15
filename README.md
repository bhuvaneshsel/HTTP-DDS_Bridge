# HTTP-DDS_Bridge 
Andrew Chen, Kevin Hu, Bhuvanesh Selvaraj

HTTP-DDS_Bridge is a bridge application that converts JSON data from an HTTP client to a DDS pub-sub application and vise versa. The application utilizes generated code based on IDL definitions of data types.
- can convert HTTP POST to DDS write
- can convert HTTP GET to DDS read

# Installation
1. **Open docker desktop** 
2. **Update submodules**
   
```bash
git submodule update --init --recursive
```

3. **Ensure following files are in LF**


```bash
extern/fastddsgen/gradlew 
Dockerfile 
extern/fastddsgen/scripts/fastddsgen 
```

4. **Build Docker container**

```bash
docker-compose up --build
docker-compose exec dds bash
```
5. **Set up project**

```bash
python3 -m venv .venv 
source .venv/bin/activate
pip install -r requirements.txt 
```

6. **Build fastddsgen**

```bash
cd extern/fastddsgen 
./gradlew assemble 
```

7. **Build bridge**
Customize sample.idl then:
```bash
cd /workspace/bridge-src 
python3 generate_code.py 
cd ../bridge-build 
cmake ..
cmake --build . 
python3 main.py 
```
8. **Build Demo Pub-Sub**
```bash
cd demo-pub-sub/demo-build
cmake .. 
cmake --build . 
./DemoSubscriber OR ./DemoPublisher
```
For GET requests, run ./DemoPublisher. For POST requests, run ./DemoSubscriber 
