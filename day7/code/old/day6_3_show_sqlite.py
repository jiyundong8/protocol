import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from day6_1_create_db import InterfaceMonitor, engine
from tools.day6_bokeh_line import bokeh_line

Session = sessionmaker(bind=engine)


def show_speed_from_db(minutes=10):
    """从 SQLite 读取最近 N 分钟数据, 用 Numpy 向量化计算速率, Bokeh 出图。"""
    session = Session()
    cutoff = datetime.now() - timedelta(minutes=minutes)

    combos = (session.query(InterfaceMonitor.device_ip, InterfaceMonitor.interface_name)
              .distinct().all())

    in_speed_lines  = []
    out_speed_lines = []

    for device_ip, interface_name in combos:
        records = (session.query(InterfaceMonitor)
                   .filter(InterfaceMonitor.device_ip == device_ip,
                           InterfaceMonitor.interface_name == interface_name,
                           InterfaceMonitor.record_datetime >= cutoff)
                   .order_by(InterfaceMonitor.record_datetime)
                   .all())

        if len(records) < 2:
            print(f"[!] {device_ip} {interface_name}: 数据点不足 2 个, 跳过")
            continue

        # ---- 关注点1: 转换为 Numpy 数组, 用 np.diff 计算增量 ----
        in_arr   = np.array([r.in_bytes for r in records],  dtype=np.int64)
        out_arr  = np.array([r.out_bytes for r in records], dtype=np.int64)
        # datetime64[s]: 以秒为单位存储时间, diff 后直接得到秒数的 int64
        time_arr = np.array([r.record_datetime for r in records], dtype='datetime64[s]')

        # np.diff([10, 20, 35]) → array([10, 15])
        diff_in   = np.diff(in_arr)
        diff_out  = np.diff(out_arr)
        # np.diff 对 datetime64[s] 返回 timedelta64[s], astype(int64) 得到总秒数
        # 注意: 不能用 .seconds 属性! 它只返回 0~86399 的分量, 跨分钟边界时会算错
        diff_secs = np.diff(time_arr).astype(np.int64)

        # ---- 关注点2: 全向量化计算 kbps + 数据清洗 (无 Python for 循环) ----
        # 公式: (字节增量 × 8) / (1000 × 秒数) = kbps
        # valid 布尔掩码: diff_secs > 0 防除零; diff > 0 过滤计数器翻转负值
        valid = (diff_secs > 0) & (diff_in > 0) & (diff_out > 0)

        in_kbps  = np.round((diff_in[valid]  * 8) / (1000 * diff_secs[valid]), 2)
        out_kbps = np.round((diff_out[valid] * 8) / (1000 * diff_secs[valid]), 2)

        # diff 结果比原数组少一个, +1 对齐; 再用 valid 掩码筛选时间点
        clean_times = np.array([r.record_datetime for r in records[1:]])[valid].tolist()
        clean_in    = in_kbps.tolist()
        clean_out   = out_kbps.tolist()

        if not clean_times:
            print(f"[!] {device_ip} {interface_name}: 清洗后无有效数据点")
            continue

        label = f"{device_ip}:{interface_name}"
        in_speed_lines.append([clean_times, clean_in,  f"RX:{label}"])
        out_speed_lines.append([clean_times, clean_out, f"TX:{label}"])
        print(f"[*] {label}: {len(clean_times)} 个有效速率点")

    session.close()

    if in_speed_lines:
        bokeh_line(in_speed_lines,  title='接口入向速率 (RX)')
    if out_speed_lines:
        bokeh_line(out_speed_lines, title='接口出向速率 (TX)')


if __name__ == '__main__':
    show_speed_from_db(minutes=10)