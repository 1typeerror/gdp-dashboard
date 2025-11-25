"""
处理温度文件仪数据
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
st.set_page_config(
    page_title="巡检仪小工具",
    page_icon="🧊",
    initial_sidebar_state="expanded",
)
uploaded_file = st.text_input('请输入文件路径', value=r'D:\文档\桌面\温度79.XLS')
# 假设文件路径正确且文件存在
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, skiprows=2, encoding='ISO-8859-1', sep='\t')  # 跳过前两行标题
    df.drop(['Group1', 'Group2', 'Group3', 'Group4'], axis=1, inplace=True)
    df = df.iloc[:-1, :33]

    # 数据预处理
    df.columns = df.columns.str.strip()  # 去除列名空格
    df.replace(['Over', 'None'], pd.NA, inplace=True)  # 统一缺失值标记
    # df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S').dt.time
    # 将时间转换为 datetime 类型
    df['Time'] = pd.to_datetime(df['Time'].astype(str))
    # 计算当前时间减去第一行时间的差值（以秒为单位）
    df['Cumulative_Time'] = (df['Time'] - df['Time'].iloc[0]).dt.total_seconds()

    # 转换为 timedelta 类型并格式化为 HH:MM:SS
    df['Cumulative_Time'] = pd.to_timedelta(df['Cumulative_Time'], unit='s')
    df['Cumulative_Time'] = df['Cumulative_Time'].dt.components.apply(
        lambda x: f"{int(x.hours):02}:{int(x.minutes):02}:{int(x.seconds):02}", axis=1
    )
    st.data_editor(df)

    selected_curves = st.multiselect("选择要绘制的曲线，CH1.1是2组，类推", options=df.columns)
    text_in = st.text_input('名称修改（用英文逗号分隔）')

    fig = go.Figure()

    # 将用户输入的名称分割成列表
    name_list = text_in.split(',') if text_in else []

    for i, curve in enumerate(selected_curves):
        # 确保索引不越界
        name = name_list[i].strip() if i < len(name_list) else curve
        fig.add_trace(go.Scatter(x=df['Cumulative_Time'], y=df[curve], mode='lines', name=name,
                                 line=dict(color=px.colors.qualitative.D3[i % len(px.colors.qualitative.Plotly)])
                                 # 使用默认颜色
                                 ))  # 使用默认颜色
    fig.update_layout(title="温升曲线", xaxis_title="时间", yaxis_title="温度")
    c_name = st.text_input('表格名称')
    ck = st.checkbox('保存图表')
    if ck:
        if c_name:  # 检查名称是否为空
            try:
                pio.write_html(fig, f'{c_name}.html', config={'displaylogo': False})
                st.success(f"图表已保存为 {c_name}.html")
            except Exception as e:
                st.error(f'保存图表时发生错误: {e}')
        else:
            st.error('请输入有效的名称')
    if c_name:
        fig.update_layout(title=c_name)
    st.plotly_chart(fig, use_container_width=True)
