from config.config import Config
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy import Column,Integer,String, Text, ForeignKey, UniqueConstraint, Index

@as_declarative()
class Base:
    def _asdict(self):
        return {c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs}

class Database:

    # 数据库操作实例
    __instance = None

    @classmethod
    def get_instance(cls):
        if not Database.__instance:
            cfg = Config.get_instance()
            # url = 'mysql+pymysql://%s:%s@%s:%d/%s?charset=utf8mb4' % (cfg.db_user, cfg.db_password, cfg.db_host, cfg.db_port, cfg.db_name)
            url = 'sqlite:///data.db'
            engine = create_engine(url)
            Base.metadata.create_all(engine)
            Session = sessionmaker(bind=engine)
            Database.__instance = Session()
        return Database.__instance

class Node(Base):
    '''
    节点表
    '''
    __tablename__ = 'node'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), unique=True, comment='节点名称')

class TaskSeq(Base):
    '''
    测试指标序列
    '''
    __tablename__ = 'task_seq'
    id = Column(Integer, primary_key=True, autoincrement=True)
    # 任务id, 可级联删除
    task_id = Column(Integer, ForeignKey('test_task.id', ondelete='CASCADE'), comment='任务id')
    stat_time = Column(Integer, nullable=False, comment='指标统计时间')
    sent = Column(Integer, default=-1, comment='消息发送速率')
    received = Column(Integer, default=-1, comment='消息接收速率')
    latency_min = Column(Integer, default=-1, comment='最小延迟')
    latency_median = Column(Integer, default=-1, comment='中位数延迟')
    latency_75th = Column(Integer, default=-1, comment='75th延迟')
    latency_95th = Column(Integer, default=-1, comment='95th延迟')
    latency_99th = Column(Integer, default=-1, comment='99th延迟')

    __table_args__ = (
        # 设置联合唯一
        UniqueConstraint('task_id', 'stat_time', name='uix_task_seq'),
        # 建立索引
        Index('uix_item', 'task_id', 'stat_time')
    )

class Task(Base):
    '''
    测试任务表
    '''
    __tablename__ = 'test_task'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False, unique=True)
    key = Column(Integer, nullable=False, comment='任务key')
    type = Column(String(32), nullable=False, comment='任务类型,标记官方测试工具还是mo_librabbitmq测试工具')
    start_time = Column(Integer, nullable=False, comment='任务开始时间')
    params = Column(Text, comment='任务参数, json Base64编码')
    seqs = relationship(
        "TaskSeq",
        order_by=TaskSeq.id,
        backref="test_task",
        cascade="all,delete"
    )

class RmqCrash(Base):
    '''
    rabbitmq进程崩溃记录
    '''
    __tablename__ = 'rmq_crash_history'
    id = Column(Integer, primary_key=True, autoincrement=True)
    node_id = Column(Integer, ForeignKey('node.id', ondelete='CASCADE'), comment='节点id')
    pid = Column(Integer, comment='进程pid')
    start_time = Column(Integer, nullable=False, comment='进程启动时间')
    crash_time = Column(Integer, nullable=False, comment='崩溃时间')

class RmqStat(Base):
    '''
    rabbitmq服务资源使用表
    '''
    __tablename__ = 'rmq_stat'
    id = Column(Integer, primary_key=True, autoincrement=True)
    node_id = Column(Integer, ForeignKey('node.id', ondelete='CASCADE'), comment='节点id')
    stat_time = Column(Integer, nullable=False, comment='指标统计时间')
    cpu_usage = Column(Integer, nullable=False, comment='cpu使用率')
    mem_usage = Column(Integer, nullable=False, comment='内存使用量')
    disk_spend = Column(Integer, nullable=False, comment='磁盘占用')
    msg_summary = Column(Text, comment='消息概况，json base64编码')

class MachineStat(Base):
    '''
    物理服务器资源使用表
    '''
    __tablename__ = 'machine_stat'
    id = Column(Integer, primary_key=True, autoincrement=True)
    node_id = Column(Integer, ForeignKey('node.id', ondelete='CASCADE'), comment='节点id')
    stat_time = Column(Integer, nullable=False, comment='指标统计时间')
    cpu_usage = Column(Integer, nullable=False, comment='cpu使用率')
    mem_usage = Column(Integer, nullable=False, comment='内存使用量')
    mem_total = Column(Integer, nullable=False, comment='系统内存')
    disk_free = Column(Integer, nullable=False, comment='磁盘分区剩余空间')