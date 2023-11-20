import behave
import time
import subprocess
import os
import signal


def before_all(context):
    context.proc = subprocess.Popen(["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
                                    preexec_fn=os.setsid)
    time.sleep(5)


def after_all(context):
    os.killpg(os.getpgid(context.proc.pid), signal.SIGTERM)
