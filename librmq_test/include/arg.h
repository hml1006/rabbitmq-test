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
    QueueInfo()
    {
        consumers = 0;
        productors = 0;
    }
    void print()
    {
        cout << "queue: " << this->queue << "  productors: " << this->productors << " consumers: " << this->consumers << endl;
    }
};

struct ThreadArg
{
    int cpu;
    // 队列信息
    vector<QueueInfo> queues;

public:
    ThreadArg(int cpu, vector<QueueInfo> queues):
        cpu(cpu), queues(queues)
    {}

    void print()
    {
        for (size_t i = 0; i < this->queues.size(); i++)
        {
            queues[i].print();
        }
    }
};

#endif /* ARG_H */