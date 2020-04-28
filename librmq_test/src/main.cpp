#include <iostream>
#include "cxxopts.hpp"
#include <unordered_map>
#include <global.h>
#include <string>
#include <regex>
#include <vector>
#include <sys/sysinfo.h>
#include <pthread.h>
#include <sched.h>

using namespace std;

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
        }
        if (result.count("x"))
        {
            config->productor_number = result["x"].as<int>();
        }
        if (result.count("y"))
        {
            config->consumer_number = result["y"].as<int>();
        }
        if (result.count("qp"))
        {
            config->queue_name_pattern = result["qp"].as<string>();
        }
        if (result.count("qpf"))
        {
            config->queue_name_from = result["qpf"].as<int>();
        }
        if (result.count("qpt"))
        {
            config->queue_name_to = result["qpt"].as<int>();
        }
        if (result.count("h"))
        {
            config->amqp_url = result["h"].as<string>();
        }
        if (config->productor_number < 0 || config->consumer_number < 0)
        {
            cout << "productor number or consumer number are wrong" << endl;
            exit(-1);
        } else if (config->productor_number == 0 && config->consumer_number == 0)
        {
            cout << "productor number and consumer number are zero" << endl;
            exit(-1);
        } else if (config->productor_number == 0 && config->consumer_number > 0)
        {
            config->role = Role::CONSUMER;
        } else if (config->productor_number > 0 && config->consumer_number == 0)
        {
            config->role = Role::PRODUCTOR;
        } else if (config->productor_number > 0 && config->consumer_number > 0)
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

void *thread_func(void *arg)
{
    return NULL;
}

// 创建线程并绑定cpu
pthread_t create_thread(int cpu, void *(*start_routine) (void *), void *arg)
{
    pthread_t tid;

    // 初始化线程属性
    pthread_attr_t att;
    pthread_attr_init(&att);

    // 设置detach
    pthread_attr_setdetachstate(&att, PTHREAD_CREATE_DETACHED);
    
    int ret = pthread_create(&tid, NULL, start_routine, arg);
    if (ret < 0)
    {
        
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
    for (int i = 0; i < cpu_num; i++)
    {
        pthread_t tid = create_thread(i, thread_func, NULL);
    }

    return 0;
}
