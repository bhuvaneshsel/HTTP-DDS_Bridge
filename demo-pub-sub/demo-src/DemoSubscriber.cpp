// Generated Subscriber for struct B

#include "SamplePubSubTypes.hpp"

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

class BSubscriber
{
private:
    DomainParticipant* participant_;
    Subscriber* subscriber_;
    DataReader* reader_;
    Topic* topic_;
    TypeSupport type_;

    

    class SubListener : public DataReaderListener
    {
    public:
        std::atomic_int samples_{0};

        //Variable to verify if subscriber has matched with publisher (for on_subscription_matched method.)
        std::atomic_int matched_{0};

        //Whether we received data or not.
        std::atomic<bool> received_data_{false};

        //Actual data we receive from Publisher to listener.
        B sample_;
    



        void on_subscription_matched(DataReader*, const SubscriptionMatchedStatus& info) override
        {
            if (info.current_count_change == 1)
            {
                //Set timer with variable info.total_count within run()
                matched_ = info.total_count;

                std::cout << "Subscriber matched." << std::endl;
            }
            else if (info.current_count_change == -1)
            {
                matched_ = info.total_count;
                std::cout << "Subscriber unmatched." << std::endl;
            }
        }

        void on_data_available(DataReader* reader) override
        {
            SampleInfo info;
            if (reader->take_next_sample(&sample_, &info) == RETCODE_OK && info.valid_data)
            {
                samples_++;
                received_data_ = true;
                std::cout << "Message RECEIVED." << std::endl;

                std::cout << "x: " << sample_.aVal().x()
                        << " | y: " << (sample_.aVal().y() ? "true" : "false")
                        << " | b[0]: " << sample_.b()[0]
                        << " | b[0]: " << sample_.b()[1]
                        << " | b[0]: " << sample_.b()[2]
                        << " | c[0]: " << sample_.c()[0]
                        << " | c[1]: " << sample_.c()[1]
                         << std::endl;
            }
        }
    } listener_;





public:
    BSubscriber()
        : participant_(nullptr), subscriber_(nullptr), reader_(nullptr), topic_(nullptr), type_(new BPubSubType())
    {}

    ~BSubscriber()
    {
        if (reader_) subscriber_->delete_datareader(reader_);
        if (topic_) participant_->delete_topic(topic_);
        if (subscriber_) participant_->delete_subscriber(subscriber_);
        DomainParticipantFactory::get_instance()->delete_participant(participant_);
    }

    bool init()
    {
        DomainParticipantQos participantQos;
        participantQos.name("Participant_B_sub");
        participant_ = DomainParticipantFactory::get_instance()->create_participant(0, participantQos);

        if (!participant_) return false;
        type_.register_type(participant_);
        topic_ = participant_->create_topic("BTopic", "B", TOPIC_QOS_DEFAULT);
        if (!topic_) return false;

        subscriber_ = participant_->create_subscriber(SUBSCRIBER_QOS_DEFAULT, nullptr);
        if (!subscriber_) return false;

        //UPDATED THIS: ADDED DURABILITY SETTINGS
        DataReaderQos reader_qos = DATAREADER_QOS_DEFAULT;
        reader_qos.durability().kind = TRANSIENT_LOCAL_DURABILITY_QOS;
        reader_qos.reliability().kind = RELIABLE_RELIABILITY_QOS;

        reader_ = subscriber_->create_datareader(topic_, reader_qos, &listener_);
        return reader_ != nullptr;
    }

    //Activates the subscriber, makes it run in the background essentially, listening for data or trying to match.
    void run()
    {
        int retries = 100;
        while (listener_.matched_ == 0 && retries-- > 0)
        {
            std::cout << "Searching for publisher to match with..." << std::endl;

            std::this_thread::sleep_for(std::chrono::milliseconds(500));
        }

        retries = 100;
        if(listener_.matched_ == 1){
            while(!listener_.received_data_ && retries-- > 0){
                if (listener_.received_data_) break;

                std::cout << "Awaiting data." << std::endl;
                std::this_thread::sleep_for(std::chrono::milliseconds(500));
            }

            if(listener_.received_data_){
                std::cout << "Received Data." << std::endl;
            }else {
                std::cout << "Didn't receive Data." << std::endl;
            }

        }else{
            std::cout << "Didn't connect to publisher." << std::endl;
        }
        std::cout << "Stopping Subscriber." << std::endl;
    }




};

int main()
{
    std::cout << "Starting B Subscriber..." << std::endl;
    BSubscriber sub;
    if (sub.init())
    {
        sub.run();
    }
    return 0;
}

