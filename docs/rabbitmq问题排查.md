## 1. mnesia数据库连接超时问题

集群最后一个退出的节点会变成master，如果集群启动时先启动的是slave，则应在30s内启动master，否则会报mnesia数据库连接超时。如果先启动master，可以正常启动。

> 如果此时master节点因为异常再也无法启动，此时slave会因为一直等待master而无法启动。如果希望启动slave，则需要先把master移出集群。
>
> ```bash
> $ rabbitmqctl forget_cluster_node rabbitmq@xxx-yyy-zzz --offline
> ```

## 2. 断电导致集群无法启动

