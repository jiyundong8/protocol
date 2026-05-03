import asyncio
from pysnmp.hlapi.v3arch.asyncio import *
from pprint import pprint


# SNMP GETBULK 操作
async def snmpv2_getbulk(ip, community, oid, count=25, port=161):
    # 使用 bulk_cmd 执行 SNMP GETBULK 操作
    iterator = bulk_cmd(
        SnmpEngine(),
        CommunityData(community),  # 配置 community
        await UdpTransportTarget.create((ip, port)),  # 配置目的地址和端口号
        ContextData(),
        0, count,  # non-repeaters 和 max-repetitions
        ObjectType(ObjectIdentity(oid)),  # OID
        lexicographicMode=True
    )

    # 获取结果
    error_indication, error_status, error_index, var_binds = await iterator

    # 错误处理
    if error_indication:
        print(f"读取错误!!!\n{error_indication}")
    elif error_status:
        print(f"读取错误!!!\n{error_status} at {error_index and var_binds[int(error_index) - 1][0] or '?'}")
    else:
        # 处理返回的 varBinds
        result = []
        for var_bind_table_row in var_binds:
            get_oid = str(var_bind_table_row[0])
            get_value = str(var_bind_table_row[1])
            if oid not in get_oid:  # 超过OID范围跳出循环
                break
            result.append((get_oid, get_value))
        return result

if __name__ == "__main__":
    # ip 地址与 snmp community 字符串
    ip_address = "192.168.0.89"
    community = "public"

    # 获取接口名称
    raw_name_list = asyncio.run(snmpv2_getbulk(ip_address, community, "1.3.6.1.2.1.2.2.1.2", port=161))
    if_name_list = [raw_if_name[1] for raw_if_name in raw_name_list]
    print(if_name_list)
    # 获取接口速率
    #raw_speed_list = asyncio.run(snmpv2_getbulk(ip_address, community, "1.3.6.1.2.1.2.2.1.5", port=161))
    #if_speed_list = [raw_speed[1] for raw_speed in raw_speed_list]
    #print(if_speed_list)
    # 获取接口管理状态
    #raw_status_list = asyncio.run(snmpv2_getbulk(ip_address, community, "1.3.6.1.2.1.2.2.1.7", port=161))
    #if_status_list = [raw_status[1] for raw_status in raw_status_list]
    #print(if_status_list)
    # 获取进接口字节数
    raw_in_bytes_list = asyncio.run(snmpv2_getbulk(ip_address, community, "1.3.6.1.2.1.2.2.1.10", port=161))
    if_in_bytes_list = [raw_in_bytes[1] for raw_in_bytes in raw_in_bytes_list]
    print(if_in_bytes_list)
    # 获取出接口字节数
    raw_out_bytes_list = asyncio.run(snmpv2_getbulk(ip_address, community, "1.3.6.1.2.1.2.2.1.16", port=161))
    if_out_bytes_list = [raw_out_bytes[1] for raw_out_bytes in raw_out_bytes_list]
    print(if_out_bytes_list)