import datetime
import os
import psutil
import requests
import sys
import threading
import time
from pathlib import Path
from flask import Flask, render_template, jsonify, request
import webview
import traceback
from config import PORT, HOST
from models import (
    db,
)

from waitress import serve
import site
from _utils import report_job, set_window


def get_current_directory():
    path = os.getcwd()
    return path

def get_user_home_app_dir() -> str:
    home_path = os.path.expanduser('~')
    app_path = os.path.join(home_path, '.imnight_aigc')
    return app_path

ffmpeg_path = os.path.join(
    os.path.dirname(__file__), 'ffmpeg', 'ffmpeg.exe'
)
os.environ['IMAGEIO_FFMPEG_EXE'] = ffmpeg_path
if getattr(sys, 'frozen', False):
    # 应用已被打包
    meipass = getattr(sys, '_MEIPASS')
    site.USER_SITE = os.path.join(meipass, 'site-packages')
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    app = Flask(__name__, template_folder=template_folder)
else:
    # 应用未被打包
    app = Flask(__name__)


from cron import (  # noqa: E402
    scheduler,
    process_clip_job,
)
from api.common import common_bp
from api.common_job import common_job_bp
from api.main import main_bp

app.jinja_env.variable_start_string = '[['
app.jinja_env.variable_end_string = ']]'
app.jinja_env.block_start_string = '[%'
app.jinja_env.block_end_string = '%]'

home_app_dir = get_current_directory()
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{home_app_dir}/video.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
# print("调皮的Macos偷偷给程序重启了一次")

# 路由分组
app.register_blueprint(common_bp)
app.register_blueprint(common_job_bp)
app.register_blueprint(main_bp)

# 定时任务
scheduler.init_app(app)
scheduler.add_job(
    'process_clip_job',
    process_clip_job,
    trigger='interval',
    seconds=3,
    max_instances=2,
)

# 启动调度器
scheduler.start()

with app.app_context():
    from models import CommonJob
    db.create_all()
    running_common_jobs = CommonJob.query.all()
    # 删除全部
    for common_job in running_common_jobs:
        db.session.delete(common_job)
    db.session.commit()

def run_flask():
    serve(app, host=HOST, port=PORT)


import os
import signal

# 获取当前进程的PID
current_pid = os.getpid()

# 获取当前进程的父进程PID
parent_pid = os.getppid()


# 结束当前进程及其所有子进程
def kill_process_tree(pid, sig=signal.SIGTERM):
    try:
        # 发送信号给当前进程
        os.kill(pid, sig)
    except OSError:
        pass  # 进程可能已经结束
    try:
        # 获取当前进程的所有子进程
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        for child in children:
            kill_process_tree(child.pid, sig)
    except psutil.NoSuchProcess:
        pass  # 进程不存在


# 调用函数结束当前进程及其所有子进程
def run_webview():
    # 设置窗口的宽度和高度
    width = 1400  # 您希望的窗口宽度
    height = 900  # 您希望的窗口高度
    menu_items = [
        wm.Menu(
            '重新加载',
            [
                wm.MenuAction('重新加载窗口', reload_window),
            ],
        ),
    ]
    _window = webview.create_window(
        '智能视频剪辑工具',
        f'http://{HOST}:{PORT}',
        width=width,
        height=height,
    )
    _window.events.closed += on_closed

    set_window(_window)
    webview.start(
        menu=menu_items,
        private_mode=False,
        # debug=True,
    )
    return _window


import webview.menu as wm


def reload_window():
    from _utils import get_window

    window = get_window()
    window.load_url(f'http://{HOST}:{PORT}')


def on_closed():
    scheduler.shutdown(wait=False)
    print('窗口程序退出')
    kill_process_tree(current_pid)
    raise Exception('窗口程序退出')
    sys.exit(0)


if __name__ == '__main__':
    # 在主线程中启动 Flask，并在另一个线程中启动 webview
    window = None
    try:
        # 测试 8001端口是否有响应 http://127.0.0.1:8001/
        runed = False
        try:
            resp = requests.get('http://127.0.0.1:8001/')
            if resp.status_code == 200:
                runed = True
        except:
            print('服务已经启动')
            pass
        if not runed:
            flask_thread = threading.Thread(target=run_flask)
            flask_thread.daemon = True
            flask_thread.start()
            print('服务成功启动')

            window = run_webview()

    except Exception as e:
        print(e)
        print('程序退出')
        scheduler.shutdown()
        sys.exit(0)
