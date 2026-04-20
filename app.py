from dotenv import load_dotenv
import os

load_dotenv()

if (flask_debug := os.environ.get("FLASK_DEBUG", "0")) and flask_debug.lower() in {
        "false",
        "0",
        "no",
    }:
    from gevent import monkey  # type: ignore

    # gevent
    monkey.patch_all()

    from grpc.experimental import gevent as grpc_gevent  # type: ignore

    # grpc gevent
    grpc_gevent.init_gevent()

    import psycogreen.gevent  # type: ignore

    psycogreen.gevent.patch_psycopg()

from app_factory import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)