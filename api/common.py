import json
from flask import jsonify, request, send_file, Response
from flask import Blueprint
from config import CURRENT_VERSION, BASE_API_HOST
import requests
from _utils import get_window, load_text_from_path
from subtitle import Subtitle
from openai import OpenAI
from datetime import datetime
common_bp = Blueprint("common", __name__)

# BASE_API_HOST = "http://127.0.0.1:5000"


@common_bp.route("/check-version/")
def get_latest_version():
    current_version = CURRENT_VERSION
    payload = json.dumps(
        {
            "path": "aigc_app_versions__get_latest_version",
            "parameter": {"app_name": "AIGC剧集工具"},
        }
    )
    headers = {"Content-Type": "application/json"}
    url = BASE_API_HOST + "//root"
    try:
        response = requests.request(
            "POST", url, headers=headers, data=payload, timeout=10
        )
        version_info = response.json().get("data", {})
        version_info["cur_version"] = current_version
        return jsonify({"version_info": version_info, "code": 200, "msg": "ok"})
    except:
        return {"code": 500, "msg": "检查更新失败"}


@common_bp.route("/open-url/", methods=["POST"])
def open_url():
    data = request.json
    url = data.get("url")
    if url:
        import webbrowser

        webbrowser.open(url)
        return jsonify({"code": 200, "url": url, "msg": "ok"})
    return jsonify({"code": 400, "msg": "url is required"})


@common_bp.route("/select-file/", methods=["GET"])
def select_file():
    from webview import OPEN_DIALOG

    window = get_window()
    file_type = request.args.get("file_types")
    file_types = (file_type,) if file_type else tuple()  # 设置文件类型过滤器
    result = window.create_file_dialog(
        dialog_type=OPEN_DIALOG,
        directory="",
        allow_multiple=False,
        save_filename="",
        file_types=file_types,
    )
    filepath = result[0] if result else ""
    return {"code": 200, "msg": "ok", "filepath": filepath}


@common_bp.route("/select-folder/", methods=["GET"])
def select_folder():
    from webview import FOLDER_DIALOG

    window = get_window()
    result = window.create_file_dialog(
        dialog_type=FOLDER_DIALOG,
        directory="",
        allow_multiple=False,
        save_filename="actor_detect.csv",
        file_types=(),
    )
    folder = result[0] if result else ""
    return {"code": 200, "msg": "ok", "filepath": folder}


@common_bp.route("/get-file-chunk/")
def video():
    file_path = request.args.get("filepath")

    def generate(file_path):
        if not file_path:
            return Response("", status=404)
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(1024 * 1024 * 100)  # 10KB
                if not chunk:
                    break
                yield chunk

    return Response(generate(file_path), mimetype="video/mp4")


@common_bp.route("/get-file/")
def get_file_total():
    file_path = request.args.get("filepath")
    return (
        send_file(file_path, mimetype="video/mp4")
        if file_path
        else Response("", status=404)
    )


@common_bp.route("/get-pic/")
def get_file_pic():
    file_path = request.args.get("filepath")
    return (
        send_file(file_path, mimetype="image/jpg")
        if file_path
        else Response("", status=404)
    )


@common_bp.route("/get-srt/", methods=["POST"])
def get_text():
    input_path = request.json.get("input_path")
    output_path = request.json.get("output_path")
    input_text = load_text_from_path(input_path)

    input_subtitle = Subtitle(user_id="")
    input_subtitle.read_srt(input_text)

    captions = [
        {
            "index": subtitle.index,
            "text": subtitle.text,
            "time": subtitle.time,
            "startTime": subtitle.time.split("-->")[0].strip(),
            "translateText": "",
        }
        for subtitle in input_subtitle.captions
    ]
    if output_path:
        try:
            output_text = load_text_from_path(output_path)
            output_subtitle = Subtitle(user_id="")
            output_subtitle.read_srt(output_text)
            for idx, oup in enumerate(captions):
                captions[idx]["translateText"] = (
                    output_subtitle.captions[idx].text
                    if idx < len(output_subtitle.captions)
                    else ""
                )
        except:
            import traceback

            return {"code": 500, "msg": traceback.format_exc()}
    return {"code": 200, "msg": "ok", "captions": captions}


@common_bp.route("/torch-enabled/")
def enable_torch():
    import torch

    enabled = torch.cuda.is_available()
    return {"code": 200, "msg": "ok", "enabled": enabled}

@common_bp.route('/split-text/', methods=['POST'])
def split_text():
    text = request.json.get('text', '')
    chunksize = request.json.get('chunksize', 1000)
    from _utils import split_text
    texts = split_text(text, chunksize)
    results = []
    for text in texts:
        result = text.lstrip(",").lstrip("，").lstrip("。").lstrip("！").lstrip("？").lstrip("：").lstrip(".").lstrip("...").lstrip()
        if result:
            results.append(result)
    return {"code": 200, "msg": "ok", "texts": results}