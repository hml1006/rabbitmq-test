#ifndef ARG_H
#define ARG_H

#include <vector>
#include <string>

#include "global.h"

using namespace std;

// 队列信息
struct QueueInfo
{
    string queue;
    Role role;

public:
    QueueInfo(string queue, Role role)
    {
        this->queue = queue;
        this->role = role;
    }
    void print()
    {
        string tag;
        if (role == Role::CONSUMER_ROLE)
        {
            tag = "consumer";
        }
        else
        {
            tag = "producer";
        }
        cout << "queue: " << this->queue << "  role: "  << endl;
    }
};

struct ThreadQueueInfo
{
    vector<QueueInfo> queues;
};

struct ThreadArg
{
    // 队列信息
    ThreadQueueInfo queue_info;

public:
    ThreadArg(ThreadQueueInfo queue_info):
        queue_info(queue_info)
    {}
};

#endif /* ARG_H */