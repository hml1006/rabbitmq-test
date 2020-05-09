#include "global.h"
#include <iostream>
#include <cstring>

using namespace std;

GlobalConfig *GlobalConfig::s_instance = nullptr;

static ThreadStatPerSecond **s_thread_stat_list = NULL;

int init_global_thread_stat(int run_duration)
{
    s_thread_stat_list = new ThreadStatPerSecond*[run_duration];
    if (s_thread_stat_list == NULL)
    {
        cout << "alloc thread stat pointer array failed" << endl;
        return -1;
    }

    memset(s_thread_stat_list, 0, run_duration * sizeof(ThreadStatPerSecond *));

    return 0;
}

ThreadStatPerSecond **get_global_thread_stat()
{
    return s_thread_stat_list;
}