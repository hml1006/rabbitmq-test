#include <iostream>
#include "cxxopts.hpp"
#include <unordered_map>
#include <global.h>
#include <string>
#include <regex>

using namespace std;

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
        if (result.count("mp"))
        {
            string mp = result["mp"].as<string>();
            
        }
        if (result.count("s"))
        {
            config->message_size = result["s"].as<int>();
        }
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
            for (int i = 0; i < vals.size() - 1; i++)
            {
                VariableSize vs;
                vs.size = vals[i];
                i++;
                vs.duration = vals[i];
                vec.push_back(vs);
            }
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
        if (result.count("d"))
        {
            config->task_id = result["d"].as<string>();
        }
        if (result.count("st"))
        {
            config->close_timeout = result["st"].as<int>();
        }

        if (result.count("vector"))
        {
            cout << "vector = ";
            const auto values = result["vector"].as<vector<double>>();
            for (const auto& v : values)
            {
                cout << v << ", ";
            }
            cout << endl;
        }

        cout << "Arguments remain = " << argc << endl;

        auto arguments = result.arguments();
        cout << "Saw " << arguments.size() << " arguments" << endl;
    }
    catch (const cxxopts::OptionException& e)
    {
        cout << "error parsing options: " << e.what() << endl;
        exit(1);
    }
}

int main(int argc, char* argv[])
{
    parse(argc, argv);

    return 0;
}
