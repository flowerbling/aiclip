import sys
import cv2
import base64
from tqdm import tqdm
from models import db
from models import (
    JobStatus,
    db,
    CommonJob,
)
import edge_tts
import os
from datetime import datetime, timedelta
from flask_apscheduler import APScheduler
import platform
from enum import Enum
from _utils import *
from models import JobStatus
from models import CommonJob, db
import requests
from _utils import replace_ext
from _utils import get_video_info
from algorithm_model.subtitle_extraction import start_scan
from script_clip.main import ScriptClip
from datetime import datetime, timedelta
import traceback

style_map = {
    "幽默风趣": "你的解说很逗比,让人捧腹大笑",
    "严肃庄重": "严肃,庄重,一字一句都有威严",
    "富有哲学": "字句都让人思考中寻找答案，又在每一个答案中发现新的问题",
    "充满诗意": "腹有诗书气自华,文字如花瓣般缓缓飘落，在心灵深处绽放出温柔的芬芳",
    "讽刺讥讽": "通过讽刺和夸张的手法来评论剧中的不合理或过于狗血的情节，让观众在笑声中进行思考。",
}


system = platform.system()
if system == "Darwin":
    encoding = "utf-8"
elif system == "Windows":
    encoding = "gbk"

scheduler = APScheduler()

CLEAR_RUNNING = False
BLUR_RUNNING = False


class ClipJobStage(int, Enum):
    ASR = 2
    LLM = 3
    CLIP = 4
    FINISH = 5


def process_clip_job():
    with scheduler.app.app_context():
        running_count = (
            db.session.query(CommonJob)
            .filter(
                CommonJob.job_type == "clip",
                CommonJob.status == JobStatus.RUNNING,
                CommonJob.start_at > datetime.now() - timedelta(minutes=60),
            )
            .count()
        )
        if running_count > 2:
            return

        queued = (
            db.session.query(CommonJob)
            .filter(CommonJob.status == JobStatus.QUEUED, CommonJob.job_type == "clip")
            .first()
        )
        if not queued:
            return
        job = queued
        input_path = job.params.get("input_path", "")
        stage = job.params.get("step", 0)
        srtpath = job.params.get("srtpath", "")
        context = job.params.get("context", "")
        script = job.params.get("script", "")
        style_config = job.params.get("style", "幽默风趣")
        apikey = job.params.get("apikey", "")
        apibase = job.params.get("apibase", "")
        model = job.params.get("model", "gpt-4o")
        uid = job.params.get("user_id", "")
        ctype = job.params.get("ctype", "1")
        job.start_at = datetime.now()
        if not uid:
            uid = job.params.get("uid", "")

        style = style_map.get(style_config)
        params = job.params.copy()
        try:
            if stage == ClipJobStage.ASR:
                srtpath = replace_ext(input_path, "srt")
                if not os.path.exists(srtpath):
                    start_scan(input_path)
                videoinfo = get_video_info(input_path)
                params["videoinfo"] = videoinfo
                params["srtpath"] = srtpath

            if stage == ClipJobStage.LLM:
                script = ScriptClip().script_split(
                    srtpath,
                    input_path,
                    style,
                    context[:4000],
                    script=script[:4000],
                    user_id=uid,
                    apibase=apibase,
                    apikey=apikey,
                    model=model,
                    ctype=ctype,
                )
                params["script_data"] = script

            if stage == ClipJobStage.CLIP:
                output_path = ScriptClip().clip(params)
                result = job.result.copy()
                result["output_path"] = output_path
                job.result = result

            job.status = JobStatus.FINISHED
            job.end_at = datetime.now()
            job.params = params
        except Exception as e:
            print(e)
            result = job.result.copy()
            job.end_at = datetime.now()
            result["detail"] = e.__str__()
            import traceback

            traceback.print_exc()

            job.result = result
            job.params = params
            job.status = JobStatus.FAILED
            # print(job)
        finally:
            db.session.commit()
