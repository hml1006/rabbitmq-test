
#ifndef GLOBAL_H
#define GLOBAL_H

#include <mutex>
#include <string>
#include <vector>
#include <map>
#include <iostream>
#include <memory>
#include <unordered_map>

#include "amqp_util.h"

using namespace std;

// 默认每个线程每秒只能处理10万条消息
#define MAX_RECEIVE_MSGS_PER_THREAD 100000

// 每组缓存消息条数
#define DEFAULT_MSG_CACHE_QUEUE_SIZE 1000

enum Role {
    ALL, // 既是生产者又是消费者
    PRODUCER_ROLE, // 生产者
    CONSUMER_ROLE, // 消费者
};


class MqInfo 
{
public:
    MqInfo(string queue, amqp_connection_state_t connection)
    {
        this->connection = connection;
        this->queue = queue;
        this->msg_queue = nullptr;
    }

    ~MqInfo()
    {
        mq_deinit(this->msg_queue.get());
    }

    void set_msg_queue(shared_ptr<MQ> msgQueue)
    {
        this->msg_queue = msgQueue;
        mq_init(this->msg_queue.get());
    }

    void set_amqp_connection(amqp_connection_state_t connection)
    {
        this->connection = connection;
    }

    amqp_connection_state_t get_amqp_connection()
    {
        return this->connection;
    }

    Role get_role()
    {
        return this->role;
    }
private:
    string queue;
    Role role;
    amqp_connection_state_t connection;
    shared_ptr<MQ> msg_queue;
};

// 可变生产者速率
struct VariableRate {
    int rate;
    int duration;
};

// 可变消息大小
struct VariableSize {
    int size;
    int duration;
};

class GlobalConfig
{
private:
    static GlobalConfig *s_instance;
    GlobalConfig()
    {
        this->role = Role::ALL;
        this->run_duration = 60; // 设置默认测试时长 60秒
        this->close_timeout = 20; // 设置默认等待关闭时间 20秒
        this->auto_ack = true;
        this->multi_ack = 1;
        this->persistent = false;
        this->prefetch = 1;
        this->consumer_rate = 0;
        this->producer_rate = 0;
        
        this->message_size = 20;
        this->producers = 1;
        this->consumers = 1;
        this->queue_name_from = 0;
        this->queue_name_to = 0;
    }
public:
    static inline GlobalConfig *get_instance()
    {
        if (GlobalConfig::s_instance == nullptr)
        {
            GlobalConfig::s_instance = new GlobalConfig();
        }
        return GlobalConfig::s_instance;
    }
    
    void print()
    {
        cout << "role: \t" << this->role << endl;
        cout << "task_id:\t" << this->task_id << endl;
        cout << "run duration:\t" << this->run_duration << endl;
        cout << "exchage:\t" << this->exchange << endl;
        cout << "routing-key:\t" << this->routing_key << endl;
        cout << "persistent:\t" << this->persistent << endl;
        cout << "prefetch:\t" << this->prefetch << endl;
        cout << "auto ack:\t" << this->auto_ack << endl;
        cout << "multi ack:\t" << this->multi_ack << endl;
        cout << "close timeout:\t" << this->close_timeout << endl;
        cout << "consumer rate:\t" << this->consumer_rate << endl;
        
        // 固定速率和可变速率二选一
        if (this->producer_rate > 0)
        {
            cout << "productor rate:\t" << this->producer_rate << endl;
        }
        else 
        {
            cout << "variable rate:\t" << endl;
            for (auto it = this->vr.begin(); it != this->vr.end(); it++)
            {
                cout << "\tduration:\t" << it->duration << endl;
                cout << "\trate:\t" << it->rate << endl;
            }
        }
        // 消息属性
        if (this->messsage_properties.size() > 0)
        {
            cout << "messge properties:\t" << endl;
            for (auto it = this->messsage_properties.begin(); it != this->messsage_properties.end(); it++)
            {
                cout << "\t" << it->first << endl;
                cout << "\t" << it->second << endl;
            }
        }
        if (this->vs.size() > 0)
        {
            cout << "variable size:\t" << endl;
            for (auto it = this->vs.begin(); it != this->vs.end(); it++)
            {
                cout << "\tduration:\t" << it->duration << endl;
                cout << "\tsize:\t" << it->size << endl;
            }
        }
        else
        {
            cout << "message size:\t" << this->message_size << endl;
        }
        if (!this->queue_name.empty())
        {
            cout << "queue:\t" << this->queue_name << endl;
        }
        else
        {
            cout << "queue pattern:\t" << this->queue_name_pattern << endl;
            cout << "queue from:\t" << this->queue_name_from << endl;
            cout << "queue to:\t" << this->queue_name_to << endl;
        }
        cout << "productor num:\t" << this->producers << endl;
        cout << "consumer num:\t" << this->consumers << endl;
        cout << "amqp url:\t" << this->amqp_url << endl;
    }
    
public:
    Role role; // 角色
    
    string task_id; // 任务名称
    int run_duration; // 任务执行时间
    int close_timeout; // 关闭超时时间
    string exchange; // exchange名称
    string routing_key; // routing-key
    bool auto_ack; // auto ack, 消费者
    int multi_ack;  // 消费者每次确认多少条
    bool persistent; // 消息持久化
    int prefetch;   // 有这么多条消息未被消费者ack，生产者停止发送
    int consumer_rate; // 消费者速率
    size_t producer_rate; // 生产者速率
    vector<VariableRate> vr; // 可变生产者速率
    map<string, string> messsage_properties; // 消息属性
    int message_size; // 消息大小
    vector<VariableSize> vs; // 可变消息大小
    string queue_name;
    size_t producers;
    size_t consumers;
    string queue_name_pattern;
    int queue_name_from;
    int queue_name_to;
    string amqp_url;
};

// 整个测试过程中每一秒都有一项
class ThreadStatPerSecond
{
public:
    ThreadStatPerSecond()
    {
        msg_sent = 0;
        msg_received = 0;
        latency_list = vector<int>();
        latency_list.reserve(MAX_RECEIVE_MSGS_PER_THREAD);
    }

public:
    // 这一秒发送消息数
    size_t msg_sent;
    // 这一秒接收消息数
    size_t msg_received;
    // 消息延迟列表
    // 收到的每条消息都会把延迟时间加到列表
    vector<int> latency_list;
};

// 全局线程数据
class ThreadGlobal
{
public:
    ThreadGlobal(size_t secs)
    {
        this->every_sec_stat = vector<shared_ptr<ThreadStatPerSecond>>();
        this->every_sec_stat.reserve(secs);
        for (size_t i = 0; i < secs; i++)
        {
            shared_ptr<ThreadStatPerSecond> ptr(new ThreadStatPerSecond());
            this->every_sec_stat.push_back(ptr);
        }
    }

    shared_ptr<ThreadStatPerSecond> get_sec_stat(int secs)
    {
        if (secs >=0 && secs < (int)this->every_sec_stat.size())
        {
            return this->every_sec_stat[secs];
        }
//        cout << "[get_sec_stat] wronng secs: " << secs << endl;
        return nullptr;
    }
private:
    // 每一秒线程统计数据
    vector<shared_ptr<ThreadStatPerSecond>> every_sec_stat;
};

void init_mq_thread_num(int thread_num);
size_t get_mq_thread_num();
size_t get_inited_mq_thread_num();
void add_thread_stat(pthread_t tid, shared_ptr<ThreadGlobal> thread_global);
shared_ptr<ThreadGlobal> get_thread_stat(pthread_t tid);
unordered_map<pthread_t, shared_ptr<ThreadGlobal>> &get_all_thread_stat();
void init_start_time();
time_t get_start_time();

#endif /* GLOBAL_H */
