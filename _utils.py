import re
from datetime import datetime
import requests
import json
from config import BASE_API_HOST
import sys
import platform
from webview import Window
import os
from http import HTTPStatus
from urllib.parse import urlparse, unquote
from pathlib import PurePosixPath


WINDOW: Window = None

# BASE_API_HOST = "http://127.0.0.1:5000"


def open_url(url: str):
    """打开浏览器访问指定url"""
    import webbrowser

    webbrowser.open(url)


def extract_subtitles_from_srt(file_path: str) -> list[str]:
    """从字幕srt文件中提取字幕内容

    Args:
        file_path (str): srt 文件路径

    Returns:
        list[str]: 字幕文字列表
    """
    subtitles = []
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
        # 使用正则表达式匹配字幕内容
        subtitle_entries = re.findall(
            r'\d+\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n([^\n]+)\n\n',
            text,
        )
        subtitles.extend(subtitle_entries)
    return subtitles


def extract_subtitles_from_srt_text(text: str) -> list[str]:
    """从字幕srt文件中提取字幕内容

    Args:
        text (str): srt 文本

    Returns:
        list[str]: 字幕文字列表
    """
    subtitles = []
    subtitle_entries = re.findall(
        r'\d+\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n([^\n]+)\n\n', text
    )
    subtitles.extend(subtitle_entries)

    if not subtitles:
        # 用\r\n分割
        subtitle_entries = re.findall(
            r'\d+\r\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\r\n([^\r\n]+)\r\n\r\n',
            text,
        )
        subtitles.extend(subtitle_entries)
    return subtitles


# @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def chat_openai(
    prompt: str, user_id: str = '', model='gpt-4-32k', timeout=120
) -> str | None:
    """调用 open ai 接口进行对话."""

    try:
        from openai import OpenAI

        max_token = 10000
        if model.startswith('gpt-3.5'):
            max_token = 2000
        if model.startswith('gpt-4o'):
            max_token = 2000
        client = OpenAI(
            api_key='sk-',
            base_url='',
            max_retries=3,
            timeout=timeout,
        )
        start = datetime.now()

        if model.startswith('qwen'):
            model = 'qwen2-72b-instruct'
            api_base = 'https://dashscope.aliyuncs.com/compatible-mode/v1'
            api_key = 'sk-'
            client = OpenAI(
                api_key=api_key,
                base_url=api_base,
                max_retries=3,
                timeout=timeout,
            )
            max_token = 6000
            response = client.chat.completions.create(
                model=model,
                messages=[{'role': 'user', 'content': prompt}],
                temperature=0.8,
                max_tokens=max_token,
            )
        else:
            response = client.chat.completions.create(
                model=model,
                messages=[{'role': 'user', 'content': prompt}],
                temperature=0.8,
                max_tokens=max_token,
            )
        choice = response.choices[0]
        result = choice.message.content
        if logger:
            logger.info(
                f'end chat openai. model: {model}. result: {result}. cost: {datetime.now() - start}'
            )
        try:
            report_token_usage(
                model=model,
                input_tokens=response.usage.prompt_tokens,
                output_tokens=response.usage.completion_tokens,
                input_str=prompt,
                output_str=result,
                user_id=user_id,
            )
        except:
            if logger:
                logger.error('report token usage error')

        if result:
            return result
        if choice.finish_reason == 'content_filter':
            raise ValueError('调用 open ai 接口返回内容被过滤')
    except Exception as e:
        print(e)
        if logger:
            logger.error(f'chat openai error: {e}')
        raise e

    return None


def get_text_hash(text: str) -> str:
    """计算文本的哈希值"""
    import hashlib

    return hashlib.md5(text.encode()).hexdigest()


def load_text_from_file(file_path: str) -> str:
    """从文件中加载文本内容"""
    text = ''
    aigc_path = getattr(sys, 'AIGCPATH') + '/' if hasattr(sys, 'AIGCPATH') else ''
    try:
        with open(aigc_path + file_path, 'r', encoding='utf-8') as file:
            text = file.read()
    except:
        with open(aigc_path + file_path, 'r', encoding='gbk') as file:
            text = file.read()
    return text


def load_text_from_path(file_path: str) -> str:
    text = ''
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
    except:
        pass

    if not text:
        try:
            with open(file_path, 'r', encoding='gbk') as file:
                text = file.read()
        except:
            pass

    if not text:
        try:
            with open(file_path, 'r', encoding='gb1312') as file:
                text = file.read()
        except:
            pass

    if not text:
        try:
            with open(file_path, 'r', encoding='utf8') as file:
                text = file.read()
        except:
            pass
    return text


def report_token_usage(
    model: str,
    input_tokens: int,
    output_tokens: int,
    input_str: str,
    output_str: str,
    app_name: str = '华策AIGC剧集工具',
    user_id: str = '',
):
    url = f'{BASE_API_HOST}//root'

    payload = json.dumps(
        {
            'path': 'token_usages__create',
            'parameter': {
                'model_type': model,
                'app_name': app_name,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'input_str': input_str,
                'output_str': output_str,
                'user_id': user_id,
            },
            'user_id': user_id,
        }
    )
    headers = {'Content-Type': 'application/json'}
    response = requests.request('POST', url, headers=headers, data=payload)
    return response

def combine_frames_to_four_in_one(frames):
    import cv2
    import numpy as np
    if len(frames)!= 4:
        if len(frames) > 4:
            frames = frames[:4]
        else:
            frames = frames + [frames[-1]] * (4 - len(frames))

    height, width, channels = frames[0].shape
    top_row = np.hstack((frames[0], frames[1]))
    bottom_row = np.hstack((frames[2], frames[3]))
    four_in_one = np.vstack((top_row, bottom_row))
    
    four_width = width * 2
    four_height = height * 2
    # 缩放到最长边为500像素
 
    resied = cv2.resize(four_in_one, (500, (four_height * 500) // four_height))

    # print(resied.shape)
    return resied


def report_job(job_type: str, status: str, result: dict, user_id: str, start_at: str):
    params = {
        'user_id': user_id,
        'job_type': job_type,
        'start_at': start_at,
        'status': status,
        'result': result,
        'app_name': '华策AIGC剧集工具',
        'end_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }
    try:
        path = BASE_API_HOST + '//root'
        payload = json.dumps(
            {
                'path': 'aigc_app_versions__report_app_job',
                'parameter': params,
                'user_id': user_id,
            }
        )
        resp = requests.request(
            'POST', path, headers={'Content-Type': 'application/json'}, data=payload
        )
        # print(BASE_API_HOST, resp.text)
        return resp.json()
    except Exception as e:
        print('report job failed.' + e.__str__())
        return {}


def split_text(text: str, chunk_size: int = 10000) -> list[str]:
    from text_splitter import RecursiveCharacterTextSplitter

    spliter = RecursiveCharacterTextSplitter(
        separators=['。', '！', '？', '；', '…', '\n'],
        chunk_size=chunk_size,
        chunk_overlap=0,
        keep_separator=False,
    )
    result = spliter.split_text(text)
    return result


def get_encoding():
    system = platform.system()
    if system == 'Darwin':
        encoding = 'utf-8'
    elif system == 'Windows':
        encoding = 'gbk'


def set_window(_window):
    global WINDOW
    WINDOW = _window
    return WINDOW


def get_window():
    return WINDOW


def add_suffix(input_path: str, suffix: str) -> str:
    """在文件名后面添加后缀"""
    import os

    dir_name = os.path.dirname(input_path)
    base_name = os.path.basename(input_path)
    name, ext = os.path.splitext(base_name)
    return os.path.join(dir_name, f'{name}_{suffix}{ext}')


def replace_ext(input_path: str, ext: str):
    dir_name = os.path.dirname(input_path)
    base_name = os.path.basename(input_path)
    name, old_ext = os.path.splitext(base_name)
    return os.path.join(dir_name, f'{name}.{ext}')


def get_video_info(video_path):
    from moviepy.editor import VideoFileClip

    video = VideoFileClip(video_path)

    # 获取视频的总时长（秒）
    video_duration_sec = video.duration

    # 计算小时，分钟和秒
    hours = int(video_duration_sec // 3600)
    minutes = int((video_duration_sec % 3600) // 60)
    seconds = int(video_duration_sec % 60)

    # 格式化为 HH:MM:SS,MS
    # 由于不需要日期，所以不需要使用 strftime 方法
    video_duration_formatted = f'{hours:02d}:{minutes:02d}:{seconds:02d},000'

    # 视频的宽度和高度
    video_width = video.w
    video_height = video.h
    video_size = f'{video_width}x{video_height}'
    # 视频帧率
    video_fps = video.fps
    # 视频比特率
    return {
        'duration': video_duration_formatted,
        'size': video_size,
        'fps': video_fps,
    }

