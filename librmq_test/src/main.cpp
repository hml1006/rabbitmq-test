#include <iostream>
#include <unordered_map>
#include <global.h>
#include <string>
#include <regex>
#include <vector>
#include <sys/sysinfo.h>
#include <pthread.h>
#include <sched.h>
#include <unistd.h>
#include <cstdio>
#include <memory>
#include <algorithm>

#include <unistd.h>

#include "cxxopts.hpp"
#include "arg.h"
#include "amqp_util.h"
#include "event.h"

using namespace std;

// 最大队列名长度
#define MAX_QUEUE_NAME_LEN 250

struct SendMsgThreadArg
{
    // event base所在线程
    pthread_t producer_tid;
    // 消息队列列表
    shared_ptr<vector<MQ *>> mq_list;
};

// 解析命令行
void parse(int argc, char* argv[])
{
    try
    {
        // 命令行设置
        cxxopts::Options options(argv[0], "mo_librabbitmq test program");
        options
                .positional_help("[optional args]")
                .show_positional_help();


        options.allow_unrecognised_options()
                .add_options()
                ("d", "task id", cxxopts::value<string>())
                ("z", "run a limit duration", cxxopts::value<int>())
                ("st", "Close timeout", cxxopts::value<int>())
                ("e", "exchange", cxxopts::value<string>())
                ("k", "routing key", cxxopts::value<string>())
                ("a", "auto ack", cxxopts::value<bool>()->default_value("false"))
                ("A", "multi ack", cxxopts::value<int>())
                ("f", "persistent", cxxopts::value<string>())
                ("q", "prefetch number", cxxopts::value<int>())
                ("R", "consumer rate", cxxopts::value<int>())
                ("r", "productor rate", cxxopts::value<int>())
                ("vr", "[RATE]:[DURATION]", cxxopts::value<vector<int>>())
                ("mp", "key1=value1,key2=value2", cxxopts::value<string>())
                ("s", "message size", cxxopts::value<int>())
                ("vs", "[SIZE]:[DURATION]", cxxopts::value<vector<int>>())
                ("u", "queue name", cxxopts::value<string>())
                ("x", "productor number", cxxopts::value<int>())
                ("y", "consumer number", cxxopts::value<int>())
                ("qp", "queue name pattern", cxxopts::value<string>())
                ("qpf", "queue name from", cxxopts::value<int>())
                ("qpt", "queue name to", cxxopts::value<int>())
                ("h", "host url", cxxopts::value<string>())
                ("help", "print help", cxxopts::value<bool>());

        auto result = options.parse(argc, argv);

        if (result.count("help"))
        {
            cout << options.help({"", "Group"}) << endl;
            exit(0);
        }

        GlobalConfig *config = GlobalConfig::get_instance();
        if (config == nullptr)
        {
            cout << "alloc configuration memory failed!" << endl;
            exit(-1);
        }
        if (result.count("d"))
        {
            config->task_id = result["d"].as<string>();
        }
        if (result.count("z"))
        {
            config->run_duration = result["z"].as<int>();
            if (config->run_duration <= 0)
            {
                cout << "run duration must bigger than 0" << endl;
                exit(-1);
            }
        }
        if (result.count("st"))
        {
            config->close_timeout = result["st"].as<int>();
        }
        if (result.count("e"))
        {
            config->exchange = result["e"].as<string>();
        }
        if (result.count("k"))
        {
            config->routing_key = result["k"].as<string>();
        }
        if (result.count("a"))
        {
            config->auto_ack = result["a"].as<bool>();
        }
        if (result.count("A"))
        {
            config->multi_ack = result["A"].as<int>();
        }
        if (result.count("f"))
        {
            if (result["f"].as<string>() == "persistent")
            {
                config->persistent = true;
            }
        }
        if (result.count("q"))
        {
            config->prefetch = result["q"].as<int>();
        }
        if (result.count("R"))
        {
            config->consumer_rate = result["R"].as<int>();
        }
        if (result.count("r"))
        {
            config->producer_rate = (size_t)result["r"].as<int>();
            cout << "****producer rate: " << config->producer_rate << endl;
        }

        if (result.count("vr"))
        {
            vector<int> vals = result["vr"].as<vector<int>>();
            // 必须是 [RATE]:[DURATION] 成对形式
            if (vals.size() % 2 != 0 || vals.size() == 0)
            {
                cout << "vr argument error!" << endl;
                exit(-1);
            }
            // 遍历可变消息
            vector<VariableRate> vec;
            for (size_t i = 0; i < vals.size() - 1; i++)
            {
                VariableRate vs;
                vs.rate = vals[i];
                i++;
                vs.duration = vals[i];
                vec.push_back(vs);
            }
        }
        // 消息属性
        if (result.count("mp"))
        {
            cout << "message properties not support" << endl;
        }

        // 消息大小
        if (result.count("s"))
        {
            config->message_size = result["s"].as<int>();
        }

        // 可变消息大小
        if (result.count("vs"))
        {
            vector<int> vals = result["vs"].as<vector<int>>();
            // 必须是 [SIZE]:[DURATION] 成对形式
            if (vals.size() % 2 != 0 || vals.size() == 0)
            {
                cout << "vs argument error!" << endl;
                exit(-1);
            }
            // 遍历可变消息
            vector<VariableSize> vec;
            for (size_t i = 0; i < vals.size() - 1; i++)
            {
                VariableSize vs;
                vs.size = vals[i];
                i++;
                vs.duration = vals[i];
                vec.push_back(vs);
            }
            config->vs = vec;
        }
        if (result.count("u"))
        {
            config->queue_name = result["u"].as<string>();
            if (config->queue_name.length() > MAX_QUEUE_NAME_LEN)
            {
                cout << "queue name too long, max length is "<< MAX_QUEUE_NAME_LEN << endl;
                exit(-1);
            }
        }
        if (result.count("x"))
        {
            config->producers = result["x"].as<int>();
        }
        if (result.count("y"))
        {
            config->consumers = result["y"].as<int>();
        }
        if (result.count("qp"))
        {
            config->queue_name_pattern = result["qp"].as<string>();
            string sub = "%d";
            size_t index = 0;
            size_t count = 0;
            while ((index = config->queue_name_pattern.find(sub, index)) < config->queue_name_pattern.length())
            {
                count++;
                index++;
            }
            if (count != 1)
            {
                cout << "queue pattern error, should like 'test-queue-%d'" << endl;
                exit(-1);
            }
            if (config->queue_name_pattern.length() > MAX_QUEUE_NAME_LEN)
            {
                cout << "queue pattern too long, max length is " << MAX_QUEUE_NAME_LEN << endl;
                exit(-1);
            }
        }
        if (result.count("qpf"))
        {
            config->queue_name_from = result["qpf"].as<int>();
        }
        if (result.count("qpt"))
        {
            config->queue_name_to = result["qpt"].as<int>();
        }
        // 检查 qpf qpt
        if (config->queue_name_from > config->queue_name_to)
        {
            cout << "qpf should small than qpt" << endl;
            exit(-1);
        }
        if (result.count("h"))
        {
            config->amqp_url = result["h"].as<string>();
            string host, user, password;
            uint16_t port = 0;
            int ret = parse_amqp_uri(config->amqp_url, user, password, host, port);
            if (ret == 0)
            {
                cout << "parse uri success" << endl;
                cout << "host: " << host << " port: " << port << " user: " << user << " password: " << password << endl;
            }
            else
            {
                cout << "uri not match" << endl;
            }
            
        }
        if (config->producers == 0 && config->consumers == 0)
        {
            cout << "productor number and consumer number are zero" << endl;
            exit(-1);
        } else if (config->producers == 0 && config->consumers > 0)
        {
            config->role = Role::CONSUMER_ROLE;
        } else if (config->producers > 0 && config->consumers == 0)
        {
            config->role = Role::PRODUCER_ROLE;
        } else if (config->producers > 0 && config->consumers > 0)
        {
            config->role = Role::ALL;
        }

         config->print();
    }
    catch (const cxxopts::OptionException& e)
    {
        cout << "error parsing options: " << e.what() << endl;
        exit(1);
    }
}

/**
 * 构造队列
 **/
vector<string> make_queues()
{
    vector<string> queues;
    GlobalConfig *config = GlobalConfig::get_instance();

    // 如果设置了 queue name, 则不在用queue pattern
    if (!config->queue_name.empty())
    {
        queues.push_back(config->queue_name);
        return queues;
    }

    // queue pattern
    if (config->queue_name_pattern.empty())
    {
        cout << "qp empty" << endl;
    } 
    else if (config->queue_name_from == config->queue_name_to)
    {
        cout << "qpf should small than qpt" << endl;
    }
    else {
        char queue_name_tmp[MAX_QUEUE_NAME_LEN + 6];
        for (int i = config->queue_name_from; i <= config->queue_name_to; i++)
        {
            snprintf(queue_name_tmp, sizeof(queue_name_tmp), config->queue_name_pattern.c_str(), i);
            queues.push_back(string(queue_name_tmp));
            cout << "queue: " << string(queue_name_tmp) << endl;
        }
    }

    return queues;
}

/**
 * 构造QueueInfo
 **/
vector<ThreadQueueInfo> make_queue_info(vector<string> &queues, size_t cpu_num)
{
    vector<QueueInfo> producers;
    vector<QueueInfo> consumers;
    GlobalConfig *config = GlobalConfig::get_instance();
    producers.reserve(config->producers);
    consumers.reserve(config->consumers);
    if (queues.size() == 0)
    {
        cout << "[make_queue_info] queues empty" << endl;
        exit(-1);
    }
    
    if (cpu_num <= 0)
    {
        cout << "[make_queue_info] cpu num error: " << cpu_num << endl;
        exit(-1);
    }
    
    size_t i = 0;
    // 创建生产者, 循环设置队列
    while (i < config->producers)
    {
        for (size_t j = 0; (j < queues.size() && i < config->producers); j++)
        {
            QueueInfo info(queues[j], Role::PRODUCER_ROLE);
            producers.push_back(info);
            i++;
        }
    }
    i = 0;
    // 创建消费者, 循环设置队列
    while (i < config->consumers)
    {
        for (size_t j = 0; (j < queues.size() && i < config->consumers); j++)
        {
            QueueInfo info(queues[j], Role::CONSUMER_ROLE);
            consumers.push_back(info);
            i++;
        }
    }
    // 初始化线程队列信息
    vector<ThreadQueueInfo> thread_queue;
    for (size_t i = 0; i < cpu_num; i++)
    {
        thread_queue.push_back(ThreadQueueInfo());
    }
    
    // 循环给线程分配生产者
    i = 0;
    for (size_t j = 0; j < config->producers; j++)
    {
        if (i == cpu_num)
        {
            i = 0;
        }
        thread_queue[i].queues.push_back(producers[j]);
        i++;
    }

    // 循环给线程分配消费者
    i = 0;
    for (size_t j = 0; j < config->consumers; j++)
    {
        if (i == cpu_num)
        {
            i = 0;
        }
        thread_queue[i].queues.push_back(consumers[j]);
        i++;
    }
    
    // 清除不存在生产者或者消费者的线程参数
	auto iter = thread_queue.begin();
	while (iter != thread_queue.end())
	{	
        if (iter->queues.size() == 0)
        {
            iter = thread_queue.erase(iter);
        }
		else
        {
            iter++;
        }
	}
    return thread_queue;
}

// 创建线程并绑定cpu
int create_thread(pthread_t &tid, void *(*start_routine) (void *), void *arg)
{
    // 初始化线程属性
    pthread_attr_t att;
    pthread_attr_init(&att);

    // 设置detach
    pthread_attr_setdetachstate(&att, PTHREAD_CREATE_DETACHED);
    
    int ret = pthread_create(&tid, NULL, start_routine, arg);
    if (ret != 0)
    {
        cout << "create pthread failed, errno: " << ret << endl;
        abort();
    }

    return 0;
}

// vector 切片
template<typename T>
vector<T> slice(vector<T> const &v, int m, int n)
{
	auto first = v.cbegin() + m;
	auto last = v.cbegin() + n + 1;

	vector<T> vec(first, last);
	return vec;
}

// 发送一条消息并更新统计
int send_one_msg(MQ *mq, MQ_ITEM *item, shared_ptr<ThreadStatPerSecond> stat)
{
    if (mq == NULL || item == NULL || stat == nullptr)
    {
        return -1;
    }

    // 写入时间戳
    time_t *content = (time_t *)(item->content.bytes);
    struct timeval tv;
    struct timezone tz;
    gettimeofday(&tv, &tz);
    *content = htonl(tv.tv_sec);
    content++;
    *content = htonl(tv.tv_usec);

    // 发送消息并更新统计
    int ret = mq_push(mq, item);
    if (ret == 0)
    {
        stat->msg_sent++;
    }

    return ret;
}

// 消息发送线程函数
void *send_msg_thread_func(void *arg)
{
    shared_ptr<SendMsgThreadArg> thread_arg((SendMsgThreadArg *)arg);
    GlobalConfig *config = GlobalConfig::get_instance();

    shared_ptr<ThreadGlobal> global = get_thread_stat(thread_arg->producer_tid);
    
    cout << "[send_msg_thread_func] send msg for: " << thread_arg->producer_tid << endl;

    while (time(NULL) - get_start_time() <= config->run_duration)
    {
        // 默认速度
        size_t producer_rate = config->producer_rate;
        size_t msg_size = config->message_size;
        // 运行时长
        size_t uptime = time(NULL) - get_start_time();
        // 检查是否区间限速
        if (config->vr.size() > 0)
        {
            size_t rate_duration = 0;
            for (size_t i = 0; i < config->vr.size(); i++)
            {
                rate_duration += config->vr[i].duration;
                if (uptime <= rate_duration)
                {
                    producer_rate = config->vr[i].rate;
                }
            }
        }
        
        if (config->vs.size() > 0)
        {
            size_t size_duration = 0;
            for (size_t i = 0; i < config->vs.size(); i++)
            {
                size_duration += config->vs[i].duration;
                if (uptime <= size_duration)
                {
                    msg_size = config->vs[i].size;
                }
            }
        }

        shared_ptr<ThreadStatPerSecond> stat = global->get_sec_stat(uptime);
        if (stat == nullptr)
        {
            cout << "[send_msg_thread_func] uptime: " << uptime << endl; 
            usleep(100 * 1000);
            continue;
        }
        // 速率检查
        if (producer_rate != 0)
        {
            // 这一秒发送数量 >= 队列速度 × 队列数量, 说明达到了限速
            if (stat->msg_sent >= (producer_rate * thread_arg->mq_list->size()))
            {
                usleep(10 * 1000);
                continue;
            }
        }

        // 每个队列发送一条消息
        for (auto it = thread_arg->mq_list->begin(); it != thread_arg->mq_list->end(); it++)
        {
            MQ_ITEM *item = prepare_msg(msg_size);
            send_one_msg(*it, item, stat);
        }

    }

    return NULL;
}

// 线程函数
void *thread_func(void *arg)
{
    shared_ptr<ThreadArg> thread_arg((ThreadArg *)arg);
    GlobalConfig *config = GlobalConfig::get_instance();
    
    cout << "[thread_func] create mq thread: " << pthread_self() << endl;
    
    // 初始化线程统计
    shared_ptr<ThreadGlobal> global(new ThreadGlobal((size_t)(config->run_duration + config->close_timeout)));
    add_thread_stat(pthread_self(), global);

    event_base *evbase = event_base_new();
    shared_ptr<event_base> base(evbase, [](event_base *base) {
        amqp_destroy_evbase(base);
    });
    vector<MQ *> *mq_list = new vector<MQ *>;
    for (auto it = thread_arg->queue_info.queues.begin(); it != thread_arg->queue_info.queues.end(); it++)
    {
        if (it->role == Role::PRODUCER_ROLE)
        {
            MQ *mq = new MQ;
            mq_list->push_back(mq);
            int ret = create_productor(evbase, config->amqp_url, config->exchange, config->routing_key, mq);
            if (ret != 0)
            {
                cout << "create productor failed, queue: " << it->queue << endl;
            }
        }
        else if (it->role == Role::CONSUMER_ROLE)
        {
            cout << "[thread_func] will create consumers: " << it->queue << endl;
            int ret = create_consumer(evbase, config->amqp_url, config->exchange, it->queue, config->routing_key);
            if (ret != 0)
            {
                cout << "create consumer failed, queue: " << it->queue << endl;
            }
        }
    }

    // 创建消息发送线程
    if (mq_list->size() > 0)
    {
        pthread_t send_msg_thread;
        SendMsgThreadArg *send_msg_thread_arg = new SendMsgThreadArg;
        send_msg_thread_arg->producer_tid = pthread_self();
        send_msg_thread_arg->mq_list = shared_ptr<vector<MQ *>>(mq_list);
        int ret = create_thread(send_msg_thread, send_msg_thread_func, (void *) send_msg_thread_arg);
        if (ret < 0)
        {
            cout << "create send msg thread failed, exiting" << endl;
            exit(-1);
        }
    }

    // 进入事件循环
    amqp_evbase_loop(evbase);

    return NULL;
}

static int s_current_sec = -1;
void print_log()
{
    int run_duration = time(NULL) - get_start_time();
    if (run_duration <= s_current_sec)
    {
        return;
    }
    
    s_current_sec++;
    auto threads_stat = get_all_thread_stat();
    size_t sent = 0;
    size_t received = 0;
    int latency_min = 0;
    int latency_median = 0;
    int latency_75th = 0;
    int latency_95th = 0;
    int latency_99th = 0;
    vector<int> latency_list;
    for (auto it = threads_stat.begin(); it != threads_stat.end(); it++)
    {
        shared_ptr<ThreadGlobal> per_thread = it->second;
        shared_ptr<ThreadStatPerSecond> current_sec = per_thread->get_sec_stat(s_current_sec);
        if (current_sec == nullptr)
        {
            cout << "[print_log] current_sec nullptr: " << s_current_sec << endl;
            return;
        }
        // 合并全部线程的延迟列表
        latency_list.insert(latency_list.end(), current_sec->latency_list.begin(), current_sec->latency_list.end());
        sent += current_sec->msg_sent;
        received += current_sec->msg_received;
    }

    GlobalConfig *config = GlobalConfig::get_instance();
    // 计算延迟
    if (config->role == Role::ALL || config->role == Role::CONSUMER_ROLE)
    {
        // 按照从小到达排序延迟时间
        sort(latency_list.begin(), latency_list.end());
        if (latency_list.size() != 0)
        {
            latency_min = latency_list[0];
            latency_median = latency_list[latency_list.size() * 0.5];
            latency_75th = latency_list[latency_list.size() * 0.75];
            latency_95th = latency_list[latency_list.size() * 0.95];
            latency_99th = latency_list[latency_list.size() * 0.99];
        }
    }

    // id: queuetest2, time: 2.000s, sent: 1001 msg/s, received: 501 msg/s, min/median/75th/95th/99th consumer latency: 447660/696961/821878/921988/941319 µs
    // id: test-134948-252, time: 1.477s, sent: 131940 msg/s
    // id: test-134939-786, time: 11.555s, received: 41666 msg/s, min/median/75th/95th/99th consumer latency: 1637/2060/2270/2386/2407 ms
    if (config->role == Role::ALL)
    {
        cout << "id: " << config->task_id << ", time: " << s_current_sec << "s, sent: " << sent << " msg/s, received: "  \
            << received << "msg/s, min/median/75th/95th/99th consumer latency: " \
            << latency_min << "/" << latency_median << "/" << latency_75th << "/" << latency_95th << "/" << latency_99th << " ms" << endl;

    }
    else if (config->role == Role::CONSUMER_ROLE)
    {
        cout << "id: " << config->task_id << ", time: " << s_current_sec << "s, received: "  \
            << received << "msg/s, min/median/75th/95th/99th consumer latency: " \
            << latency_min << "/" << latency_median << "/" << latency_75th << "/" << latency_95th << "/" << latency_99th << " ms" << endl;
    }
    else
    {
        cout << "id: " << config->task_id << ", time: " << s_current_sec << "s, sent: " << sent << " msg/s" << endl;
    }
}

void main_loop()
{
    GlobalConfig *config = GlobalConfig::get_instance();
    
    int total_secs = config->run_duration + config->close_timeout;
    size_t mq_thread_num = get_mq_thread_num();
    // 循环创建缓存消息
    while (true)
    {
        int run_duration = time(NULL) - get_start_time();
        if (total_secs <= run_duration)
        {
            cout << "[main_loop] total secs: " << total_secs << ", run_duration: " << run_duration << endl;
            break;
        }
        if (mq_thread_num == get_inited_mq_thread_num())
        {
            print_log();
            usleep(500 * 1000);
        }
        else if (mq_thread_num != get_inited_mq_thread_num())
        {
            cout << "thread not init ok, waiting ..." << "total: " << mq_thread_num << ", inited: " << get_inited_mq_thread_num() << endl;
            usleep(500 * 1000);
        }
    }
}

int main(int argc, char* argv[])
{
    parse(argc, argv);

    // 获取cpu核心数
    int cpu_num = get_nprocs_conf();
    cout << "cpu number is " << cpu_num << endl;

    if (cpu_num <= 0)
    {
        cout << "cpu number error: " << cpu_num << endl;
        return -1;
    }

    vector<string> queues = make_queues();
    if (queues.size() == 0)
    {
        cout << "queues empty" << endl;
        return -1;
    }

    // 队列平分生产者和消费者数量, 如果有余数, 把余数分给前面的队列
    // cpu平分生产者和消费者, 循环分配
    vector<ThreadQueueInfo> infos = make_queue_info(queues, (size_t)cpu_num);
    if (infos.size() == 0)
    {
        cout << "make thread queue info failed" << endl;
        return -1;
    }

    // 线程数取cpu核数和队列数的小值
    size_t thread_num = infos.size();
    init_mq_thread_num(thread_num);

    // mq_init会初始化kdvlog, kdvlog初始化函数不能多线程调用
    MQ *mq = new MQ;
    mq_init(mq);
    mq_deinit(mq);
    
//    mq_log_console();
    cout << "will create thread: " << thread_num << endl;
    
    // mq线程列表
    vector<pthread_t> mq_threads;
    // 每个核创建一个线程
    for (size_t i = 0; i < thread_num; i++)
    {
        // 构造线程参数
        ThreadArg *arg = new ThreadArg(infos[i]);
        pthread_t tid;
        cout << "creating thread: " << i << endl;
        int ret = create_thread(tid, thread_func, (void *)arg);
        if (ret < 0)
        {
            cout << "create thread failed, exiting" << endl;
            return -1;
        }
        mq_threads.push_back(tid);
    }
    cout << "will enter main loop !!!!!!!!!!!!!!!!!" << endl;
    main_loop();
    
    // 退出mq线程
    for (auto it = mq_threads.begin(); it != mq_threads.end(); it++)
    {
        pthread_cancel(*it);
    }
    
    usleep(100 * 1000);
    cout << "exiting" << endl;

    return 0;
}
