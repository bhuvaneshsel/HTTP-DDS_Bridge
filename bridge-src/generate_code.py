import re
import subprocess
from generator.publisher_generator import generate_publisher_cpp
from generator.subscriber_generator import generate_subscriber_cpp
from generator.bindings_generator import generate_bindings_cpp


# Config
FASTDDSGEN_PATH = "/workspace/extern/fastddsgen/scripts/fastddsgen"
IDL_FILENAME = "Sample.idl"
OUTPUT_DIR = "."  

# Extracts struct names from IDL file
def extract_struct_names(idl_path):
    with open(idl_path, 'r') as f:
        content = f.read()
    return re.findall(r'struct\s+(\w+)\s*{', content)

if __name__ == "__main__":

    #Runs Fast-DDS Gen to generate header files for all the structs in the IDL file
    subprocess.run(["/workspace/extern/fastddsgen/scripts/fastddsgen", IDL_FILENAME])

    struct_names = extract_struct_names(IDL_FILENAME)

    #Generate publisher and subscriber for each struct
    for struct_name in struct_names:
        generate_publisher_cpp(struct_name, IDL_FILENAME.replace(".idl", ""), OUTPUT_DIR, IDL_FILENAME)
        generate_subscriber_cpp(struct_name, IDL_FILENAME.replace(".idl", ""), OUTPUT_DIR, IDL_FILENAME)

    #Generate bindings.cpp for all publishers and subscribers
    generate_bindings_cpp(struct_names, OUTPUT_DIR)