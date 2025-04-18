import os
import re
import subprocess

# === CONFIG ===
FASTDDSGEN_PATH = "/Users/bhuvaneshselvaraj/Fast-DDS/src/fastddsgen/scripts/fastddsgen"
IDL_FILENAME = "Sample.idl"
OUTPUT_DIR = "."  # adjust as needed

# === 1. Extract struct names from IDL ===
def extract_struct_names(idl_path):
    with open(idl_path, 'r') as f:
        content = f.read()
    return re.findall(r'struct\s+(\w+)\s*{', content)

# === 2. Generate Publisher App ===
def generate_publisher_cpp(struct_name: str, idl_name: str, output_dir: str):
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

    void set_data()
    {{
        
    }}

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

namespace py = pybind11;

void bind_{struct_name}Publisher(py::module_& m)
{{
    py::class_<{struct_name}Publisher>(m, "{struct_name}Publisher")
        .def(py::init<>())
        .def("init", &{struct_name}Publisher::init)
        .def("publish", &{struct_name}Publisher::publish)
        .def("set_data", &{struct_name}Publisher::set_data)
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

    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"{struct_name}Publisher.cpp")
    with open(filename, 'w') as f:
        f.write(cpp_code)
    print(f"✅ Generated {filename}")

# === 3. Generate Subscriber App ===
def generate_subscriber_cpp(struct_name: str, idl_name: str, output_dir: str):
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
        {struct_name} sample_;

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
            }}
        }}
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
        while (true)
        {{
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        }}
    }}
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


if __name__ == "__main__":
    # Step 1: Run fastddsgen
    subprocess.run([FASTDDSGEN_PATH, IDL_FILENAME])

    # Step 2: Extract struct names
    struct_names = extract_struct_names(IDL_FILENAME)

    # Step 3: Generate publisher for each struct
    for struct_name in struct_names:
        generate_publisher_cpp(struct_name, IDL_FILENAME.replace(".idl", ""), OUTPUT_DIR)
        generate_subscriber_cpp(struct_name, IDL_FILENAME.replace(".idl", ""), OUTPUT_DIR)

    # Step 4: Generate bindings.cpp for all publishers and subscribers
    generate_bindings_cpp(struct_names, OUTPUT_DIR)