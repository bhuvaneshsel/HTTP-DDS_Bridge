// Generated Publisher for struct B

#include "SamplePubSubTypes.hpp"

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

class BPublisher
{
private:
    B sample_;
    DomainParticipant* participant_;
    Publisher* publisher_;
    Topic* topic_;
    DataWriter* writer_;
    TypeSupport type_;

    class PubListener : public DataWriterListener
    {
    public:
        std::atomic_int matched_{0};

        void on_publication_matched(DataWriter*, const PublicationMatchedStatus& info) override
        {
            if (info.current_count_change == 1)
            {
                matched_ = info.total_count;
                std::cout << "Publisher matched." << std::endl;
            }
            else if (info.current_count_change == -1)
            {
                matched_ = info.total_count;
                std::cout << "Publisher unmatched." << std::endl;
            }
        }
    } listener_;

public:
    BPublisher()
        : participant_(nullptr), publisher_(nullptr), topic_(nullptr), writer_(nullptr), type_(new BPubSubType())
    {}

    ~BPublisher()
    {
        if (writer_) publisher_->delete_datawriter(writer_);
        if (publisher_) participant_->delete_publisher(publisher_);
        if (topic_) participant_->delete_topic(topic_);
        DomainParticipantFactory::get_instance()->delete_participant(participant_);
    }

    bool init()
    {
        DomainParticipantQos participantQos;
        participantQos.name("Participant_B_pub");
        participant_ = DomainParticipantFactory::get_instance()->create_participant(0, participantQos);

        if (!participant_) return false;
        type_.register_type(participant_);
        topic_ = participant_->create_topic("BTopic", "B", TOPIC_QOS_DEFAULT);
        if (!topic_) return false;

        publisher_ = participant_->create_publisher(PUBLISHER_QOS_DEFAULT, nullptr);
        if (!publisher_) return false;

        DataWriterQos writer_qos = DATAWRITER_QOS_DEFAULT;
        writer_qos.durability().kind = TRANSIENT_LOCAL_DURABILITY_QOS;
        writer_qos.reliability().kind = RELIABLE_RELIABILITY_QOS;
    
        writer_ = publisher_->create_datawriter(topic_, writer_qos, &listener_);
        return writer_ != nullptr;
    }

    bool publish()
    {
        if (listener_.matched_ > 0)
        {
            sample_.aVal().x(5.0f);
            sample_.aVal().y(false);
            
            sample_.b()[0] = 10;
            sample_.b()[1] = 20;
            sample_.b()[2] = 30;

            sample_.c() = std::vector<std::string>{"one", "two", "three"};

            writer_->write(&sample_);
            return true;
        }
        return false;
    }

    void run()
    {
        uint32_t samples = 1;
        uint32_t samples_sent = 0;
        while (samples_sent < samples)
        {
            if (publish())
            {
                samples_sent++;
                std::cout << "SAMPLE SENT" << std::endl;
            }
            else {
                std::cout << "Waiting for subscriber" << std::endl;
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(1000));
        }
    }
};

int main()
{
    std::cout << "Starting B Demo Publisher..." << std::endl;
    BPublisher pub;
    if (pub.init())
    {
        pub.run();
    }
    return 0;
}

