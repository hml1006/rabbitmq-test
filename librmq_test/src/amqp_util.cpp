#include <string>
#include <arpa/inet.h>
#include <sys/time.h>

#include <mutex>
#include <vector>

#include "amqp_util.h"
#include "event2/event.h"
#include "global.h"

using namespace std;

int parse_amqp_uri(string &uri, string &user, string &passwd, string &host, uint16_t &port)
{
    char *buf = new char[512];
    shared_ptr<char> url(buf, std::default_delete<char[]>());
    snprintf(buf, 512, "%s", uri.c_str());
    
    struct amqp_connection_info parsed;
    memset(&parsed, 0, sizeof(struct amqp_connection_info));
    int status = amqp_parse_url(buf, &parsed);
    if (status != AMQP_STATUS_OK)
    {
        cout << "bad amqp url => " << uri << endl;
        return -1;
    }
    if (parsed.user != NULL && parsed.password != NULL)
    {
        user = parsed.user;
        passwd = parsed.password; 
    }

    host = parsed.host;
    port = parsed.port;
    
	return 0;
}

int create_productor(struct event_base *evbase, string &url, string &exchange, string &routing_key, MQ* msg_queue)
{
	string user, passwd, host;
	uint16_t port = 0;

	if (parse_amqp_uri(url, user, passwd, host, port) != 0)
	{
		cout << "parse uri failed" << endl;
		return -1;
	}
    mq_init(msg_queue);
    int flag = add_producer(evbase, host.c_str(), port, 
		        VHOST, user.c_str(), passwd.c_str(),
		        exchange.c_str(),
                routing_key.c_str(),
	            EMPTY, //attr
	            msg_queue,//msgQ
		        CT_PLAIN, //消息类型
		        0, //是否强制的(mandatory)
		        HB_TIME,//心跳检测
		        PRODUCER_TAG,
		        connection_suc_cb, connection_disc_cb, NULL);
	if (flag == 0)
	{
		return 0;
	}
	else
	{
		cout << "create productor failed" << endl;
	}
	return -1;
}

int create_consumer(struct event_base *evbase, string &url, string &exchange, string &queue, string &binding_key)
{
	string user, passwd, host;
	uint16_t port = 0;

	GlobalConfig *config = GlobalConfig::get_instance();

	if (parse_amqp_uri(url, user, passwd, host, port) != 0)
	{
		cout << "parse uri failed" << endl;
		return -1;
	}

	int flag = add_consumer(evbase, host.c_str(), port,
				VHOST, user.c_str(), passwd.c_str(),
				queue.c_str(),
				exchange.c_str(),
				binding_key.c_str(),
				Q_DECLARE|Q_BIND|B_QOS|B_CONSUME,//attr
				NULL, //msgQ
				config->auto_ack? 1:0,      //是否自动ACK
				config->prefetch,      //prefetch_count个数
				HB_TIME,    //心跳检测
				CONSUMER_TAG,
				connection_suc_cb, connection_disc_cb,
				NULL,
				local_comsume_cb,
				NULL);
	if (flag == 0)
	{
		return 0;
	}
	else
	{
		cout << "create consumer failed" << endl;
	}
	return -1;
}

//void publisher_confirm_cb(amqp_connection_state_t conn, void *rspStruct, response_type rspType)
//{}

void local_comsume_cb( __attribute__((unused))amqp_connection_state_t conn, void *buf, __attribute__((unused))size_t len, response_type *rsp_type)
{
	*rsp_type = RT_ACK ;
    
	// GlobalConfig *config = GlobalConfig::get_instance();

	// mo_librabbitmq不支持multi ack
	shared_ptr<ThreadGlobal> global = get_thread_stat(pthread_self());
    if (global == nullptr)
    {
        pthread_exit(0);
    }
	long secs = time(NULL) - get_start_time();

	shared_ptr<ThreadStatPerSecond> sec_stat = global->get_sec_stat(secs);
    if (sec_stat == nullptr)
    {
        return;
    }

	// 消息发布时间戳
	timeval msg_tv;
	time_t *sec = (time_t *)buf;
	msg_tv.tv_sec = ntohl(*sec);
	msg_tv.tv_usec = ntohl(*(++sec));

	// 当前时间戳
	timeval cur_tv;
	struct timezone tz;
	gettimeofday(&cur_tv, &tz);

	// 计算延迟并把延迟添加到对应时间点
	int latency = (cur_tv.tv_sec - msg_tv.tv_sec) * 1000 + (cur_tv.tv_usec - msg_tv.tv_usec)/1000;
    sec_stat->msg_received++;
	sec_stat->latency_list.push_back(latency);
}

void connection_suc_cb(amqp_connection_state_t conn, char *desc)
{
	cout << "[****connection_suc_cb****] connect success=> " << " tag: " << amqp_get_tag(conn) << ", desc: " << desc << endl;
//    cout.flush();
}

void connection_disc_cb(amqp_connection_state_t conn, const char *expect, const char *recv)
{
    cout << "[####connection_disc_cb####] connection disconnect, expect: " << expect << ", recv: " << recv << endl;
    
    sleep(1);
    
    
	GlobalConfig *config = GlobalConfig::get_instance();

	event_base *evbase = amqp_get_evbase(conn);
	string tag = amqp_get_tag(conn);
	if (tag == CONSUMER_TAG)
	{
        string queue = amqp_get_queue_name(conn);
        int ret = create_consumer(evbase, config->amqp_url, config->exchange, queue, config->routing_key);
        if (ret != 0)
        {
            cout << "create consumer failed, queue: " << queue << endl;
        }
	}
	else if (tag == PRODUCER_TAG)
	{
		MQ *mq = amqp_get_msg_queue(conn);
        int ret = create_productor(evbase, config->amqp_url, config->exchange, config->routing_key, mq);
        if (ret != 0)
        {
            cout << "create productor failed, routing_key: " << config->routing_key << endl;
        }
	}
}

// 构造一条消息
MQ_ITEM *prepare_msg(size_t msg_size)
{
	GlobalConfig *config = GlobalConfig::get_instance();

	// 最小消息大小为sizeof（struct timeval）, 用来存储时间戳
	size_t true_size = msg_size;
	if (msg_size < sizeof(struct timeval))
	{
		true_size = sizeof(struct timeval);
	}
	shared_ptr<char> content(new char[true_size], [](char *ptr) {
		delete [] ptr;
	});

	MQ_ITEM *msg = mqi_prepare(config->exchange.c_str(), config->routing_key.c_str(), \
	 					content.get(), true_size, config->persistent?1:0, 0, NULL, NULL, 0, NULL);
	return msg;
}
