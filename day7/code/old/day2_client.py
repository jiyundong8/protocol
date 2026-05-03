#设计一个自己的UDP协议，用于传输各种python数据

import socket
import struct
import hashlib
import pickle

def udp_send_data(ip,port,data_list):
    address = (ip, port)
    #创建UDP套接字socket，AF_INET为IPV4，SOCK_DGRAM为Datagram也就是UDPUDP
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    version = 1
    pkt_type = 1
    seq_id = 1

    for x in data_list:
        send_data = pickle.dumps(x)
        length = len(send_data)

        header = struct.pack (
            "!HHIQ",
            version,
            pkt_type,
            seq_id,
            length
        )

        #MD5校验
        md5 = hashlib.md5(header + send_data).digest()

        #数据包
        packet = header + send_data + md5

        #发送
        s.sendto(packet, address)

        print(f"发送: id={seq_id}, size={length}")

        seq_id += 1

    s.close()


if __name__ == "__main__":
    from datetime import datetime
    user_data = ['乾颐堂',[1,'qytang',3],{'qytang':1,'test':3},{'datetime':datetime.now()}]
    udp_send_data('192.168.0.64',6666,user_data)