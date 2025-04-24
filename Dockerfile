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

# 7. Add fastddsgen if needed
# Optional: COPY fastddsgen into /opt if you want code generation

# 8. Copy your project
WORKDIR /workspace
COPY . /workspace

# 9. Default command
CMD [ "bash" ]
