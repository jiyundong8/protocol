from operator import length_hint
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
from day6_1_create_db import InterfaceMonitor
from tools.day6_snmp_getbulk import snmpv2_getbulk


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
OID_ifDescr = "1.3.6.1.2.1.2.2.1.2"
OID_ifInOctets = "1.3.6.1.2.1.2.2.1.10"
OID_ifOutOctets = "1.3.6.1.2.1.2.2.1.16"

#SNMP采集函数
def get_value(ip,community,oid):
    result = asyncio.run(snmpv2_getbulk(ip, community, oid))

    if not result:
        print(f"[!] 没有获取到OID{oid}的数据:{ip}")
        return []

    return result
   
  

#主程序
def main():
    count = 0
    #获取最大设备IP长度，以便对齐
    max_ip_length = max(len(dev['ip']) for dev in devices)
    
    for dev in devices:
        ip = dev["ip"]
        community = dev["community"]

        try:
            ifDescr_list = get_value(ip,community,OID_ifDescr)
            ifIn_list = get_value(ip,community,OID_ifInOctets)
            ifOut_list = get_value(ip,community,OID_ifOutOctets)

            length = min(len(ifDescr_list),len(ifIn_list),len(ifOut_list))

            for i in range(length):
                interface_name = ifDescr_list[i][1]
                #跳过空接口后者"NULL0"接口
                if not interface_name or interface_name == "Null0":
                    continue

                in_bytes = int(ifIn_list[i][1]) if ifIn_list[i][1].isdigit() else 0
                out_bytes = int(ifOut_list[i][1]) if ifOut_list[i][1].isdigit() else 0

                if not interface_name:
                    print(f"[!]{ip} 接口名为空，跳过该接口")
                    continue

                record = InterfaceMonitor(
                    device_ip=ip,
                    interface_name = interface_name,
                    in_bytes = in_bytes,
                    out_bytes = out_bytes,
                    record_datetime=datetime.now()
                )

                db.add(record)
                count += 1
                

                
                print(f"[+] {ip:<{max_ip_length}}: {interface_name:<25} IN={in_bytes:>12} OUT={out_bytes:>12}")
            
            db.commit()
        except Exception as e:
            print(f"[!] {ip} 采集失败: {e}")
            db.rollback()
            
   
    print(f"[*]共写入{count}条记录")
    
if __name__ == "__main__":
    main()