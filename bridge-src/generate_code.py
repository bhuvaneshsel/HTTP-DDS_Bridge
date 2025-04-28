import os
import re
import subprocess

# === CONFIG ===
FASTDDSGEN_PATH = "/workspace/extern/fastddsgen/scripts/fastddsgen"
IDL_FILENAME = "Sample.idl"
OUTPUT_DIR = "."  # adjust as needed

# === 1. Extract struct names from IDL ===
def extract_struct_names(idl_path):
    with open(idl_path, 'r') as f:
        content = f.read()
    return re.findall(r'struct\s+(\w+)\s*{', content)

# === 2. Generate Publisher App ===
def generate_publisher_cpp(struct_name: str, idl_name: str, output_dir: str):

    all_structs = extract_struct_fields(IDL_FILENAME)
    set_data_body = "\n".join(generate_set_data_from_dict(struct_name, all_structs))
   
    # Use plain string for placeholder replacement
    cpp_code = f"""// Generated Publisher for struct {struct_name}

#include "{idl_name}PubSubTypes.hpp"

#include <chrono>
#include <thread>
#include <array>
#include <vector>
#include <string>

#include <fastdds/dds/domain/DomainParticipant.hpp>
#include <fastdds/dds/domain/DomainParticipantFactory.hpp>
#include <fastdds/dds/publisher/DataWriter.hpp>
#include <fastdds/dds/publisher/DataWriterListener.hpp>
#include <fastdds/dds/publisher/Publisher.hpp>
#include <fastdds/dds/topic/TypeSupport.hpp>

using namespace eprosima::fastdds::dds;

class {struct_name}Publisher
{{
private:
    {struct_name} sample_;
    DomainParticipant* participant_;
    Publisher* publisher_;
    Topic* topic_;
    DataWriter* writer_;
    TypeSupport type_;

    class PubListener : public DataWriterListener
    {{
    public:
        std::atomic_int matched_{{0}};

        void on_publication_matched(DataWriter*, const PublicationMatchedStatus& info) override
        {{
            if (info.current_count_change == 1)
            {{
                matched_ = info.total_count;
                std::cout << "Publisher matched." << std::endl;
            }}
            else if (info.current_count_change == -1)
            {{
                matched_ = info.total_count;
                std::cout << "Publisher unmatched." << std::endl;
            }}
        }}
    }} listener_;

public:
    {struct_name}Publisher()
        : participant_(nullptr), publisher_(nullptr), topic_(nullptr), writer_(nullptr), type_(new {struct_name}PubSubType())
    {{}}

    ~{struct_name}Publisher()
    {{
        if (writer_) publisher_->delete_datawriter(writer_);
        if (publisher_) participant_->delete_publisher(publisher_);
        if (topic_) participant_->delete_topic(topic_);
        DomainParticipantFactory::get_instance()->delete_participant(participant_);
    }}

    bool init()
    {{
        DomainParticipantQos participantQos;
        participantQos.name("Participant_{struct_name}_pub");
        participant_ = DomainParticipantFactory::get_instance()->create_participant(0, participantQos);

        if (!participant_) return false;
        type_.register_type(participant_);
        topic_ = participant_->create_topic("{struct_name}Topic", "{struct_name}", TOPIC_QOS_DEFAULT);
        if (!topic_) return false;

        publisher_ = participant_->create_publisher(PUBLISHER_QOS_DEFAULT, nullptr);
        if (!publisher_) return false;

        writer_ = publisher_->create_datawriter(topic_, DATAWRITER_QOS_DEFAULT, &listener_);
        return writer_ != nullptr;
    }}
#ifdef BUILD_PYBIND_MODULE
    void set_data(const pybind11::dict& d)
    {{
{set_data_body}
    }}
#endif

    bool publish()
    {{
        int retries = 10;
        while (listener_.matched_ == 0 && retries-- > 0)
        {{
            std::cout << "Waiting for subscriber to match..." << std::endl;
            std::this_thread::sleep_for(std::chrono::milliseconds(500));
        }}

        if (listener_.matched_ > 0)
        {{
            writer_->write(&sample_);
            return true;
        }}
        return false;
    }}

    void run()
    {{
        if (publish())
        {{
            std::cout << "Sample SENT." << std::endl;
        }}
        else
        {{
            std::cout << "No subscribers matched." << std::endl;
        }}
    }}
}};

#ifdef BUILD_PYBIND_MODULE
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/pytypes.h>


namespace py = pybind11;

void bind_{struct_name}Publisher(py::module_& m)
{{
    py::class_<{struct_name}Publisher>(m, "{struct_name}Publisher")
        .def(py::init<>())
        .def("init", &{struct_name}Publisher::init)
        .def("publish", &{struct_name}Publisher::publish)
        .def("set_data", &{struct_name}Publisher::set_data, py::arg("d"))
        .def("run", &{struct_name}Publisher::run);
}}
#endif

#ifndef BUILD_PYBIND_MODULE
int main()
{{
    std::cout << "Starting {struct_name} Publisher..." << std::endl;
    {struct_name}Publisher pub;
    if (pub.init())
    {{
        pub.run();
    }}
    return 0;
}}
#endif
"""

    

    cpp_code = cpp_code.replace("{set_data_body}", set_data_body)

    # Write file
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"{struct_name}Publisher.cpp")
    with open(filename, 'w') as f:
        f.write(cpp_code)
    print(f"✅ Generated {filename}")

# === 3. Generate Subscriber App ===
def generate_subscriber_cpp(struct_name: str, idl_name: str, output_dir: str):

    all_structs = extract_struct_fields(IDL_FILENAME)
    set_json_body = "\n".join(generate_json_in_subscriber(struct_name, all_structs))
    cpp_code = f"""// Generated Subscriber for struct {struct_name}

#include \"{idl_name}PubSubTypes.hpp\"

#include <chrono>
#include <thread>
#include <fastdds/dds/domain/DomainParticipant.hpp>
#include <fastdds/dds/domain/DomainParticipantFactory.hpp>
#include <fastdds/dds/subscriber/DataReader.hpp>
#include <fastdds/dds/subscriber/DataReaderListener.hpp>
#include <fastdds/dds/subscriber/Subscriber.hpp>
#include <fastdds/dds/topic/TypeSupport.hpp>
#include <fastdds/dds/subscriber/qos/DataReaderQos.hpp>
#include <fastdds/dds/subscriber/SampleInfo.hpp>

#include <nlohmann/json.hpp>  // Include the nlohmann JSON library

using json = nlohmann::json;
using namespace eprosima::fastdds::dds;

class {struct_name}Subscriber
{{
private:
    DomainParticipant* participant_;
    Subscriber* subscriber_;
    DataReader* reader_;
    Topic* topic_;
    TypeSupport type_;

    // Flag to indicate if we should stop the subscriber
    std::atomic<bool> stop_subscriber_{{false}};

    class SubListener : public DataReaderListener
    {{
    public:
        std::atomic_int samples_{{0}};

        //Actual data we receive from Publisher to listener.
        {struct_name} sample_;

        //Json data that we send to server.
        json json_data;



        void on_subscription_matched(DataReader*, const SubscriptionMatchedStatus& info) override
        {{
            if (info.current_count_change == 1)
            {{
                std::cout << \"Subscriber matched.\" << std::endl;
            }}
            else if (info.current_count_change == -1)
            {{
                std::cout << \"Subscriber unmatched.\" << std::endl;
            }}
        }}

        void on_data_available(DataReader* reader) override
        {{
            SampleInfo info;
            if (reader->take_next_sample(&sample_, &info) == RETCODE_OK && info.valid_data)
            {{
                samples_++;
                std::cout << \"Message RECEIVED.\" << std::endl;

                //------------------------------------------------------------------------------------------------------------------

                // Convert the received data to JSON
                json_data = convert_data_to_json(sample_);

                 // Set the stop flag to true after receiving data
                stop_subscriber_ = true;
                //------------------------------------------------------------------------------------------------------------------
            }}
        }}
        
        //------------------------------------------------------------------------------------------------------------------
        // Convert the data to JSON.
    json convert_data_to_json()
    {{
            //Remember that: sample_ is the data.
{set_json_body}
    }}
        //------------------------------------------------------------------------------------------------------------------
    }} listener_;





public:
    {struct_name}Subscriber()
        : participant_(nullptr), subscriber_(nullptr), reader_(nullptr), topic_(nullptr), type_(new {struct_name}PubSubType())
    {{}}

    ~{struct_name}Subscriber()
    {{
        if (reader_) subscriber_->delete_datareader(reader_);
        if (topic_) participant_->delete_topic(topic_);
        if (subscriber_) participant_->delete_subscriber(subscriber_);
        DomainParticipantFactory::get_instance()->delete_participant(participant_);
    }}

    bool init()
    {{
        DomainParticipantQos participantQos;
        participantQos.name(\"Participant_{struct_name}_sub\");
        participant_ = DomainParticipantFactory::get_instance()->create_participant(0, participantQos);

        if (!participant_) return false;
        type_.register_type(participant_);
        topic_ = participant_->create_topic(\"{struct_name}Topic\", \"{struct_name}\", TOPIC_QOS_DEFAULT);
        if (!topic_) return false;

        subscriber_ = participant_->create_subscriber(SUBSCRIBER_QOS_DEFAULT, nullptr);
        if (!subscriber_) return false;

        reader_ = subscriber_->create_datareader(topic_, DATAREADER_QOS_DEFAULT, &listener_);
        return reader_ != nullptr;
    }}

    void run()
    {{
        //Stop subscriber once data received.
        while (!stop_subscriber_)
        {{
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        }}

        // Subscriber has received data, now we can stop
        std::cout << "Stopping subscriber after receiving data." << std::endl;
    }}

    //------------------------------------------------------------------------------------------------------------------
    //Retrieves JSON data we received (and server should call method to retrieve it via pybibd.----------------------------------------------------------------------------------------------------------------------------------
        // Expose the method that returns JSON data

    nlohmann::json get_json_data() {{
        return listener_.json_data;
    }}
    //------------------------------------------------------------------------------------------------------------------

    //Pybind Code---------------------------------------------------------------------------------------------------------------------------------------
    #ifdef BUILD_PYBIND_MODULE
    #include <pybind11/pybind11.h>
    #include <pybind11/stl.h>
    #include <pybind11/pytypes.h>

    namespace py = pybind11;
    void bind_{struct_name}Subscriber(py::module_& m)
    {{
        py::class_<{struct_name}Subscriber>(m, "{struct_name}Subscriber")
            .def(py::init<>())
            .def("init", &{struct_name}Subscriber::init)
            .def("get_json_data", &{struct_name}Subscriber::get_json_data)
            .def("run", &{struct_name}Subscriber::run);
    }}
    #endif
    //---------------------------------------------------------------------------------------------------------------------------------------



}};
#ifndef BUILD_PYBIND_MODULE
int main()
{{
    std::cout << \"Starting {struct_name} Subscriber...\" << std::endl;
    {struct_name}Subscriber sub;
    if (sub.init())
    {{
        sub.run();
    }}
    return 0;
}}
#endif
"""

    filename = os.path.join(output_dir, f"{struct_name}Subscriber.cpp")
    with open(filename, 'w') as f:
        f.write(cpp_code)
    print(f"✅ Generated {filename}")

def generate_bindings_cpp(struct_names, output_dir="."):
    lines = [
        "// Auto-generated bindings.cpp",
        "#include <pybind11/pybind11.h>",
    ]

    # Include all publisher/subscriber implementations
    for struct in struct_names:
        lines.append(f'#include "{struct}Publisher.cpp"')
       # lines.append(f'#include "{struct}Subscriber.cpp"')

    lines.append("\nnamespace py = pybind11;")
    lines.append("PYBIND11_MODULE(ddspython, m) {")
    lines.append('    m.doc() = "Unified DDS Python Bindings Module";')

    # Call the binding functions
    for struct in struct_names:
        lines.append(f"    bind_{struct}Publisher(m);")
        #lines.append(f"    bind_{struct}Subscriber(m);")

    lines.append("}")

    # Write to file
    bindings_path = os.path.join(output_dir, "bindings.cpp")
    with open(bindings_path, "w") as f:
        f.write("\n".join(lines))

    print(f"✅ Generated {bindings_path}")

#provides a dictionary with struct names?
def extract_struct_fields(idl_path):
    with open(idl_path, 'r') as f:
        content = f.read()

    struct_defs = re.findall(r'struct\s+(\w+)\s*{([^}]*)}', content)
    structs = {}
    for struct_name, body in struct_defs:
        fields = re.findall(r'(\w+(?:\s+\w+)?(?:<.*?>)?(?:\s*\[.*\])?)\s+(\w+);', body)
        parsed_fields = []
        for t, n in fields:
            parsed_fields.append((t.strip(), n.strip()))
        structs[struct_name] = parsed_fields
    return structs

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Generate C++ code for converting the struct data to JSON based on parsed IDL structs.  (For Subscriber class.)
    #dataName represents the data package in the subscriber, in this case, it's sample_.
def generate_json_in_subscriber(struct_name, all_structs, indent="        ", dataName = "sample_"):
    """
    :param struct_name: The name of the struct to generate conversion for.
    :param all_structs: A dictionary with struct names as keys and a list of (field_type, field_name) tuples.
    :param indent: Indentation to use for the generated code.
    :return: C++ code as a string that converts struct data to JSON.
    """

    # Define a basic IDL to C++ type mapping
    idl_to_cpp_cast_map = {
        "short": "int16_t",
        "unsigned short": "uint16_t",
        "long": "int32_t",
        "unsigned long": "uint32_t",
        "long long": "int64_t",
        "unsigned long long": "uint64_t",
        "float": "float",
        "double": "double",
        "boolean": "bool",
        "char": "char",
        "string": "std::string",
    }

    #remember sample_ is the data
    # Start generating C++ function
    cpp_code = []
    #cpp_code.append(f"{indent}json j;")  # Initialize the json object with proper indentation

    # Get fields for the given struct_name from all_structs
    fields = all_structs.get(struct_name, [])

    # Iterate over fields to generate conversion code
    for field_type, field_name in fields:
        field_type = field_type.strip()
        cpp_type = idl_to_cpp_cast_map.get(field_type, field_type)

        # Handle different field types
        if field_type.startswith("sequence<"):
            # Handle sequences (e.g., sequence<int>)
            element_type = field_type[len("sequence<"):-1].strip()
            cpp_type = idl_to_cpp_cast_map.get(element_type, element_type)
            cpp_code.append(f"{indent}j[\"{field_name}\"] = {dataName}.{field_name}(); // sequence<{cpp_type}>")
        
        elif "[" in field_type:
            # Handle fixed-size arrays (e.g., long[5])
            base_type = field_type.split("[")[0].strip()
            cpp_type = idl_to_cpp_cast_map.get(base_type, base_type)
            cpp_code.append(f"{indent}j[\"{field_name}\"] = {dataName}.{field_name}(); // array<{cpp_type}>")
        
        else:
            # Handle basic scalar types (int, float, etc.)
            cpp_code.append(f"{indent}j[\"{field_name}\"] = {dataName}.{field_name}(); // {cpp_type}")
    
    cpp_code.append(f"{indent}return j;")  # Ensure proper indentation for the return statement

    # Now we join the code with proper line breaks and return a single formatted string
    
    for line in cpp_code:
        print(line)
    # formatted_code = "\n".join(cpp_code)
    
    return cpp_code

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def generate_set_data_from_dict(struct_name, all_structs, indent="        ", var_name="sample_"):
    lines = []
    fields = all_structs.get(struct_name, [])

    lines.append(f"{indent}using namespace pybind11::literals;")

    # IDL to C++ cast mapping
    idl_to_cpp_cast_map = {
        "short": "int16_t",
        "unsigned short": "uint16_t",
        "long": "int32_t",
        "unsigned long": "uint32_t",
        "long long": "int64_t",
        "unsigned long long": "uint64_t",
        "float": "float",
        "double": "double",
        "boolean": "bool",
        "char": "char",
        "string": "std::string",
        # Add more as needed
    }

    for field_type, field_name in fields:
        field_type = field_type.strip()

        if field_type.startswith("sequence<"):
            # Extract element type from sequence<...>
            element_type = field_type[len("sequence<"):-1].strip()
            cpp_type = idl_to_cpp_cast_map.get(element_type, element_type)
            lines.append(f'{indent}if (d.contains("{field_name}"))')
            lines.append(f'{indent}    {var_name}.{field_name}() = d["{field_name}"].cast<std::vector<{cpp_type}>>();')

        elif "[" in field_type:
            # Handle fixed-size arrays like short[3]
            base_type = field_type.split("[")[0].strip()
            cpp_type = idl_to_cpp_cast_map.get(base_type, base_type)
            lines.append(f'{indent}if (d.contains("{field_name}")) {{')
            lines.append(f'{indent}    auto tmp = d["{field_name}"].cast<std::vector<{cpp_type}>>();')
            lines.append(f'{indent}    std::copy(tmp.begin(), tmp.end(), {var_name}.{field_name}().begin());')
            lines.append(f'{indent}}}')

        elif field_type in all_structs:
            # Handle nested struct!
            nested_var_name = f"{var_name}.{field_name}()"  # Accessor to nested struct
            lines.append(f'{indent}if (d.contains("{field_name}")) {{')
            lines.append(f'{indent}    auto nested_dict = d["{field_name}"].cast<pybind11::dict>();')
            lines.extend(generate_set_data_from_dict(field_type, all_structs, indent + "    ", nested_var_name))
            lines.append(f'{indent}}}')

        else:
            # Scalar types
            cpp_type = idl_to_cpp_cast_map.get(field_type, field_type)
            lines.append(f'{indent}if (d.contains("{field_name}"))')
            lines.append(f'{indent}    {var_name}.{field_name}(d["{field_name}"].cast<{cpp_type}>());')

    return lines

if __name__ == "__main__":
    # Step 1: Run fastddsgen
    #subprocess.run([FASTDDSGEN_PATH, IDL_FILENAME])
    #subprocess.run(["java", "-jar", FASTDDSGEN_PATH, IDL_FILENAME])
    subprocess.run(["/workspace/extern/fastddsgen/scripts/fastddsgen", IDL_FILENAME])



    # Step 2: Extract struct names
    struct_names = extract_struct_names(IDL_FILENAME)

    # Step 3: Generate publisher for each struct
    for struct_name in struct_names:
        generate_publisher_cpp(struct_name, IDL_FILENAME.replace(".idl", ""), OUTPUT_DIR)
        generate_subscriber_cpp(struct_name, IDL_FILENAME.replace(".idl", ""), OUTPUT_DIR)

    # Step 4: Generate bindings.cpp for all publishers and subscribers
    generate_bindings_cpp(struct_names, OUTPUT_DIR)