## 使用基础镜像
FROM python:3.12 as live-tv-source
WORKDIR /tv
COPY requirements.txt .
# 设置默认的源地址为 PyPI 官方源
ARG PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
# 使用 ARG 定义的变量作为 pip 源地址
RUN python3 -m venv .venv && .venv/bin/pip install --no-cache-dir -r requirements.txt -i ${PIP_INDEX_URL}

FROM python:3.12-slim
#RUN cp /etc/apt/sources.list /etc/apt/sources.list.bak
ADD sources.list /etc/apt/
# 安装 Chrome 和 ChromeDriver
RUN apt-get update && apt-get install -y chromium chromium-driver
# 设置环境变量，指定 ChromeDriver 的路径
ENV CHROME_DRIVER_PATH /usr/lib/chromium/chromedriver
WORKDIR /tv
COPY --from=live-tv-source /tv/.venv /tv/.venv
COPY run.py .
COPY ./data ./data
ENTRYPOINT ["/tv/.venv/bin/python3", "run.py"]