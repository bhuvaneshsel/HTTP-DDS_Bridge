cmake_minimum_required(VERSION 3.20)

project(demo-dds)

# Find requirements
if(NOT fastcdr_FOUND)
    find_package(fastcdr 2 REQUIRED)
endif()

if(NOT fastdds_FOUND)
    find_package(fastdds 3 REQUIRED)
endif()

# Set C++11
include(CheckCXXCompilerFlag)
if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_COMPILER_IS_CLANG OR
        CMAKE_CXX_COMPILER_ID MATCHES "Clang")
    check_cxx_compiler_flag(-std=c++11 SUPPORTS_CXX11)
    if(SUPPORTS_CXX11)
        add_compile_options(-std=c++11)
    else()
        message(FATAL_ERROR "Compiler doesn't support C++11")
    endif()
endif()

message(STATUS "Configuring HelloWorld publisher/subscriber example...")
file(GLOB DDS_HELLOWORLD_SOURCES_CXX "demo-src/*.cxx")

# === Publisher Executables ===
add_executable(DemoPublisher demo-src/DemoPublisher.cpp ${DDS_HELLOWORLD_SOURCES_CXX})
target_link_libraries(DemoPublisher fastdds fastcdr)


# === Subscriber Executables ===
add_executable(DemoSubscriber demo-src/DemoSubscriber.cpp ${DDS_HELLOWORLD_SOURCES_CXX})
target_link_libraries(DemoSubscriber fastdds fastcdr)


