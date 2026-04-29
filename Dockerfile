# ---- 基础准备 ----
# 使用官方轻量级 Python 镜像
FROM python:3.12-slim as builder

# 设置工作目录
WORKDIR /app

# ---- 依赖安装 ----
# 1. 创建非 root 用户，提升安全性[reference:0]
# 2. 先复制依赖列表（这是 Docker 分层优化的关键）
# 3. 安装依赖，使用国内镜像源加速
COPY requirements.txt .
RUN useradd --create-home appuser && \
    pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# ---- 正式运行 ----
# 复制项目所需的所有文件
COPY . .

# 切换到非 root 用户
USER appuser

# 对外暴露的端口，与 Gunicorn 配置文件中的端口保持一致，默认为 5002[reference:1]
EXPOSE 5002

# 使用 Gunicorn 作为生产级 WSGI 服务器启动应用[reference:2]
# 'app:app' 中的第一个 app 是启动文件名 app.py，第二个是 Flask 实例名
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:5002"]