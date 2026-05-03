#UDP服务器端

import socket
import sys
import struct
import hashlib
import pickle
from types import BuiltinMethodType

#绑定地址到UDP端口
address = ('0.0.0.0',6666)
s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s.bind(address)

print('UDP服务器就绪！等待客户数据！')
while True:
    try:
        #接收数据限制大小为512
        recv_source_data = s.recvfrom(512)

        #提取发送数据与socket信息（源地址，源端口）
        packet, addr = recv_source_data
        #拆包
        header = packet[:16]
        body = packet[16:-16]
        md5_recv = packet[-16:]

        #解析header
        version, pkt_type, seq_id, length = struct.unpack("!HHIQ",header)

        #计算MD5
        md5_calc = hashlib.md5(header + body).digest()

        if md5_recv == md5_calc:
            print('=' * 80)
            print("{0:<30}:{1:<30}".format("数据源自于",str(addr)))
            print("{0:<30}:{1:<30}".format("数据序列号",seq_id))
            print("{0:<30}:{1:<30}".format("数据长度为",length))
            print("{0:<30}:{1:<30}".format("数据内容为",str(pickle.loads(body))))
        else:
            print('MD5校验错误：')
    except KeyboardInterrupt:
        sys.exit()

