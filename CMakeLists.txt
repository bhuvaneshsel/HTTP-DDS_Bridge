cmake_minimum_required(VERSION 3.20)

project(dds)

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

message(STATUS "Configuring Test publisher/subscriber example...")
file(GLOB DDS_SAMPLE_SOURCES_CXX "bridge-src/*.cxx")


# === DDS Source files ===
file(GLOB DDS_SAMPLE_SOURCES_CXX "bridge-src/*.cxx")
file(GLOB PUB_FILES "bridge-src/*Publisher.cpp")
file(GLOB SUB_FILES "bridge-src/*Subscriber.cpp")
file(GLOB GENERATED_SOURCES
    "bridge-src/*PubSubTypes.cxx"
    "bridge-src/*TypeObjectSupport.cxx"
)

# === Publisher Executables ===
foreach(pub ${PUB_FILES})
    get_filename_component(pub_name ${pub} NAME_WE)
    add_executable(${pub_name} ${pub} ${GENERATED_SOURCES})
    target_link_libraries(${pub_name} fastdds fastcdr)
endforeach()

# === Subscriber Executables ===
foreach(sub ${SUB_FILES})
    get_filename_component(sub_name ${sub} NAME_WE)
    add_executable(${sub_name} ${sub} ${GENERATED_SOURCES})
    target_link_libraries(${sub_name} fastdds fastcdr)
endforeach()


# === Pybind11 Module ===   
add_subdirectory(${CMAKE_SOURCE_DIR}/extern/pybind11 extern_pybind11_build)

file(GLOB PYBIND_GENERATED_SOURCES
    bridge-src/*PubSubTypes.cxx
    bridge-src/*TypeObjectSupport.cxx
)

pybind11_add_module(ddspython
    bridge-src/bindings.cpp
    ${PYBIND_GENERATED_SOURCES}
)

target_link_libraries(ddspython PRIVATE fastdds fastcdr)
target_compile_definitions(ddspython PRIVATE BUILD_PYBIND_MODULE)


