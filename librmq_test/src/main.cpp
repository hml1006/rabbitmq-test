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

#include <unistd.h>

#include "cxxopts.hpp"
#include "arg.h"
#include "amqp_util.h"
#include "event.h"

using namespace std;

// 最大队列名长度
#define MAX_QUEUE_NAME_LEN 250

// 拆分字符串
vector<string> str_split(const string& in, const string& delim) {
    regex re{ delim };
    // 调用 vector::vector (InputIterator first, InputIterator last,const allocator_type& alloc = allocator_type())
    // 构造函数,完成字符串分割
    return vector<string> {
        sregex_token_iterator(in.begin(), in.end(), re, -1),
        sregex_token_iterator()
    };
}

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
            config->productor_rate = result["r"].as<int>();
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
            string mp_str = result["mp"].as<string>();
            vector<string> mp = str_split(mp_str, ",");
            if (mp.size() == 0)
            {
                cout << "mp argument error" << endl;
                exit(-1);
            }
            map<string, string> properties;
            for (auto it = mp.begin(); it != mp.end(); ++it)
            {
                vector<string> item = str_split(*it, "=");
                if (item.size() == 2)
                {
                    properties.insert(make_pair(item[0], item[1]));
                }
            }
            if (properties.size() > 0)
            {
                config->messsage_properties = properties;
            }
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
            config->productors = result["x"].as<int>();
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
        if (config->productors < 0 || config->consumers < 0)
        {
            cout << "productor number or consumer number are wrong" << endl;
            exit(-1);
        } else if (config->productors == 0 && config->consumers == 0)
        {
            cout << "productor number and consumer number are zero" << endl;
            exit(-1);
        } else if (config->productors == 0 && config->consumers > 0)
        {
            config->role = Role::CONSUMER_ROLE;
        } else if (config->productors > 0 && config->consumers == 0)
        {
            config->role = Role::PRODUCTOR_ROLE;
        } else if (config->productors > 0 && config->consumers > 0)
        {
            config->role = Role::ALL;
        }

        // config->print();
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
        }
    }

    return queues;
}

/**
 * 构造QueueInfo
 **/
vector<QueueInfo> make_queue_info(vector<string> &queues)
{
    vector<QueueInfo> infos;
    GlobalConfig *config = GlobalConfig::get_instance();
    if (queues.size() == 0)
    {
        cout << "queues empty" << endl;
        return infos;
    }
    if (config->productors < queues.size() || config->consumers < queues.size())
    {
        cout << "consumer number and productor number must bigger than queue number" << endl;
        return infos;
    }

    size_t consumer_per_queue = config->consumers / queues.size();
    size_t productor_per_queue = config->productors / queues.size();

    size_t rest_consumer = config->consumers % queues.size();
    size_t rest_productor = config->productors % queues.size();

    // 设置队列信息
    for (size_t i = 0; i < queues.size(); i++)
    {
        QueueInfo info;
        info.queue = queues[i];
        info.consumers = (i < rest_consumer)? (consumer_per_queue + 1) : consumer_per_queue;
        info.productors = (i < rest_productor)? (productor_per_queue + 1) : productor_per_queue;

        infos.push_back(info);
    }

    return infos;
}

// 创建线程并绑定cpu
int create_thread(pthread_t &tid, int cpu, void *(*start_routine) (void *), void *arg)
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

void *send_msg_thread_func(void *arg)
{
    shared_ptr<vector<MQ *>> mq_list((vector<MQ *> *) arg);

    // TODO 发消息

    return NULL;
}

// 线程函数
void *thread_func(void *arg)
{
    shared_ptr<ThreadArg> thread_arg((ThreadArg *)arg);
    thread_arg->print();
    GlobalConfig *config = GlobalConfig::get_instance();
    
    // 初始化线程统计
    shared_ptr<ThreadGlobal> global(new ThreadGlobal((size_t)(config->run_duration)));
    add_thread_stat(pthread_self(), global);

    event_base *evbase = event_base_new();
    vector<MQ *> *mq_list = new vector<MQ *>;
    for (auto it = thread_arg->queues.begin(); it != thread_arg->queues.end(); it++)
    {
        for (int productors = 0; productors < it->productors; productors++)
        {
            MQ *mq = new MQ;
            mq_list->push_back(mq);
            int ret = create_productor(evbase, config->amqp_url, config->exchange, it->queue, config->routing_key, mq);
            if (ret != 0)
            {
                cout << "create productor failed, queue: " << it->queue << endl;
            }
        }
        for (int consumers = 0; consumers < it->consumers; consumers++)
        {
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
        int ret = create_thread(send_msg_thread, thread_arg->cpu, send_msg_thread_func, (void *) mq_list);
        if (ret < 0)
        {
            cout << "create send msg thread failed, exiting" << endl;
            return NULL;
        }
    }

    // 进入事件循环
    amqp_evbase_loop(evbase);

    return NULL;
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
    vector<QueueInfo> infos = make_queue_info(queues);
    if (infos.size() == 0)
    {
        cout << "make queue info failed" << endl;
        return -1;
    }

    // 线程数取cpu核数和队列数的小值
    size_t thread_num = ((size_t)cpu_num > infos.size())? infos.size() : (size_t)cpu_num;
    init_mq_thread_num(thread_num);

    // 线程将会均分队列信息
    size_t queue_info_per_thread = infos.size() / thread_num;
    size_t rest_queue_info = infos.size() % thread_num;

    // GlobalConfig *config = GlobalConfig::get_instance();
    init_start_time();

    cout << "will create thread: " << thread_num << endl;
    // 每个核创建一个线程
    for (size_t i = 0; i < thread_num; i++)
    {
        // 分配线程所属队列信息
        int begin = (i < rest_queue_info)? (i * queue_info_per_thread + i) : (i * queue_info_per_thread + rest_queue_info);
        int len = (i < rest_queue_info) ? (queue_info_per_thread + 1) : queue_info_per_thread;
        vector<QueueInfo> thread_queue = slice(infos, begin, begin + len - 1);

        // 构造线程参数
        ThreadArg *arg = new ThreadArg(i, thread_queue);
        pthread_t tid;
        cout << "creating thread: " << i << endl;
        int ret = create_thread(tid, i, thread_func, (void *)arg);
        if (ret < 0)
        {
            cout << "create thread failed, exiting" << endl;
            return -1;
        }
    }


    sleep(3);
    return 0;
}
