## 使用基础镜像
FROM python:3.12
WORKDIR /tv
COPY requirements.txt .
# 设置默认的源地址为 PyPI 官方源
ARG PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
# 使用 ARG 定义的变量作为 pip 源地址
RUN python3 -m venv .venv && .venv/bin/pip install --no-cache-dir -r requirements.txt -i ${PIP_INDEX_URL}

FROM python:3.12-slim
WORKDIR /tv
COPY --from=builder /tv/.venv /tv/.venv
COPY run.py .
COPY /data ./data
EXPOSE 80
ENTRYPOINT ["/tv/.venv/bin/python3", "run.py"]