import behave
import time
import subprocess
import os
import signal
from unit_tests.testAPI import API

def before_all(context):
    context.proc = subprocess.Popen(["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
                                    preexec_fn=os.setsid)
    time.sleep(5)


def after_all(context):
    os.killpg(os.getpgid(context.proc.pid), signal.SIGTERM)


def before_scenario(context, scenario):
    DEBUG_HEADERS = {
        "accept": "application/json"
    }
    context.api = API(DEBUG_HEADERS)

