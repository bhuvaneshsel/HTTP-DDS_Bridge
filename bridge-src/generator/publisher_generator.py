from .idl_parser import parse_structs_with_antlr
import os

def generate_publisher_cpp(struct_name: str, idl_name: str, output_dir: str, idl_file_name: str):

    all_structs =  parse_structs_with_antlr(idl_file_name)
    set_data_body = "\n".join(generate_set_data_from_dict(struct_name, all_structs, dict_name="d"))
   
    # Use plain string for placeholder replacement
    cpp_code = f"""

// Generated Publisher for struct {struct_name}

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

        DataWriterQos writer_qos = DATAWRITER_QOS_DEFAULT;
        writer_qos.durability().kind = TRANSIENT_LOCAL_DURABILITY_QOS;
        writer_qos.reliability().kind = RELIABLE_RELIABILITY_QOS;
    
        writer_ = publisher_->create_datawriter(topic_, writer_qos, &listener_);
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
        int retries = 100;
        while (listener_.matched_ == 0 && retries-- > 0)
        {{
            std::cout << "Waiting for subscriber to match..." << std::endl;
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        }}
    
        if (listener_.matched_ > 0)
        {{
            std::cout << "Subscriber matched. Writing sample..." << std::endl;
            writer_->write(&sample_);
            return true;
        }}
        std::cerr << "No subscribers matched after retries." << std::endl;
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
    print(f"Generated {filename}")

def generate_set_data_from_dict(struct_name, all_structs, indent="        ", var_name="sample_", dict_name="d"):
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
    }

    for field_type, field_name in fields:
        field_type = field_type.strip()

        if field_type.startswith("sequence<"):
            element_type = field_type[len("sequence<"):-1].strip()
            cpp_type = idl_to_cpp_cast_map.get(element_type, element_type)
            lines.append(f'{indent}{var_name}.{field_name}() = {dict_name}["{field_name}"].cast<std::vector<{cpp_type}>>();')

        elif "[" in field_type:
            base_type = field_type.split("[")[0].strip()
            cpp_type = idl_to_cpp_cast_map.get(base_type, base_type)
            lines.append(f'{indent}{{')
            lines.append(f'{indent}    auto tmp = {dict_name}["{field_name}"].cast<std::vector<{cpp_type}>>();')
            lines.append(f'{indent}    std::copy(tmp.begin(), tmp.end(), {var_name}.{field_name}().begin());')
            lines.append(f'{indent}}}')

        elif field_type in all_structs:
            nested_var_name = f"{var_name}.{field_name}()"
            lines.append(f'{indent}{{')
            lines.append(f'{indent}    auto nested_dict = {dict_name}["{field_name}"].cast<pybind11::dict>();')
            lines.extend(generate_set_data_from_dict(field_type, all_structs, indent + "    ", nested_var_name, "nested_dict"))
            lines.append(f'{indent}}}')

        else:
            cpp_type = idl_to_cpp_cast_map.get(field_type, field_type)
            lines.append(f'{indent}{var_name}.{field_name}({dict_name}["{field_name}"].cast<{cpp_type}>());')

    return lines