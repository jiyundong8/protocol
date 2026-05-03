#!/usr/bin/env python3
# -*- coding=utf-8 -*-
"""Day 10 - 使用 PyShark 解析 PCAP 并写入 Elasticsearch"""

import json
from datetime import timedelta
from datetime import timezone
from pathlib import Path
from urllib import error
from urllib import request

import pyshark


# 设置时区为 UTC
TZUTC_0 = timezone(timedelta(hours=0))
CURRENT_DIR = Path(__file__).resolve().parent
PCAP_FILE = CURRENT_DIR / 'pkt.pcap'
ES_URL = 'http://127.0.0.1:9200'
INDEX_NAME = 'qyt-pyshark-index'


def es_request(method, path, payload=None):
    """通过 Elasticsearch HTTP API 发送请求。"""
    data = None

    if payload is not None:
        data = json.dumps(payload).encode('utf-8')

    req = request.Request(
        f'{ES_URL}{path}',
        data=data,
        headers={'Content-Type': 'application/json'},
        method=method,
    )

    try:
        with request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
    except error.HTTPError as http_error:
        error_body = http_error.read().decode('utf-8', errors='ignore')
        print("ES ERROR:", error_body)
        raise RuntimeError(f'Elasticsearch 请求失败: {http_error.code} {error_body}') from http_error


def get_layer_fields(layer):
    """提取单个协议层的字段字典。"""
    layer_fields = getattr(layer, '_all_fields', {})

    if isinstance(layer_fields, dict):
        return layer_fields

    return {}


def normalize_packet(pkt):
    """把单个数据包整理为适合写入 Elasticsearch 的字典。"""
    pkt_dict = {}

    # ★★★★★★ 请学员自己完成这里: 遍历全部协议层, 把字段合并到 pkt_dict ★★★★★★
    for layer in pkt.layers:
        fields = get_layer_fields(layer)

        for k,v in fields.items():
            if v is None:
                continue
            #pyshark 字段有时候是对象，转成字符串更安全
            pkt_dict[str(k)] = str(v)

    pkt_dict_final = {}

    # ★★★★★★ 请学员自己完成这里: 去掉空键, 并把字段名中的 . 替换为 _ ★★★★★★
    
    


    pkt_dict_final['sniff_time'] = pkt.sniff_time.astimezone(TZUTC_0).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    pkt_dict_final['highest_layer'] = pkt.highest_layer

    for k,v in pkt_dict.items():
        if not k:
            continue

        clean_key = k.replace('.','_')
        pkt_dict_final[clean_key] = v

    ip_len = pkt_dict_final.get('ip_len')

    if ip_len is not None:
        try:
            pkt_dict_final['ip_len'] = int(ip_len)
        except (TypeError, ValueError):
            pass

    return pkt_dict_final
def create_index_if_not_exists():
    try:
        es_request('GET', f'/{INDEX_NAME}')
        #print('[+] index 已存在')
    except Exception:
        print('[+] index 不存在，正在创建...')

        es_request(
            'PUT',
            f'/{INDEX_NAME}',
            {
                "mappings": {
                    "dynamic": True
                }
            }
        )
        print('[+] index 创建成功')

def process_pcap():
    """读取 PCAP 文件并写入 Elasticsearch。"""
    cap = pyshark.FileCapture(str(PCAP_FILE),use_json=True)
    cap.load_packets()
    success_count = 0

    try:
        for packet_id, pkt in enumerate(cap, start=1):
            packet_data = normalize_packet(pkt)
            if not packet_data:
                continue

            # ★★★★★★ 请学员自己完成这里: 调用 HTTP API 把 packet_data 写入 Elasticsearch 索引 ★★★★★★
            try:
                res = es_request(
                    'POST',
                    f'/{INDEX_NAME}/_doc',
                    packet_data
                )
                #print(res)
                if res.get("result") == "created" and res["_shards"]["failed"] == 0:
                    success_count += 1
                    print('created')
                else:
                    print("[FAILED]",res)
            # ★★★★★★ 写入成功后打印结果, 并统计 success_count ★★★★★★
                #print(f'[+] 写入成功 packet{packet_id}: {res.get("_id")}')
                
            except Exception as e:
                import traceback
                print(f'[!]写入失败 packet{packet_id}:{e}')
                traceback.print_exc()        
    finally:
        cap.close()
    print(f'[+] 写入成功 packet{packet_id}: {res.get("_id")}')
    #print(f'\n共写入{success_count}个数据包到 {INDEX_NAME}')

if __name__ == '__main__':
    es_info = es_request('GET', '/')
    print(f'[+] Elasticsearch 版本: {es_info.get("version", {}).get("number")}')
    create_index_if_not_exists()
    process_pcap()
    count_res = es_request('GET', f'/{INDEX_NAME}/_count')
    print(f'[+] 当前索引文档总数: {count_res.get("count")}')