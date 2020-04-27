use std::os::raw::c_char;
use libc::{c_int, c_uint, c_void, size_t, uint8, pthread_mutex_t};

pub type AmqpBoolean = c_int;

#[repr(C)]
pub struct AmqpBytes {
    len: size_t,
    bytes: *mut c_void,
}

#[repr(C)]
pub struct AmqpFieldValue {
    kind: uint8
    value: u64
}

#[repr(C)]
pub struct AmqpTableEntry {
    key: AmqpBytes,
    value: AmqpFieldValue
}

#[repr(C)]
pub struct AmqpTable {
    num_entries: c_int,
    entries: *mut AmqpTableEntry
}

#[repr(C)]
pub struct MsgQueueItem {
    exchange: AmqpBytes,
    routingkey: AmqpBytes,
    content: AmqpBytes,

    msg_persistent: AmqpBoolean,

    rpc_mode: AmqpBoolean,
    correlation_id: AmqpBytes,
    reply_to: AmqpBytes,

    ttl_per_msg: AmqpBoolean,
    expiration: AmqpBytes,

    headers: AmqpTable,

    next: *c_void
}

#[repr(C)]
pub struct MsgQueue {
    num: c_int,
    head: *mut MsgQueueItem,
    tail: *mut MsgQueueItem,
    lock: pthread_mutex_t
}

#[link(name = "rabbitmq_r")]
extern {
    pub fn amqp_create_evbase_with_lock() ->*c_void;
    pub fn amqp_destroy_evbase(evbase: *c_void);
    pub fn amqp_evbase_loop(evbase: *c_void) -> c_int;

    pub fn add_producer(ev_base: *mut c_void, dist_ip: *c_char, dist_port: u16, vhost: *c_char, luname: *c_char, lupass: *c_char, \
                    exchange: *c_char, routing_key: *c_char, attr: c_uint, ) -> c_int;
    pub fn mq_init(mq: *mut MsgQueue);
    pub fn mq_deinit(mq: *mut MsgQueue);

    pub fn mq_push(mq: *mut MsgQueue, item: *mut MsgQueueItem) -> c_int;
    pub fn mqi_prepare(exchage: *c_char, routing_key: *c_char, content: *c_char, len: size_t, persistent: AmqpBoolean, rpc_mode: AmqpBoolean, \
                    correlation_id: *c_char, reply_to: *c_char, ttl_per_msg: AmqpBoolean, expiration: *c_char) -> *MsgQueueItem;
    pub fn mqi_prepare_with_headers(exchage: *c_char, routing_key: *c_char, content: *c_char, len: size_t, persistent: AmqpBoolean, rpc_mode: AmqpBoolean, \
                     correlation_id: *c_char, reply_to: *c_char, ttl_per_msg: AmqpBoolean, expiration: *c_char, headers: AmqpTable) -> *MsgQueueItem;          
    
    pub fn amqp_table_free(table: AmqpTable);
    pub fn mqi_free(item: *MsgQueueItem);
    pub fn mqi_free_all(item: *MsgQueueItem);

    pub fn amqp_bytes_malloc_dup_cstring(cstr: *c_char) -> AmqpBytes;

}