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
    int consumers;
    int productors;

public:
    void print()
    {
        cout << "queue: " << this->queue << "  productors: " << this->productors << " consumers: " << this->consumers << endl;
    }
};

struct ThreadArg
{
    int cpu; // cpu 核心编号
    // 角色
    Role role;
    // 队列信息
    vector<QueueInfo> queues;

public:
    ThreadArg(int cpu, Role role, vector<QueueInfo> queues):
        cpu(cpu), role(role), queues(queues)
    {}

    void print()
    {
        cout << "thread args， core =>" << this->cpu << endl;
        switch (this->role)
        {
        case Role::PRODUCTOR_ROLE:
            cout << "role: productor" << endl;
            break;
        case Role::CONSUMER_ROLE:
            cout << "role: consumer" << endl;
            break;
        case Role::ALL:
            cout << "role: all" << endl;
            break;
        default:
            break;
        }

        for (size_t i = 0; i < this->queues.size(); i++)
        {
            queues[i].print();
        }
    }
};

#endif /* ARG_H */