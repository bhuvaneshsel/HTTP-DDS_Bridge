// Copyright 2016 Proyectos y Sistemas de Mantenimiento SL (eProsima).
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

/**
 * @file TestPublisher.cpp
 *
 */

//TestPubSubTypes.hpp contains the logic for serializing and deserialzing the DDS data type
#include "TestPubSubTypes.hpp"

#include <chrono>
#include <thread>

#include <fastdds/dds/domain/DomainParticipant.hpp> //Domain Participant is the container that holds DDS publisher, subscriber, topics, etc.
#include <fastdds/dds/domain/DomainParticipantFactory.hpp> //used to create and destroy Domain Participants
#include <fastdds/dds/publisher/DataWriter.hpp> //writes data to the topic
#include <fastdds/dds/publisher/DataWriterListener.hpp> //allows user to implement callbacks from DataWriter, optional
#include <fastdds/dds/publisher/Publisher.hpp> //mangages DateWriter objects, does not actually write the data to the topic
#include <fastdds/dds/topic/TypeSupport.hpp> //manages the custom defined data type?


using namespace eprosima::fastdds::dds;


class TestPublisher
{
private: //defines all private variables

    Test test_; //UPDATE THIS BASED ON IDL DEFINITION

    DomainParticipant* participant_;

    Publisher* publisher_;

    Topic* topic_;

    DataWriter* writer_;

    TypeSupport type_;

    class PubListener : public DataWriterListener //PubListener class inherits from DataWriterListener
    {
    public:

        //constructor that initializes matched = 0
        PubListener() 
            : matched_(0)
        {
        }

        //destructor, called when the object is destroyed (doesn't do anything right now)
        ~PubListener() override
        {
        }

        //callback function that runs when a new DataReader is detected listening to the topic that DataWrtier is publishing to
        void on_publication_matched(
                DataWriter*,
                const PublicationMatchedStatus& info) override
        {
            //new DataWriter has matched, increment total count which is the # of DataWriters connected to the Topic
            if (info.current_count_change == 1)
            {
                matched_ = info.total_count;
                std::cout << "Publisher matched." << std::endl;
            }
            //DataWriter disconnected
            else if (info.current_count_change == -1)
            {
                matched_ = info.total_count;
                std::cout << "Publisher unmatched." << std::endl;
            }
            //Error/Catch all
            else
            {
                std::cout << info.current_count_change
                        << " is not a valid value for PublicationMatchedStatus current count change." << std::endl;
            }
        }

        std::atomic_int matched_; //variable that tracks number of currently connected subscribers

    } listener_;

public:

    //constructor
    TestPublisher()
        : participant_(nullptr)
        , publisher_(nullptr)
        , topic_(nullptr)
        , writer_(nullptr)
        , type_(new TestPubSubType())
    {
    }
    //destructor
    virtual ~TestPublisher()
    {
        if (writer_ != nullptr)
        {
            publisher_->delete_datawriter(writer_);
        }
        if (publisher_ != nullptr)
        {
            participant_->delete_publisher(publisher_);
        }
        if (topic_ != nullptr)
        {
            participant_->delete_topic(topic_);
        }
        DomainParticipantFactory::get_instance()->delete_participant(participant_);
    }

    //!Initialize the publisher
    bool init()
    {
        //UPDATE THIS BASED ON IDL DEFINITION | sets initial values of data sample
        test_.index(0);
        test_.message("Test");

        //creates DomainParticipant
        DomainParticipantQos participantQos;
        participantQos.name("Participant_publisher");
        participant_ = DomainParticipantFactory::get_instance()->create_participant(0, participantQos);

        if (participant_ == nullptr)
        {
            return false;
        }

        // Register the Type
        type_.register_type(participant_);

        // Create the publications Topic, name and type must match on subscriber side
        topic_ = participant_->create_topic("TestTopic", "Test", TOPIC_QOS_DEFAULT);

        if (topic_ == nullptr)
        {
            return false;
        }

        // Create the Publisher, does not send data
        publisher_ = participant_->create_publisher(PUBLISHER_QOS_DEFAULT, nullptr);

        if (publisher_ == nullptr)
        {
            return false;
        }

        // Create the DataWriter, this sends data
        writer_ = publisher_->create_datawriter(topic_, DATAWRITER_QOS_DEFAULT, &listener_);

        if (writer_ == nullptr)
        {
            return false;
        }
        return true;
    }

    void set_data(uint32_t index, const std::string& message)
    {   
        test_.index(index);
        test_.message(message);
    }   

    //!Send a publication
    bool publish()
    {
        //checks if there is a subscriber first
        if (listener_.matched_ > 0)
        {
            test_.index(test_.index() + 1);
            writer_->write(&test_); //publishes data to topic
            return true;
        }
        return false;
    }

    //!Run the Publisher
    void run()
    {
        if (publish())
            {
                std::cout << "Message: " << test_.message() << " with index: " << test_.index()
                            << " SENT" << std::endl;
            }
            else
            {
                std::cout << "No subscribers matched." << std::endl;
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(1000));
    }
};


int main(
        int argc,
        char** argv)
{
    std::cout << "Starting publisher." << std::endl;

    TestPublisher* mypub = new TestPublisher();
    if(mypub->init())
    {
        mypub->run();
    }

    delete mypub;
    return 0;
}

#ifdef BUILD_PYBIND_MODULE
    #include <pybind11/pybind11.h>
    namespace py = pybind11;

    PYBIND11_MODULE(ddspython, m) {
        m.doc() = "DDS publisher";

        py::class_<TestPublisher>(m, "TestPublisher")
        .def(py::init<>())                      // Expose the constructor
        .def("init", &TestPublisher::init)      // Bind the init() method
        .def("publish", &TestPublisher::publish) //Bind the publish() method
        .def("set_data", &TestPublisher::set_data) //Bind the set_data() method
        .def("run", &TestPublisher::run);  //Bind the run() method
}
#endif