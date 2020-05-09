#include <string>
#include <regex>

#include "amqp_util.h"
#include "event2/event.h"
#include "global.h"

using namespace std;

int parse_amqp_uri(string &uri, string &user, string &passwd, string &host, uint16_t &port)
{
	regex regex_without_accout("^amqp://(\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}):(\\d+)/*$");
	regex regex_with_accout("^amqp://([a-zA-Z\\d_]+):([\\d\\S]+)@(\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}):(\\d+)/*$");
	smatch match_result;

	if (regex_match(uri, match_result, regex_without_accout))
	{
		user = DEFAULT_USER;
		passwd = DEFAULT_PASS;
		host = match_result[1];
		port = (uint16_t)stoul(match_result[2]);
		return 0;
	}
	else if (regex_match(uri, match_result, regex_with_accout))
	{
		user = match_result[1];
		passwd = match_result[2];
		host = match_result[3];
		port = (uint16_t)stoul(match_result[4]);
		return 0;
	}

	return -1;
}

int create_productor(struct event_base *evbase, string &url, string &exchange, string &queue, string &routing_key, MQ *msgQueue)
{
	string user, passwd, host;
	uint16_t port = 0;

	if (parse_amqp_uri(url, user, passwd, host, port) != 0)
	{
		cout << "parse uri failed" << endl;
		return -1;
	}

    int flag = add_producer(evbase, host.c_str(), port, 
		        VHOST, user.c_str(), passwd.c_str(),
		        exchange.c_str(),
                routing_key.c_str(),
	            EMPTY, //attr
	            msgQueue,//msgQ
		        CT_JSON, //消息类型
		        0, //是否强制的(mandatory)
		        HB_TIME,//心跳检测
		        PRODUCER_TAG,
		        connection_suc_cb, connection_disc_cb, publisher_confirm_cb);
	if (flag == 0)
	{
		cout << "create productor success" << endl;
		return 0;
	}
	else
	{
		cout << "create productor failed" << endl;
	}
	return -1;
}

int create_consumer(struct event_base *evbase, string &url, string &exchange, string &queue, string &binding_key, MQ *msgQueue)
{
	string user, passwd, host;
	uint16_t port = 0;

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
				0,      //是否自动ACK
				1,      //prefetch_count个数
				HB_TIME,    //心跳检测
				DEFAULT_CONSUMER_TAG,
				connection_suc_cb, connection_disc_cb,
				NULL,
				local_comsume_cb,
				NULL);
	if (flag == 0)
	{
		cout << "create consumer success" << endl;
		return 0;
	}
	else
	{
		cout << "create consumer failed" << endl;
	}
	return -1;
}

void publisher_confirm_cb(amqp_connection_state_t conn, void *rspStruct, response_type rspType)
{}

void local_comsume_cb( amqp_connection_state_t conn, void *buf, size_t len, response_type *rsp_type)
{}

void connection_suc_cb(amqp_connection_state_t conn, char *desc)
{}

void connection_disc_cb(amqp_connection_state_t conn, const char *expect, const char *recv)
{}

MQ_ITEM *perpare_msg()
{
	return NULL;
}

int start_loop()
{
	return -1;
}