FROM ubuntu:22.04

# 1. Install dependencies
RUN apt-get update && apt-get install -y \
    git cmake g++ wget curl \
    python3 python3-pip \
    openjdk-11-jdk \
    libssl-dev \
    libasio-dev \
    libtinyxml2-dev \
    libpugixml-dev \
    libfoonathan-memory-dev \
    build-essential \
    ca-certificates \
    # Ensure nlohmann_json is installed
    nlohmann-json3-dev \
    tmux

# 2. Set up workspace
WORKDIR /opt

# 3. Clone Fast DDS and dependencies
RUN git clone --recursive https://github.com/eProsima/Fast-DDS.git && \
    git clone https://github.com/eProsima/Fast-CDR.git

# 4. Build and install Fast-CDR
RUN mkdir -p Fast-CDR/build && cd Fast-CDR/build && \
    cmake .. && \
    make -j$(nproc) && make install

# 5. Build and install Fast-DDS
RUN mkdir -p Fast-DDS/build && cd Fast-DDS/build && \
    cmake .. && \
    make -j$(nproc) && make install

# 6. Install pybind11 via pip
RUN pip3 install pybind11

# 7. Copy your project
WORKDIR /workspace
COPY . /workspace

# 8. Build fastddsgen
WORKDIR /workspace/extern/fastddsgen
RUN ./gradlew assemble

# 9. Default command
WORKDIR /workspace
CMD [ "bash" ]
