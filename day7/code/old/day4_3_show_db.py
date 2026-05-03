from datetime import datetime,timedelta
from collections import defaultdict
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

#from bokeh.plotting import figure,output_file,save
#from bokeh.models import DatetimeTickFormatter

from day4_1_create_db import RouterMonitor
from tools.day4_bokeh_line import bokeh_line

#数据库路径
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "sqlalchemy_syslog_sqlite3.db"

engine = create_engine(f"sqlite:///{DB_PATH}")
Session = sessionmaker(bind=engine)
db = Session()

#查询最近一小时
one_hour_ago = datetime.now() - timedelta(hours=1)

records = db.query(RouterMonitor)\
    .filter(RouterMonitor.record_datetime >= one_hour_ago)\
    .order_by(RouterMonitor.record_datetime.desc())\
    .all()

#按IP分组
data_by_ip = defaultdict(list)

for r in records:
    mem_usage = r.mem_use / (r.mem_use + r.mem_free) * 100

    data_by_ip[r.device_ip].append({
        "time": r.record_datetime,
        "cpu": r.cpu_usage_percent,
        "mem": mem_usage
    })
for ip in data_by_ip:
    data_by_ip[ip] = data_by_ip[ip][-10:]    

#输出读取情况
for ip,data in data_by_ip.items():
    print(f"[*] {ip}: 读取 {len(data)}条记录")

#创建输出目录
output_dir = BASE_DIR / "outputs"
output_dir.mkdir(exist_ok=True)

#===================CPU图==================
cpu_lines = []

for ip,data in data_by_ip.items():
    times = [d["time"] for d in data]
    cpu_vals = [d["cpu"] for d in data]

    cpu_lines.append([times,cpu_vals,ip])

bokeh_line(
    cpu_lines,
    title = "CPU利用率趋势",
    y_label="利用率（%)",
    save_name=str(output_dir / "CPU利用率趋势.html")
)

# ================= 内存图 =================
mem_lines = []

for ip, data in data_by_ip.items():
    times = [d["time"] for d in data]
    mem_vals = [d["mem"] for d in data]

    mem_lines.append([times, mem_vals, ip])

bokeh_line(
    mem_lines,
    title="内存利用率趋势",
    y_label="利用率 (%)",
    save_name=str(output_dir / "内存利用率趋势.html")
)


db.close()