# 1. 功能分析

​		rabbitmq测试集成工具需完成官方测试工具测试和mo_librabbitmq库测试，官方测试工具和mo_librabbitmq需进行对比测试。

​		rabbitmq服务器需进行崩溃模拟测试，集群需进行脑裂测试。

​		测试工具需可以根据测试计划自动顺序执行测试任务并输出测试报告。

## 1.1 任务脚本功能

   - 动态设置消息发送速率

   - 动态设置消息大小

   - 动态设置生产者消费者数量

   - queue动态设置

   - 自定义消息属性

   - 自定义exchange、queue、routing-key

   - 自定义prefetch

   - 定时爬取rabbitmq服务器统计数据

   - 自动执行测试任务

## 1.2 监控脚本功能

- 监控rabbitmq服务器cpu使用率

- 监控rabbitmq服务器内存使用数量

- 监控rabbitmq服务器磁盘空间占用大小

- 监控rabbitmq服务器进程状态

- 监控服务器信息统计(cpu/内存/磁盘)

## 1.3 报表生成功能

- 日志分析

- 数据整合

- html报表生成

## 1.4 mo_librabbimq库测试程序

- exchange、queue、routing-key参数设置
- 消息参数设置
- 消息大小设置
- 发送速率设置
- prefetch设置
- 发送时长设置

# 2 系统设计

## 2.1 程序组织

```mermaid
graph TD
task[测试计划执行脚本]
monitor[服务器监控脚本]
```
```mermaid
graph TD
librabbitmq[mo_librabbitmq库测试程序]
log[日志分析脚本]
```
``` mermaid
graph TD
export[报表生成脚本]
```

## <span id="plan-config"> 2.1 测试计划配置格式</span>

配置文件采用yaml格式：

``` yaml
# 每项任务间隔, 确保上一项测试已经结束，服务器负载恢复正常
duration: 60
# rabbitmq服务器地址
url: amqp://localhost:5671
# 任务列表
task_list:
  -
  	# 测试时长 秒
    time: 300
    # 生产者和消费者在不同机器上时，此参数生效
    routing-key: keda.test.k
    # exchange
    exchange: test.rmq.ex
	# 消费者自动确认
    auto-ack: true
    # 一次确认多个消息
    multi-ack: 100
    # 持久化消息和队列
    persistent: true
    # 消息预取
    prefetch: 500
    # 消费者速率 msg/s, 每个消费者都是这个速率
    consumer-rate: 500
    # 发送速率 msg/s，每个消费者都是这个速率
    productor-rate: 20000
    # 消息大小
    msg-size:
      -
        # 发送消息大小1000字节，持续发送5秒
        # 持续时间
        duration: 5
        size: 1000
      -
        duration: 10
        size: 2000
      -
        duration: 15
        size: 3000
    # 消息属性，key-value形式
    msg-properties:
      # 例子：优先级属性
      priority：10
    # 单个队列
    queue:
      # 队列名
      name: keda.test.q
      # 生产者数量
      producter: 2
      # 消费者数量
      consumer: 4
  -
    time: 100
    exchange: keda.exchg.test2
    # 消费者自动确认
    auto-ack: true
    # 一次确认多个消息
    multi-ack: 100
    # 持久化消息和队列
    persistent: false
    # 消息预取
    prefetch: 1
    # 消费者速率 msg/s, 每个消费者都是这个速率
    consumer-rate: 500
    # 发送速率 msg/s，每个消费者都是这个速率
    productor-rate:
      - # 发送间隔5秒，发送速率 1000 msg/s
        duration: 5
        rate: 1000
    # 多队列
    queues:
      # 队列生成规则，将从 perf-test-1 到perf-test-10
      pattern：perf-test-%d
      from: 1
      to: 10
      # 生产者和消费者会均衡到所有队列
      # 总的生产者数量
      producter: 100
      # 总的消费者数量
      consumer: 100
```


> 上述配置文件模板生产者消费者在同一台机器上，如果生产者和消费者在不同机器上，task_list只能有一项测试任务。
>

## 2.2 生产者消费者单机执行流程

```mermaid
graph TD
	msg_sender-->rabbitmq
	rabbitmq-->msg_sender
	monitor-->collect
	msg_sender-->collect
	task_script-->collect
	analysis-->data
	rabbitmq--通过api获取消息统计-->collect
	data-->deal
	subgraph data[数据库]
	end
	subgraph log[日志分析]
	collect[日志采集]-->analysis[数据分析]
	end
    subgraph report[报表工具]
    deal[数据整合]-->web[界面展示]
    end
    subgraph server[服务器]
    rabbitmq[rabbitmq服务器]-->monitor[服务器监控脚本]
    end
    subgraph test[测试任务]
    task_script[任务执行脚本]-->msg_sender[消息收发程序]
    end
```
> 消息收发程序为rabbitmq官方测试工具或者mo_librabbitmq库测试程序
## 2.3 生产者消费者双机执行流程
```mermaid
graph TD
	producter-->rabbitmq
	rabbitmq-->consumer
	monitor-->collect
	producter-->collect
	consumer-->collect
	p_task_script-->collect
	c_task_script-->collect
	analysis-->data
	rabbitmq--通过api获取消息统计-->collect
	data-->deal
	subgraph data[数据库]
	end
	subgraph log[日志分析]
	collect[日志采集]-->analysis[数据分析]
	end
    subgraph report[报表工具]
    deal[数据整合]-->web[界面展示]
    end
    subgraph server[服务器]
    rabbitmq[rabbitmq服务器]-->monitor[服务器监控脚本]
    end
    subgraph p_test[测试任务-生产者]
    p_task_script[任务执行脚本]-->producter[生产者]
    end
    subgraph c_test[测试任务-消费者]
    c_task_script[任务执行脚本]-->consumer[消费者]
    end
```
> 生产者和消费者同单机模式的消息收发程序一样，是rabbitmq官方测试程序或者mo_librabbitmq库测试程序，不同之处为作为两个角色运行于不同进程。

# 3 模块设计

## 3.1 测试任务执行脚本

测试任务执行脚本需要解析任务配置文件，配置文件为yaml格式。

 ```flow
 st=>start: 开始
 e=>end: 结束
 readarg=>operation: 解析命令参数
 readcfg=>operation: 解析配置文件
 buildcmd=>operation: 构造命令行参数
 execcmd=>operation: 执行命令
 sub1=>subroutine: 进入双机流程
 cond=>condition: 是否单机测试模式
 io=>inputoutput: 发送日志到日志分析程序
 st->readarg->readcfg->cond
 cond(yes)->buildcmd->execcmd->io->e
 cond(no)->sub1(right)
 ```
> 双机流程为一端是生产者，一端是消费者

**下面是双机流程**

 ```flow
 st=>subroutine: 双机流程
 e=>end: 结束
 buildprod=>operation: 构造生产者命令参数
 buildcons=>operation: 构造消费者命令参数
 execcmd=>operation: 执行命令
 io=>inputoutput: 发送日志到日志分析程序
 cond=>condition: 是否生产者
 st->cond
 cond(yes)->buildprod->execcmd->io
 cond(no)->buildcons->execcmd->io->e
 ```
> 脚本命令中会指定一个参数，指明角色是作为生产者还是消费者
## 3.2 服务器监控脚本

> 服务器监控采用python psutil库。



```flow

st=>start: 开始
e=>end: 结束
start_stat=>operation: 开启统计
will_calc=>parallel: 准备计算
calc_machine=>operation: 计算物理服务器
calc_rabbitmq=>operation: 计算rabbitmq进程
calc_machine_cpu=>operation: 计算cpu使用率
calc_machine_mem=>operation: 计算内存使用率
calc_machine_disk=>operation: 计算磁盘剩余空间
calc_rmq_cpu=>operation: 计算rabbitmq进程cpu使用率
calc_rmq_mem=>operation: 计算rabbitmq进程内存使用量
calc_rmq_disk_spend=>operation: 计算rabbitmq进程磁盘占用
send_stat=>inputoutput: 发送统计数据
calc_end=>parallel: 休眠一个统计间隔

st->will_calc(path1, bottom)->calc_machine->calc_machine_cpu->calc_machine_mem->calc_machine_disk->send_stat->calc_end(path1, left)->will_calc
will_calc(path2, right)->calc_rabbitmq->calc_rmq_cpu->calc_rmq_mem->calc_rmq_disk_spend->send_stat->calc_end(path2, bottom)->e
```

## 3.3 统计数据采集和报表服务
### 3.3.1 数据采集脚本

> 日志分析脚本监听网络端口，等待接收任务脚本发来的日志数据和监控脚本发来的监控数据，解析后存入数据库。
>
  日志分析脚本处理流程如下：

```flow
st=>start: 开始
e=>end: 结束
wait=>operation: 接收客户端请求
parse=>parallel: 解析请求
log=>operation: 日志请求处理
stat=>operation: 监控请求处理
parse_log=>operation: 日志数据解析
parse_stat=>operation: 监控数据解析
write_db=>inputoutput: 写数据库
end_db=>parallel: 请求处理结束
st->wait->parse(path1, bottom)->log->parse_log->write_db->end_db(path1, bottom)->e
parse(path2, right)->stat->parse_stat->write_db->end_db(path2, left)->wait

```

**监控脚本定时上报rabbitmq统计数据**

### 3.4.1 api

#### 3.4.1.1 测试任务

- **添加测试任务**

  POST /tasks

- **删除测试任务**
  DELETE /tasks/{task_id}
- **获取测试任务列表**
  GET /tasks
- **获取测试任务详情**
  GET /tasks/{task_id}
- **添加任务统计条目**
  POST /tasks/{task_id}/task_seqs
- **查询任务统计数据**
  GET /tasks/{task_id}/task_seqs
- **清空任务统计数据**
  DELETE /tasks/{task_id}/task_seqs

#### 3.4.1.2 节点
- **新增节点**
  POST /nodes
- **获取节点列表**
  GET /nodes
- **获取节点名**
  GET /nodes/{node_id}/name
- **删除节点**
  DELETE /nodes/{node_id}

#### 3.4.1.3 rabbitmq服务资源统计
- **添加资源统计条目**
  POST /nodes/{node_id}/rabbitmq/resources
- **查询资源统计条目**
  GET /nodes/{node_id}/rabbitmq/resources?<from><to>
- **清空节点rabbitmq资源统计条目**
  DELETE /nodes/{node_id}/rabbitmq/resources

#### 3.4.1.4 物理服务器资源统计
- **添加物理服务器资源统计条目**
  POST /nodes/{node_id}/machine/resources
- **查询物理服务器资源统计条目**
  GET /nodes/{node_id}/machine/resource?<from><to>
- **清空物理服务器资源统计条目**
  DELETE /nodes/{node_id}/machine/resource

#### 3.4.1.5 rabbitmq服务崩溃统计
- **添加崩溃记录**
  POST /nodes/{node_id}/rabbitmq/crashes
- **获取rabbitmq服务崩溃记录**
  GET /nodes/{node_id}/rabbitmq/crashes
- **删除节点rabbitmq服务崩溃历史**
  DELETE /nodes/{node_id}/rabbitmq/crashes

### 3.4.3 前端界面

> 前端界面请求html页面，并通过api请求报表数据，在浏览器端渲染。

## 3.4 mo_librabbitmq测试程序

mo_librabbitmq测试程序需提供和rabbitmq官方测试工具相同的参数，以方便任务测试脚本调用，并且需要支持任务脚本需要的功能。

   - 动态设置消息发送速率

   - 动态设置消息大小

   - 设置生产者消费者数量

   - queue动态设置

   - 自定义消息属性

   - 自定义exchange、queue、routing-key

   - 自定义prefetch


## 3.5 数据库设计

**数据库名称**：rmq_test

### 3.5.1 任务列表

**表名**：test_task

|  属性    | 类型 | 备注 |
| ---- | ---- | ---- |
| id | int | 自增id，主键 |
| name | varchar(64) | 任务名称 |
| key | int | 任务key |
| type | char(32) | 任务类型(standard, mo_librabbitmq) |
| start_time | timestamp | 任务开始时间 |
| params | text | 任务参数(对json进行base64编码) |

> type是standard测试为采用官方测试工具测试，是mo_librabbitmq则为mo_librabbitmq测试工具测试。
>
> 针对动态生产者和消费者数量测试，需要执行多个测试任务，如果key相同，则确认属于与同一个任务，这多个测试任务逻辑上属于子任务，测试结果存放一起。

### 3.5.2 任务实时统计

**表名**：task_seq

| 属性           | 类型      | 备注         |
| -------------- | --------- | ------------ |
| id             | int       | 自增id，主键 |
| task_id        | int       | 任务id       |
| stat_time      | timestamp | 统计时间点   |
| sent           | int       | 发送的消息数 |
| received       | int       | 接收的消息数 |
| latency_min    | int       | 最小延迟     |
| latency_median | int       | 中位数延迟   |
| latency_75th   | int       | 75th延迟     |
| latency_95th   | int       | 95th延迟     |
| latency_99th   | int       | 99th延迟     |

> 延迟时间单位 μs，微秒。
>
> 条目为每秒的统计，这些数据会用来生成折线图。

### 3.5.3 rabbitmq进程崩溃历史
**表名**：rmq_crash_history

| 属性       | 类型      | 备注         |
| ---------- | --------- | ------------ |
| id         | int       | 自增id，主键 |
| node_id    | int       | 节点id       |
| crash_time | timestamp | 崩溃时间     |
| pid        | int       | 崩溃前pid    |
| start_time | timestamp | 进程启动时间 |

> 监控脚本通过每秒检测一次rabbitmq服务进程状态来判断是否发生崩溃，监控脚本不能判断是崩溃还是重启，如果重启rabbitmq服务，也会被认为崩溃。

### 3.5.4 rabbitmq资源统计
**表名**：rmq_stat

| 属性        | 类型      | 备注               |
| ----------- | --------- | ------------------ |
| id          | int       | 自增id，主键       |
| node_id     | int       | 节点id             |
| stat_time   | timestamp | 统计时间           |
| cpu_usage   | int       | cpu使用率百分比    |
| mem_usage   | int       | 内存使用，单位KB   |
| disk_spend  | int       | 磁盘使用量，单位KB |
| msg_summary | text      | json               |

> msg_summary消息概况，记录消息ack情况。

### 3.5.5 物理服务器资源统计
**表名**：machine_stat

| 属性      | 类型      | 备注                 |
| --------- | --------- | -------------------- |
| id        | int       | 自增id，主键         |
| node_id   | int       | 节点id               |
| stat_time | timestamp | 统计时间             |
| cpu_usage | int       | cpu使用率百分比      |
| mem_usage | int       | 内存使用，单位KB     |
| mem_total | int       | 系统内存             |
| disk_free | int       | 磁盘剩余空间，单位KB |
> disk_free字段为rabbitmq服务器mnesia数据库所在磁盘分区剩余空间。rabbitmq如果有持久化操作，这个值可以估算rabbitmq服务器压力，并且剩余空间为0时，rabbitmq可能崩溃。

### 3.5.6 rabbitmq节点
**表名**：node

| 属性 | 类型         | 备注         |
| ---- | ------------ | ------------ |
| id   | int          | 自增id，主键 |
| name | varchar(128) | 节点名       |



# 4 使用方法

## 4.1 程序功能

```bash
$ ls
docs  etc  main  mo_librabbitmq_test  monitor  rabbitmq-perf-test README.md  server
```

> docs 目录存放文档
>
> etc 目录存放配置文件
>
> main 目录为测试计划执行程序
>
> mo_librabbitmq_test 目录为mo_librabbitmq库测试程序目录
>
> monitor 为rabbitmq和物理服务器监控脚本
>
> rabbitmq-perf-test 目录为官方测试工具
>
> server 目录为数据收集和报表服务服务器

## 4.2 启动数据采集和报表服务

**配置文件**

``` yaml
# http服务器设置
server:
  ip: 0.0.0.0
  port: 8888

# 数据库设置
database:
  host: 127.0.0.1
  port: 3306
  name: rmqtest
  user: root
  password: root
```

> 需要预先创建好数据库，表结构会自动创建，该数据库用户需要有建表权限。

**命令**

``` bash
$ python3 server/main.py -f etc/server.yaml
server: 
	ip: 0.0.0.0
	port: 8888
database: 
	ip: 127.0.0.1
	port: 3306
	name: rmqtest
	user: root
	password: root
```

## 4.3 启动监控程序

**配置**

``` yaml
# rabbitmq管理页配置
rabbitmq:
  host: 172.16.176.70
  manage_port: 6674
  username: dev
  password: dev

# 数据收集服务器地址
collect:
  host: 127.0.0.1
  port: 8888
```

**命令**

``` bash
$ python3 monitor/main.py -f etc/monitor.yaml
```

> 监控程序会每隔5秒采集一次数据并上报服务器，rabbitmq如果有崩溃，也会被上报

## 4.4 启动测试任务执行脚本

**配置**

[测试任务配置](#plan-config)

**命令**

``` bash
$ python3 main/main.py -f etc/plan.yaml -r all -t standard
```

## 4.5 查看结果

chrome 浏览器打开链接：

[http://172.16.80.122:8888/](http://172.16.80.122:8888/)

> IE 浏览器可能有兼容性问题，请使用chrome或者firefox

# 5  注意事项



