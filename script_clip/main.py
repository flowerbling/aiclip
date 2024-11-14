import asyncio
import json
import os
import re
import subprocess
import time
from datetime import datetime, timedelta

import requests

from .char2voice import create_voice_srt_new2
from .chatgpt import Chat
from .conf import Config
from mutagen.mp3 import MP3
from mutagen.wave import WAVE
from random import sample
from _utils import add_suffix, replace_ext
from algorithm_model.baidu_translate import translate_text, Lang

def translate(text, languane="en"):
    result = ""
    if languane == 'en':
        result = translate_text(text, to=Lang.EN)
    if languane == 'ru':
        result = translate_text(text, to=Lang.RU)
    return result

ffmpeg = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "ffmpeg",
    "ffmpeg.exe",
)

class ScriptClip:
    def sort_by_number(self, filename):
        numbers = re.findall(r"\d+", filename)
        if numbers:
            return [int(num) for num in numbers]
        else:
            return filename

    def script_split(
        self, srt_path: str, video_path: str, style: str, context: str, script: str, user_id: str, apibase: str, apikey: str, model: str, ctype: str
    ) -> list[dict]:
        chat = Chat(api_key=apikey, base_url=apibase, model=model)
        # print(ctype)
        if int(ctype) == 1:
            result = chat.chat(srt_path, video_path, style=style, context=context, script=script, user_id=user_id)
        elif int(ctype) ==  2:
            result = chat.chatv3(srt_path, video_path, context=context, script=script, user_id=user_id)
        result = json.loads(result) if isinstance(result, str) else result
        return result

    def clip(self, config: dict = {}):
        video_path = config.get("input_path")
        script_data = config.get("script_data")
        voice = config.get("voice", {})
        speaker = voice.get("speaker", "zh-CN-XiaoxiaoNeural")
        speed = voice.get("speed", 30)
        videoinfo = config.get("videoinfo")
        width, height = videoinfo.get("size", "1920x1080").split("x")
        height = int(height)
        width = int(width)
        fontsize = max(12, width // 100)
        blur_height = height * 0.16 if height < width else height * 0.11
        # 蒙版位置
        blur_y = height - blur_height
        # 字幕位置
        MarginV = 10
        # print(height, fontsize, blur_height, blur_y, MarginV)


        data = script_data
        end_time = "00:00:00.000"
        # 先将所有解说转成声音
        outputs = []
        for k, v in enumerate(data):
            outpath = add_suffix(video_path, f"trime_{k}")
            if os.path.exists(outpath):
                os.remove(outpath)
            if os.path.exists(replace_ext(outpath, "mp3")):
                os.remove(replace_ext(outpath, "mp3"))
            if os.path.exists(replace_ext(outpath, "srt")):
                os.remove(replace_ext(outpath, "srt"))
                # outputs.append(outpath.split(".")[0])
            start_time = v["time"].split(" --> ")[0]
            end_time_ = v["time"].split(" --> ")[-1]
            start_time = start_time.replace(";", ":")
            end_time = end_time.replace(";", ":")
            outpath = add_suffix(video_path, f"trime_{k}")
            outputs.append(outpath.split(".")[0])
            res = self.calculate_time_difference_srt(f"{end_time} --> {start_time}")
            if speaker.startswith("en") and v.get("content"):
                v["content"] = translate(v['content'], 'en')
            if speaker.startswith("ru") and v.get("content"):
                v["content"] = translate(v['content'], 'ru')
            if res[0] == "-":
                start_time = end_time
            if v["type"] == "解说":
                self.generate_speech(
                    v["content"], outpath.split(".")[0], p_voice=speaker, p_rate=f"+{speed}%"
                )
                duration = self.get_mp3_length_formatted(f"{outpath.split('.')[0]}.mp3")
                result = str(self.add_seconds_to_time(start_time, duration))
                if "." in result:
                    result = result.replace(".", ",")[:-3]
                else:
                    result = result + ",000"
                end_time = result
            else:
                duration = self.calculate_time_difference_srt(
                    f"{start_time} --> {end_time_}"
                )
            if duration[0] == "-" or duration == "00:00:00.000":
                continue

            start_time = start_time.replace(",", ".")
            trime_out_path = replace_ext(outpath, "mp4")
            if not os.path.exists(trime_out_path):
                try:
                    self.trim_video(
                        video_path, trime_out_path, start_time, duration, Config.lz_path
                    )
                except Exception as e:
                    print(str(e))
                    print(f"裁剪片段失败 {trime_out_path}", "跳过该片段处理")
                    
            if v["type"] == "解说":
                try:
                    self.process_video(
                        f"{outpath.split('.')[0]}.mp4", 
                        f"{outpath.split('.')[0]}.mp3", 
                        f"{outpath.split('.')[0]}.srt", 
                        f"{outpath.split('.')[0]}_out.mp4",
                        blur_height=blur_height,
                        blur_y=blur_y,
                        MarginV=MarginV,
                        fontsize=fontsize,
                        )
                except Exception as e:
                    print(str(e))
                    print(f"合并片段音频字幕失败 {trime_out_path}", "跳过该片段处理")
                    if os.path.exists(f"{outpath.split('.')[0]}.mp3"):
                        os.remove(f"{outpath.split('.')[0]}.mp3")
                    if os.path.exists(f"{outpath.split('.')[0]}.srt"):
                        os.remove(f"{outpath.split('.')[0]}.srt")
                    if os.path.exists(f"{outpath.split('.')[0]}_out.mp4"):
                        os.remove(f"{outpath.split('.')[0]}_out.mp4")
            # 合成视频
        now = datetime.now()
        out_path = add_suffix(video_path, f'解说_{now.strftime("%Y%m%d%H%M%S")}')
        self.concat_videos(
            [f"{path}.mp4" for path in outputs if os.path.exists(f"{path}.mp4")],
            out_path,
        )
        return out_path

    def calculate_time_difference_srt(self, srt_timestamp):
        """
        计算SRT时间戳之间的差值，并以标准的时间格式返回。

        参数：
        srt_timestamp (str): 形式为 "hh:mm:ss.sss --> hh:mm:ss.sss" 或 "hh:mm:ss --> hh:mm:ss" 的时间戳字符串。

        返回：
        formatted_difference (str): 时间差，格式为 "hh:mm:ss.sss" 或 "hh:mm:ss"。
        """
        # 解析开始和结束时间
        start_time_str, end_time_str = srt_timestamp.replace(",", ".").split(" --> ")

        # 定义时间格式
        if "." in start_time_str:  # 检查时间戳是否包含毫秒
            time_format = "%H:%M:%S.%f"
        else:
            time_format = "%H:%M:%S"
        print("正在裁剪片段: ", start_time_str, end_time_str)
        # 将字符串转换为datetime对象
        start_time = datetime.strptime(start_time_str, time_format)
        end_time = datetime.strptime(end_time_str, time_format)

        # 计算时间差
        time_difference = end_time - start_time

        # 计算差异的总秒数
        total_seconds = time_difference.total_seconds()

        # 计算小时、分钟、秒和可选的毫秒
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        milliseconds = int((total_seconds % 1) * 1000)

        # 根据输入是否包含毫秒来决定输出格式
        if "." in start_time_str:
            formatted_difference = (
                f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"
            )
        else:
            formatted_difference = f"{hours:02}:{minutes:02}:{seconds:02}"

        return formatted_difference

    def generate_speech(
        self,
        text,
        file_name,
        p_voice=Config.voice,
        p_rate=Config.rate,
        p_volume=Config.volume,
    ):
        # 将文本转成语音并且保存
        try_times = 1

        while True:
            try:
                asyncio.run(
                    create_voice_srt_new2(
                        file_name, text, "./", p_voice, p_rate, p_volume
                    )
                )
                break
            except Exception as e:
                print(e)
                try_times += 1
            if try_times > 3:
                break

    def get_mp3_length_formatted(self, file_path):
        """
        获取MP3文件的长度，并将其格式化为 "hh:mm:ss.sss" 格式。

        参数：
        file_path (str): MP3文件的路径。

        返回：
        formatted_length (str): 音频长度，格式化为 "hh:mm:ss.sss"。
        """
        try:
            audio = MP3(file_path)
        except:
            audio = WAVE(file_path)
        total_seconds = audio.info.length

        # 计算小时、分钟、秒和毫秒
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        milliseconds = int((total_seconds % 1) * 1000)

        # 格式化时间长度为字符串，确保小时、分钟、秒都是双位数字，毫秒是三位数字
        formatted_length = f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"

        return formatted_length

    def add_seconds_to_time(self, time_str, seconds_to_add):
        seconds_to_add = seconds_to_add.replace(".", ",")
        # 定义时间格式
        time_format = "%H:%M:%S,%f"

        try:
            # 解析时间字符串
            time_obj = datetime.strptime(time_str, time_format)

            # 解析要添加的秒数（时间间隔）
            interval_obj = datetime.strptime(seconds_to_add, time_format)
            total_seconds_to_add = (
                interval_obj.hour * 3600
                + interval_obj.minute * 60
                + interval_obj.second
                + interval_obj.microsecond / 1000000
            )

            # 添加秒数
            new_time_obj = time_obj + timedelta(seconds=total_seconds_to_add)

            # 返回结果
            return new_time_obj.time()

        except ValueError:
            return "Invalid time format"

    def get_video(self, path):
        list_ = []
        for file_name in os.listdir(path):
            if file_name == r"Thumbs.db":
                continue
            list_.append(path + "/" + file_name)
        return list_

    def trim_video(
        self,
        input_path,
        output_path,
        start_time,
        duration,
        lz_path=None,
        log_level="error",
    ):
        """
        使用FFmpeg截取视频的指定时间段。

        参数：
        input_path (str): 原视频文件的路径。
        output_path (str): 输出视频文件的路径。
        start_time (str): 开始时间，格式应为 "hh:mm:ss" 或 "ss"。
        duration (str): 截取的持续时间，格式同上。
        """
        if lz_path is None:

            # 构建FFmpeg命令
            command = [
                ffmpeg,
                "-ss",
                start_time,  # 开始时间
                "-y",
                "-v",
                log_level,  # 设置日志级别
                "-i",
                input_path,  # 输入文件
                "-t",
                duration,  # 持续时间
                # '-c', 'copy',  # 使用相同的编码进行复制
                "-ac",
                str(2),
                "-ar",
                str(24000),
                output_path,  # 输出文件
            ]
        else:
            fbl_lz1_path = os.path.join(
                sample(self.get_video(os.path.join(lz_path)), 1)[0]
            )
            # 构建FFmpeg命令
            command = [
                ffmpeg,
                "-ss",
                start_time,  # 开始时间
                "-v",
                log_level,  # 设置日志级别
                "-i",
                input_path,  # 输入文件
                "-i",
                fbl_lz1_path,  # 输入文件
                "-t",
                duration,  # 持续时间
                # '-c', 'copy',  # 使用相同的编码进行复制
                "-filter_complex",
                "[1:v]format=yuva444p,colorchannelmixer=aa=0.001[valpha];[0:v][valpha]overlay=(W-w):(H-h)",
                "-ac",
                str(2),
                "-ar",
                str(24000),
                output_path,  # 输出文件
            ]

        # 执行命令
        # os.system(command[0])
        subprocess.run(command, check=True)

    def process_video(
        self,
        video_path,
        audio_path,
        subtitle_path,
        output_path,
        blur_height=Config.blur_height,
        blur_y=Config.blur_y,
        MarginV=Config.MarginV,
        log_level="error",
        fontsize=20,
    ):

        origin_subtitle = subtitle_path
        subtitle_path = subtitle_path.replace("\\", "/")
        subtitle_path = subtitle_path.replace(":", "\:")
        command = [
            ffmpeg,
            "-v",
            log_level,  # 设置日志级别
            "-y",
            "-i",
            video_path,  # 输入视频文件
            "-i",
            audio_path,  # 输入音频文件
            "-filter_complex",
            f"[0:v]crop=iw:{blur_height}:{blur_y}[gblur];"  # 裁剪出底部用于模糊的区域
            f"[gblur]gblur=sigma=20[gblurred];"  # 对裁剪出的区域应用高斯模糊
            f"[0:v][gblurred]overlay=0:{blur_y}[blurredv];"  # 将模糊区域覆盖回原视频
            f"[blurredv]subtitles='{subtitle_path}':force_style='Alignment=2,Fontsize={fontsize},MarginV={MarginV}'[v];"  # 添加字幕，并调整字幕位置
            f"[1:a]aformat=channel_layouts=stereo[a]",  # 确保音频为立体声
            "-map",
            "[v]",  # 映射处理过的视频流
            "-map",
            "[a]",  # 映射处理过的音频流
            "-c:v",
            "libx264",  # 视频使用x264编码
            "-c:a",
            "aac",  # 音频使用AAC编码
            "-strict",
            "experimental",  # 如果需要，使用实验性功能
            "-preset",
            "fast",  # 选择预设以平衡编码速度和质量
            output_path,  # 输出文件路径
        ]
        # print(">>>>>", " ".join(command))
        subprocess.run(command, check=True)
        if os.path.exists(output_path):
            os.replace(output_path, video_path)  # 用输出文件替换原始文件

        # 完成后删除subtitle_path字幕文件
        os.remove(origin_subtitle)
        os.remove(audio_path)

    def concat_videos(self, video_files, output_file, log_level="error"):
        # 创建一个临时文件列表
        with open("filelist.txt", "w", encoding="utf-8") as file:
            for video in video_files:
                file.write(f"file '{video}'\n")

        # 构建FFmpeg命令
        command = [
            ffmpeg,
            "-loglevel",
            log_level,
            "-y",
            "-f",
            "concat",  # 使用concat格式
            "-safe",
            "0",  # 允许非安全文件名
            "-i",
            "filelist.txt",  # 使用文件列表
            "-c",
            "copy",  # 视频流直接复制
            output_file,
        ]

        # 调用FFmpeg
        subprocess.run(command)

        # 删除临时文件
        os.remove("filelist.txt")
        # 删除所有视频文件
        for video in video_files:
            os.remove(video)
