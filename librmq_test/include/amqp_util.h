#ifndef AMQP_UTIL_H
#define AMQP_UTIL_H

#include <string>
#include <cstring>

using namespace std;

#include "amqp_mq.h"
#include "global.h"

#define VHOST            (char *)"/"
#define DEFAULT_USER     (char *)"dev"
#define DEFAULT_PASS     (char *)"dev"
#define DEFAULT_EXCHANGE_TYPE     (char *)("direct")
#define CONSUMER_TAG      (char *)("consumer.tag")
#define PRODUCER_TAG              (char *)("producer.tag")
#define HB_TIME             10

int parse_amqp_uri(string &uri, string &user, string &passwd, string &host, uint16_t &port);

int create_productor(struct event_base *evbase, string &url, string &exchange, string &queue, string &routing_key, MQ* msg_queue);

int create_consumer(struct event_base *evbase, string &url, string &exchange, string &queue, string &routing_key);

void publisher_confirm_cb(amqp_connection_state_t conn, void *rspStruct, response_type rspType);

void local_comsume_cb( amqp_connection_state_t conn, void *buf, size_t len, response_type *rsp_type );

void connection_suc_cb(amqp_connection_state_t conn, char *desc );

void connection_disc_cb(amqp_connection_state_t conn, const char *expect, const char *recv);

void drop_msg_list(vector<MQ_ITEM *> &msg_list);

shared_ptr<vector<MQ_ITEM *>> make_msg_list(size_t msg_num, size_t msg_size);

void add_msg_cache(shared_ptr<vector<MQ_ITEM *>> cache);

shared_ptr<vector<MQ_ITEM *>> get_msg_cache();

size_t get_cache_group_num();

#endif /* AMQP_UTIL_H */