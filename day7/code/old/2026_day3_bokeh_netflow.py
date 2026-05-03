import re
from tools.day3_ssh_single_cmd import ssh_run
from tools.day3_bokeh_bing import bokeh_bing


def get_netflow_app(host, username, password):
    """SSH登录路由器, 采集Netflow数据, 正则提取, 绘制Bokeh饼状图。"""
    # 1. SSH执行命令获取Netflow数据
    show_result = ssh_run(host, username, password,
                          'show flow monitor name qytang-monitor cache format table')
    #print(show_result)

    # 2. ★ 正则提取APP NAME和bytes (你需要完成这部分!)
    app_name_list = []
    app_bytes_list = []
    for line in show_result.strip().split('\n'):
        #跳过表头
        if "APP NAME" in line or "====" in line:
            continue
        match = re.match(r'^(port|layer7|prot)\s+(.+?)\s+(\d+)$',line.strip())

        if match:
            prefix = match.group(1)
            app = match.group(2)
            bytes = match.group(3)

            app_name = f"{prefix} {app}"

            app_name_list.append(app_name)
            app_bytes_list.append(int(bytes))


    # 3. 打印提取结果
    print(f"[*] 提取到 {len(app_name_list)} 条 Netflow 记录")
    for name, byt in zip(app_name_list, app_bytes_list):
        print(f"    {name:<25s} {byt} bytes")

    # 4. 调用bokeh_bing生成饼状图
    bokeh_bing(app_name_list, app_bytes_list, 'Netflow应用流量分布')


if __name__ == "__main__":
    get_netflow_app('192.168.0.89', 'admin', 'Cisco123')