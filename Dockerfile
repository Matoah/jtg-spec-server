# 使用 Python 3.12 作为基础镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . .

# 安装系统依赖（如果需要）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口
EXPOSE 5002

# 定义环境变量
ENV FLASK_APP=app.py
ENV FLASK_DEBUG=0

# 启动应用
CMD ["python", "app.py"]