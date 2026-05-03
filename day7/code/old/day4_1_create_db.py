from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class RouterMonitor(Base):
    __tablename__ = 'router_monitor'

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_ip = Column(String(50))
    cpu_usage_percent = Column(Integer)
    mem_use = Column(Integer)
    mem_free = Column(Integer)
    record_datetime = Column(DateTime,default=datetime.now)

engine = create_engine('sqlite:///sqlalchemy_syslog_sqlite3.db')

Base.metadata.create_all(engine)

    #print("[*] 数据库和表已创建成功")