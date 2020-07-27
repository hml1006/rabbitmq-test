#!/usr/bin/python3
import argparse
import yaml

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='create test yaml file')
    parser.add_argument('--url', type=str, dest='url', help='amqp url', default='amqp://dev:dev@127.0.0.1:5672')
    parser.add_argument('-z', '--run_duration', type=int, dest='time', help='Run duration', default=3600)
    parser.add_argument('-l', '--log_server', type=str, dest='log_server', help='Log server url', default='http://127.0.0.1:9999')
    parser.add_argument('-e', '--exchange', type=str, dest='exchange', help='Exchange', default='test.rmq.ex')
    parser.add_argument('-t', '--type', type=str, dest='type', help='Exchange type', default='direct')
    parser.add_argument('-k', '--routing_key', type=str, dest='routing_key', help='Routing key', default='test.rmq.k')
    parser.add_argument('-u', '--queue', type=str, dest='queue', help='Queue name', default='test.rmq.q')
    parser.add_argument('-x', '--producer', type=int, dest='producer',  help='Producer number', default=10)
    parser.add_argument('-y', '--consumer', type=int, dest='consumer', help='Consumer number', default=10)
    parser.add_argument('-r', '--rate', type=int, dest='rate', help='Producer send rate', default=0)
    parser.add_argument('-s', '--size', type=int, dest='size', help='Message size', default=2000)
    parser.add_argument('-q', type=int, dest='prefetch', help='Consumer prefetch', default=0)
    parser.add_argument('-qp', type=str, dest='qp', help='Queue pattern, for example: perf-test-q-%%d')
    parser.add_argument('-qpf', type=int, dest='qpf', help='Queue pattern from')
    parser.add_argument('-qpt', type=int, dest='qpt', help='Queue pattern to')
    parser.add_argument('-vs', type=str, dest='vs', help='Dynamically message size, for example=> 1000:5,2000:10,3000:20')
    parser.add_argument('-vr', type=str, dest='vr', help='Dynamically message send rate, for example=> 1000:5,2000:10,3000:20')
    parser.add_argument('--name', type=str, dest='name', help='Yaml file name')
    args = parser.parse_args()

    yaml_data = {
        'sleep': 0,
        'url': args.url,
        'log_server': args.log_server,
        'task-list': []
    }

    # parse rate
    if not args.vr:
        task_rate = args.rate
    else:
        rate_duration_list = []
        rate_durations = args.vr.split(',')
        for item in rate_durations:
            [rate, duration] = item.split(':')
            rate_duration_list.append({
                'rate': int(rate),
                'duration': int(duration)
            })
        task_rate = rate_duration_list

    # parse size
    if not args.vs:
        msg_size = args.size
    else:
        size_duration_list = []
        size_durations = args.vs.split(',')
        for item in size_durations:
            [size, duration] = item.split(':')
            size_duration_list.append({
                'size': int(size),
                'duration': int(duration)
            })
        msg_size = size_duration_list

    # parse queue
    if not args.qp:
        queue = {
            'name': args.queue,
            'producer': args.producer,
            'consumer': args.consumer
        }
    else:
        queue = {
            'pattern': args.qp,
            'from': args.qpf,
            'to': args.qpt,
            'producer': args.producer,
            'consumer': args.consumer
        }
    if not args.name:
        name = 'task-p%dc%d' % (args.producer, args.consumer)
    else:
        name = args.name
    task = {
        'name': name,
        'time': args.time,
        'routing-key': args.routing_key,
        'exchange': args.exchange,
        'type': args.type,
        'auto_ack': True,
        'multi_ack': 0,
        'persistent': False,
        'prefetch': args.prefetch,
        'consumer_rate': 0,
        'msg-properties': {
            'priority': 1
        },
        'producer-rate': task_rate,
        'msg-size': msg_size,
        'queue': queue
    }

    yaml_data['task-list'].append(task)

    text = yaml.dump(yaml_data, default_flow_style=False)
    print(text)
    filenane = 'etc/' + name + '.yaml'
    f = open(file=filenane, mode='w')
    if f:
        print('Writing to %s ...' % filenane)
        f.write(text)
        f.close()
        print('Written successfully')
    else:
        print('Write failed')
