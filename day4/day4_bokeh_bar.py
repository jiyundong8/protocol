from bokeh.plotting import figure, output_file, save
from bokeh.models import HoverTool, DatetimeTickFormatter, ColumnDataSource
import os
from pathlib import Path

OUTPUTS_DIR = Path(__file__).resolve().parent.parent / 'outputs'


def bokeh_bar(time_list, value_list, line_name,
            title='CPU利用率柱状图测试', y_label='利用率 (%)', save_name=None):
    """使用 Bokeh 绘制时间序列柱状图 (单设备单指标随时间变化)。"""
    # 根据相邻时间间隔, 自动计算柱宽 (取间隔的 60%, 单位毫秒)
    if len(time_list) > 1:
        delta_ms = (time_list[1] - time_list[0]).total_seconds() * 1000 * 0.6
    else:
        delta_ms = 30000

    source = ColumnDataSource(data={
        'time': time_list,
        'time_str': [t.strftime("%Y-%m-%d %H:%M:%S") for t in time_list],
        'value': value_list
    })

    p = figure(height=400, width=700, title=f"{title} - {line_name}",
            x_axis_type="datetime", x_axis_label='时间', y_axis_label=y_label,
            y_range=(0, 100))
    p.vbar(x='time', top='value', source=source, width=delta_ms,
        color="#e84d60", alpha=0.8, legend_label=line_name)

    hover = HoverTool(tooltips=[("时间", "@time_str"), ("值", "@value%")])
    p.add_tools(hover)

    p.xaxis.formatter = DatetimeTickFormatter(
        minutes="%H:%M", hours="%H:%M", days="%m-%d")
    p.legend.location = "top_right"

    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    output_filename = save_name if save_name else str(OUTPUTS_DIR / f"{title}.html")
    output_file(output_filename, title=title)
    save(p)
    print(f"[*] Bokeh 柱状图已生成: {output_filename}")

if __name__ == "__main__":
    from datetime import datetime,timedelta
    now = datetime.now()
    time_list = [now+timedelta(minutes=i) for i in range(9)]
    value_list = [54,52,24,53,44,8,59,60,36]

    bokeh_bar(time_list,value_list,"R1 CPU")