from flask import jsonify, request, send_file, Response, render_template, current_app
from flask import Blueprint
import time
import datetime
import os
import requests
import time
from pathlib import Path
from flask import render_template, jsonify, request
import traceback
from config import ASSETS_PATH
from models import db, Video, CommonJob
from _utils import report_job
from algorithm_model.subtitle_extraction import get_scan_status, scan_frame
from script_clip.main import ffmpeg
from algorithm_model.baidu_translate import translate_text, Lang

scanned_files = 0
all_files = 0
main_bp = Blueprint('main', __name__)


@main_bp.route('/home')
def home():
    return render_template('home.html')


@main_bp.route('/clip')
def clip():
    return render_template('clip.html')


@main_bp.route('/search')
def search():
    return render_template('search.html')


@main_bp.route('/subtitle-blur')
def upload():
    return render_template('blur.html')


@main_bp.route('/subtitle-remove')
def rem():
    return render_template('rem.html')


@main_bp.route('/subtitle-extract')
def ext():
    return render_template('ext.html')


@main_bp.route('/subtitle-translate')
def translate():
    return render_template('translate.html')


@main_bp.route('/script-generate')
def script():
    return render_template('script.html')


@main_bp.route('/img2video')
def img2video():
    return render_template('img2video.html')


@main_bp.route('/split')
def split():
    return render_template('split.html')


@main_bp.route('/actor')
def actor():
    return render_template('actor.html')

@main_bp.route('/actorv2')
def actorv2():
    return render_template('actorv2.html')


@main_bp.route('/tts')
def tts():
    return render_template('tts.html')

@main_bp.route('/tti')
def tti():
    return render_template('tti.html')

@main_bp.route('/')
def run():
    return render_template('clip.html')


@main_bp.route('/login')
def login():
    return render_template('login.html')

@main_bp.route('/videodetect')
def videodetect():
    return render_template('videodetect.html')

@main_bp.route('/get-tts', methods=['GET'])
def amain():
    text = '我的笑声能绕地球三圈，不信你听！哈哈哈哈哈哈'
    speed = request.args.get('speed', 30)
    def tts_openai(speak):
        from openai import OpenAI
        client = OpenAI(
            api_key="xxx",
            base_url="",
            max_retries=3,
        )
        if float(speed) > 0:
            speed1 = 1 * float(speed) / 12.5
        if float(speed) < 0:
            speed1 = 1 / -float(speed) / 12.5
        if float(speed) == 0:
            speed1 = 1
        response = client.audio.speech.create(
            model="tts",
            voice=speak,
            input=text,
            speed=speed1
        )
        yield response.content

    voice = request.args.get('voice', "")
    if voice.startswith("openai"):
        speaker = voice.split("-")[-1]
        return Response(tts_openai(speaker), mimetype='audio/mp3')

    import edge_tts

    """Main function"""
    speaker = voice
    text_split = text
    if 'FR' in speaker:
        text_split = translate_text(text_split, to=Lang.FRA)
    elif 'RU' in speaker:
        text_split = translate_text(text_split, to=Lang.RU)
    elif 'US' in speaker or 'GB' in speaker:
        text_split = translate_text(text_split, to=Lang.EN)
    elif 'DE' in speaker:
        text_split = translate_text(text_split, to=Lang.DE)
    elif 'KR' in speaker:
        text_split = translate_text(text_split, to=Lang.KOR)
    elif 'JP' in speaker:
        text_split = translate_text(text_split, to=Lang.JP)
    elif speaker.startswith("ar"):
        # 阿拉伯语
        text_split = translate_text(text_split, to=Lang.ARA)
    elif speaker.startswith("es"):
        # 西班牙语
        text_split = translate_text(text_split, to=Lang.SPA)
    elif speaker.startswith("pt"):
        # 葡萄牙语
        text_split = translate_text(text_split, to=Lang.PT)
    else:
        text_split = text
    communicate = edge_tts.Communicate(text_split, voice, rate=f'+{speed}%')

    def tts():
        for chunk in communicate.stream_sync():
            if chunk['type'] == 'audio':
                yield chunk['data']
            elif chunk['type'] == 'WordBoundary':
                pass

    return Response(tts(), mimetype='audio/mp3')
