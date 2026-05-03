from pathlib import Path
import sys
# 获取当前文件的路径
current_file_path = Path(__file__).resolve()

# 上一级目录的路径
parent_dir = current_file_path.parent.parent.parent

# 添加上一级目录到 Python 路径
sys.path.insert(0, str(parent_dir))

from tools.day5_snmp_v2_4_get_all import snmpv2_get_all

import time
import datetime
from influxdb import InfluxDBClient

# ---------网络设备信息---------
routers = [
    {"ip": "192.168.0.89", "community": "public"},
    {"ip": "192.168.0.107", "community": "public"},
]

# ---------InfluxDB信息--------
influx_host = '192.168.0.64'
influx_port = 8086
influx_measurement = "router_monitor"
influx_db = "qytdb"
influx_user = "qytdbuser"
influx_password = "Cisc0123"


client = InfluxDBClient(influx_host, influx_port, influx_user, influx_password, influx_db)
# client.query("drop measurement router_monitor")  # 删除表
# client.query("drop measurement if_monitor")  # 删除表


for router in routers:
    router_ip = router["ip"]
    snmp_coummnity = router["community"]

    getall_result = snmpv2_get_all(router_ip, snmp_coummnity)

    
#----------------------写入接口进出数据------------------------
    current_time = datetime.datetime.now(datetime.UTC).isoformat("T")

    if_bytes_body = []  # 用于存储多个接口的字典

    for if_info in getall_result.get('interface_list',[]):
        #只显示Gi1
        if if_info.get('interface_name') != 'GigabitEthernet1':
            continue

        if if_info.get('in_bytes') and if_info.get('out_bytes'):
            if_info_dict = {
                                "measurement": "if_monitor",   # 可以认为是表名
                                "time": current_time,          # 时间戳，时序数据库的核心
                                "tags": {                      # 标签，用于过滤
                                    "device_ip": getall_result.get('device_ip'),
                                    "device_type": "IOS-XE",
                                    "interface_name": if_info.get('interface_name')
                                },
                                "fields": {                    # 字段，用于存储数据
                                    "in_bytes": if_info.get('in_bytes'),
                                    "out_bytes": if_info.get('out_bytes'),
                                },
                            }
            if_bytes_body.append(if_info_dict)



    print(if_bytes_body)
    client.write_points(if_bytes_body)  # 写入数据库
    print(router_ip, getall_result.get('device_ip'))