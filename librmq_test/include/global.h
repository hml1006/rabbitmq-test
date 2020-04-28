
#ifndef STAT_H
#define STAT_H

#include <mutex>
#include <string>
#include <vector>
#include <map>
#include <iostream>

using namespace std;

enum Role {
    ALL, // 既是生产者又是消费者
    PRODUCTOR, // 生产者
    CONSUMER, // 消费者
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
        this->productor_rate = 0;
        
        this->message_size = 20;
        this->productor_number = 1;
        this->consumer_number = 1;
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
        cout << "rote: \t" << this->role << endl;
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
        if (this->productor_rate > 0)
        {
            cout << "productor rate:\t" << this->productor_rate << endl;
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
        cout << "productor num:\t" << this->productor_number << endl;
        cout << "consumer num:\t" << this->consumer_number << endl;
        cout << "amqp url:\t" << this->amqp_url << endl;
    }
    
public:
    Role role; // 角色
    
    string task_id; // 任务名称
    int run_duration; // 任务执行时间
    int close_timeout; // 关闭超时时间
    string exchange; // exchange名称
    string routing_key; // routing-key
    bool auto_ack; // auto ack
    int multi_ack;
    bool persistent; // 消息持久化
    int prefetch; 
    int consumer_rate; // 消费者速率
    int productor_rate; // 生产者速率
    vector<VariableRate> vr; // 可变生产者速率
    map<string, string> messsage_properties; // 消息属性
    int message_size; // 消息大小
    vector<VariableSize> vs; // 可变消息大小
    string queue_name;
    int productor_number;
    int consumer_number;
    string queue_name_pattern;
    int queue_name_from;
    int queue_name_to;
    string amqp_url;
};

// 全局统计信息
class GlobalStat
{
public:
    inline void inc_sent() {
        lock_guard<mutex> lk(lock);
        sent++;
    }
    
    inline void inc_received() 
    {
        lock_guard<mutex> lk(lock);
        received++;
    }

public:
    static inline GlobalStat *get_instance()
    {
        if (GlobalStat::s_instance == nullptr)
        {
            GlobalStat::s_instance = new GlobalStat();
        }
        return GlobalStat::s_instance;
    }
    
private:
    static GlobalStat *s_instance;
    
private:
    GlobalStat()
    {
        sent = 0;
        received = 0;
        latency_min = 0;
        latency_median = 0;
        latency_75th = 0;
        latency_95th = 0;
        latency_99th = 0;
    }
    
private:
    mutex lock;
    
    // 已发送消息数
    int sent;
    // 已接收消息数
    int received;
    // 延迟
    int latency_min;
    int latency_median;
    int latency_75th;
    int latency_95th;
    int latency_99th;
};
#endif /* STAT_H */

