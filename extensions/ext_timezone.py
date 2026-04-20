import os
import time

from spec_app import SpecApp


def init_app(app: SpecApp):
    os.environ["TZ"] = "UTC"
    # windows platform not support tzset
    if hasattr(time, "tzset"):
        time.tzset()
