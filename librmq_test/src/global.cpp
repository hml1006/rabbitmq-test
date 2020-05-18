#include "global.h"

#include <ctime>
#include <pthread.h>
#include <mutex>

using namespace std;

GlobalConfig *GlobalConfig::s_instance = nullptr;

// 总mq线程数
static size_t s_mq_thread_num = 0;
// 全部线程统计数据
static unordered_map<pthread_t, shared_ptr<ThreadGlobal>> s_thread_stats;
// 初始化锁
static mutex s_thread_stats_mutex;
// 初始化线程数
static size_t s_mq_thread_init_num = 0;

static time_t s_start_time = 0;

void init_mq_thread_num(int thread_num)
{
    s_mq_thread_num = thread_num;
}

size_t get_mq_thread_num()
{
    return s_mq_thread_num;
}

size_t get_inited_mq_thread_num()
{
    return s_mq_thread_init_num;
}

// 添加线程统计
void add_thread_stat(pthread_t tid, shared_ptr<ThreadGlobal> thread_global)
{
    // 加锁
    lock_guard<mutex> lock(s_thread_stats_mutex);
    cout << "add thread stat, tid: " << tid << " stat: " << thread_global << endl;
    s_thread_stats.insert(pair<pthread_t, shared_ptr<ThreadGlobal>>(tid, thread_global));

    // 增加已经初始化的mq线程数量
    s_mq_thread_init_num++;
    cout << "[add_thread_stat] thread inited: " << s_mq_thread_init_num << endl;
}

// 查找线程统计数据
shared_ptr<ThreadGlobal> get_thread_stat(pthread_t tid)
{
    // 加锁
    lock_guard<mutex> lock(s_thread_stats_mutex);
    auto it = s_thread_stats.find(tid);
    if (it == s_thread_stats.end())
    {
        cout << "[get_thread_stat] nullptr, tid: " << tid << endl;
        return nullptr;
    }
    return s_thread_stats[tid];
}

// 获取全部线程统计数据
unordered_map<pthread_t, shared_ptr<ThreadGlobal>> &
get_all_thread_stat()
{
    return s_thread_stats;
}

time_t get_start_time()
{
    if (s_start_time == 0)
    {
        s_start_time = time(NULL);
    }
    return s_start_time;
}