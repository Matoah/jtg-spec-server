# ===== 构建阶段 =====
FROM python:3.12-slim AS builder

WORKDIR /app

# 安装依赖到 site-packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    -i https://pypi.tuna.tsinghua.edu.cn/simple

# ===== 运行阶段 =====
FROM python:3.12-slim

WORKDIR /app

# 安装 curl（供 healthcheck 使用）并创建非 root 用户
RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/* && \
    useradd --create-home appuser

# 从构建阶段复制已安装的包
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 复制项目文件
COPY . .

# 切换到非 root 用户
USER appuser

# 对外暴露端口（默认 5002，可通过 PORT 环境变量覆盖）
EXPOSE 5002

# 使用 Gunicorn 启动
CMD ["sh", "-c", "gunicorn app:app -b 0.0.0.0:${PORT:-5002}"]
