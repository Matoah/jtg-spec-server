import time
from spec_app import SpecApp
import logging
import os
from configs import spec_server_config
from contexts.wrapper import RecyclableContextVar

def _create_flask_app_with_configs() -> SpecApp:
    """
        创建 Flask 应用实例
        并加载环境变量中的配置项
    """
    dify_app = SpecApp("公路工程-标准规范-服务")
    dify_app.config.from_mapping(spec_server_config.model_dump())

    # add before request hook
    @dify_app.before_request
    def before_request():
        # add an unique identifier to each request
        RecyclableContextVar.increment_thread_recycles()
        pass

    return dify_app

def _initialize_extensions(app: SpecApp):
    from extensions import (
        ext_blueprints,
        ext_celery,
        ext_logging,
        ext_timezone,
    )

    extensions = [
        ext_timezone,
        ext_logging,
        ext_celery,
        ext_blueprints
    ]
    mode = os.environ.get('MODE', 'api')
    # 保证异步的时候不加载
    # 注意：调度器现在在独立的 scheduler 服务中运行，不在 api 服务中加载
    # 避免 Gunicorn 多 Worker 导致定时任务重复执行
    for ext in extensions:
        short_name = ext.__name__.split(".")[-1]
        is_enabled = ext.is_enabled() if hasattr(ext, "is_enabled") else True
        if not is_enabled:
            if spec_server_config.DEBUG:
                logging.info(f"忽略插件： {short_name}")
            continue
        start_time = time.perf_counter()
        ext.init_app(app)
        end_time = time.perf_counter()
        if spec_server_config.DEBUG:
            logging.info(
                f"插件【{short_name}】完成，耗时： ({round((end_time - start_time) * 1000, 2)} ms)"
            )

def create_app():
    start_time = time.perf_counter()
    app = _create_flask_app_with_configs()
    _initialize_extensions(app)
    end_time = time.perf_counter()
    if spec_server_config.DEBUG:
        logging.info(
            f"服务启动完成，耗时： ({round((end_time - start_time) * 1000, 2)} ms)"
        )
    return app