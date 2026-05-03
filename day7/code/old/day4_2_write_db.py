from signal import valid_signals
import sys
from pathlib import Path

from sqlalchemy.sql.expression import except_all
from datetime import datetime
import asyncio

#让crond能找到项目
PROJECT_DIR = '/root/protocol'
sys.path.insert(0,PROJECT_DIR)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from day4_1_create_db import RouterMonitor
#from day4_1_create_db import Base
from tools.day4_get import snmpv2_get

#数据库连接
engine = create_engine('sqlite:///sqlalchemy_syslog_sqlite3.db')
#Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
db = Session()

#设备列表
devices = [
    {"ip": "192.168.0.89","community": "public"},
    {"ip": "192.168.0.107","community": "public"},
]


#OID
OID_CPU = "1.3.6.1.4.1.9.9.109.1.1.1.1.6.7"
OID_MEM_USED = "1.3.6.1.4.1.9.9.109.1.1.1.1.12.7"
OID_MEM_FREE = "1.3.6.1.4.1.9.9.109.1.1.1.1.13.7"

#SNMP采集函数
def get_value(ip,community,oid):
    oid_str,value = asyncio.run(snmpv2_get(ip, community, oid))
    return int(value)

 

    
  

#主程序
def main():
    count = 0

    for dev in devices:
        ip = dev["ip"]
        community = dev["community"]

        try:
            cpu = get_value(ip,community, OID_CPU)
            mem_used = get_value(ip,community,OID_MEM_USED)
            mem_free = get_value(ip,community,OID_MEM_FREE)

            record = RouterMonitor(
                device_ip=ip,
                cpu_usage_percent=cpu,
                mem_use=mem_used,
                mem_free=mem_free,
                record_datetime=datetime.now()
            )

            db.add(record)
            count += 1
            db.commit()

            #print(f"[+] {ip} OK")
            

            print(f"[+] {ip}: CPU={cpu}%, MEM_used{mem_used}, MEM_Free={mem_free}")
            

        except Exception as e:
            print(f"[!] {ip} 采集失败: {e}")
            db.rollback()
            
   
    print(f"[*]共写入{count}条记录")
    print("DB FILE:", engine.url)
if __name__ == "__main__":
    main()