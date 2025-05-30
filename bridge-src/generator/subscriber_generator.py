from .idl_parser import parse_structs_with_antlr
import os


def generate_subscriber_cpp(struct_name: str, idl_name: str, output_dir: str, idl_file_name: str):

    all_structs = parse_structs_with_antlr(idl_file_name)
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

    

    class SubListener : public DataReaderListener
    {{
    public:
        std::atomic_int samples_{{0}};

        //Variable to verify if subscriber has matched with publisher (for on_subscription_matched method.)
        std::atomic_int matched_{{0}};

        //Whether we received data or not.
        std::atomic<bool> received_data_{{false}};

        //Actual data we receive from Publisher to listener.
        {struct_name} sample_;

        //Json data that we send to server. Defaults it with no data.
        json json_data = {{ {{"Data", "None"}} }};



        void on_subscription_matched(DataReader*, const SubscriptionMatchedStatus& info) override
        {{
            if (info.current_count_change == 1)
            {{
                //Set timer with variable info.total_count within run()
                matched_ = info.total_count;

                std::cout << \"Subscriber matched.\" << std::endl;
            }}
            else if (info.current_count_change == -1)
            {{
                matched_ = info.total_count;
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

                //Received data to convert to json.
                received_data_ = true;

                // Convert the received data to JSON
                std::cout << "Converted Data" << std::endl;
                json_data = convert_data_to_json();
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

        //UPDATED THIS: ADDED DURABILITY SETTINGS
        DataReaderQos reader_qos = DATAREADER_QOS_DEFAULT;
        reader_qos.durability().kind = TRANSIENT_LOCAL_DURABILITY_QOS;
        reader_qos.reliability().kind = RELIABLE_RELIABILITY_QOS;

        reader_ = subscriber_->create_datareader(topic_, reader_qos, &listener_);
        return reader_ != nullptr;
    }}

    //Activates the subscriber, makes it run in the background essentially, listening for data or trying to match.
    void run()
    {{
        //Stop subscriber once data received or past time limit (to connect and receive data).

        //Retries = how many seconds before timeout if not connected with publisher.
        int retries = 100;
        while (listener_.matched_ == 0 && retries-- > 0)
        {{
            std::cout << "Searching for publisher to match with..." << std::endl;

            std::this_thread::sleep_for(std::chrono::milliseconds(1000));
        }}

        //Retries = seconds to receive JSON data after connecting to publisher.
        retries = 100;
        if(listener_.matched_ == 1){{
            while(!listener_.received_data_ && retries-- > 0){{
            
                // Subscriber has received data, now we can stop
                std::cout << "Awaiting data." << std::endl;
                std::this_thread::sleep_for(std::chrono::milliseconds(1000));
            }}

            //If true, then means data has been received.
            if(listener_.received_data_){{
                std::cout << "Received Data." << std::endl;
            }}else {{
                std::cout << "Didn't receive Data." << std::endl;
            }}

        }}else{{
            std::cout << "Didn't connect to publisher." << std::endl;
        }}

       
        //NOTE: if data wasn't received, get_json_data() will send default data ("Data" : "None").

        std::cout << "Stopping Subscriber." << std::endl;
    }}

    //------------------------------------------------------------------------------------------------------------------
    //Retrieves JSON data we received (and server should call method to retrieve it via pybind)
    //------------------------------------------------------------------------------------------------------------------
    std::string get_json_data() {{
        return listener_.json_data.dump();  // Dump JSON string here
    }}
    //------------------------------------------------------------------------------------------------------------------



}};

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
    print(f"Generated {filename}")

def generate_json_in_subscriber(struct_name, all_structs, indent="        ", dataName="sample_"):
    """
    Generate recursive C++ JSON serialization code.
    """
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

    cpp_code = []
    cpp_code.append(f"{indent}json j;")  # Initialize JSON
    #If statement that returns if no JSON data received.
    cpp_code.append(f"{indent}if (!received_data_){{ ")
    cpp_code.append(f"{indent} j[\"Data\"] = \"None\";")
    cpp_code.append(f"{indent} return j;")
    cpp_code.append(f"{indent} }}")
    

    fields = all_structs.get(struct_name, [])

    for field_type, field_name in fields:
        field_type = field_type.strip()
        cpp_type = idl_to_cpp_cast_map.get(field_type, field_type)

        if field_type.startswith("sequence<"):
            element_type = field_type[len("sequence<"):-1].strip()
            cpp_type = idl_to_cpp_cast_map.get(element_type, element_type)
            cpp_code.append(f"{indent}j[\"{field_name}\"] = {dataName}.{field_name}(); // sequence<{cpp_type}>")

        elif "[" in field_type:
            base_type = field_type.split("[")[0].strip()
            cpp_type = idl_to_cpp_cast_map.get(base_type, base_type)
            cpp_code.append(f"{indent}j[\"{field_name}\"] = {dataName}.{field_name}(); // array<{cpp_type}>")

        elif field_type in all_structs:
            # It's a nested struct -> Recursively serialize it
            nested_var = f"{dataName}.{field_name}()"
            cpp_code.append(f"{indent}{{")  # Open a block for nested struct
            nested_indent = indent + "    "
            cpp_code.append(f"{nested_indent}json nested;")
            nested_code = generate_json_in_subscriber(field_type, all_structs, indent=nested_indent, dataName=nested_var)
            # Skip "json j;" and "return j;" because we're inlining
            for line in nested_code[1:-1]:
                # replace "j" with "nested" to avoid conflicts
                cpp_code.append(line.replace("j", "nested", 1))
            cpp_code.append(f"{nested_indent}j[\"{field_name}\"] = nested;")
            cpp_code.append(f"{indent}}}")

        else:
            # Primitive types
            cpp_code.append(f"{indent}j[\"{field_name}\"] = {dataName}.{field_name}(); // {cpp_type}")

    cpp_code.append(f"{indent}return j;")  # Done

    return cpp_code