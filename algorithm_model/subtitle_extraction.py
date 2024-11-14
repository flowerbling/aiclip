import sys
import re
from pathlib import Path
import wordninja
from paddleocr import PaddleOCR
import cv2
import time
from _utils import load_text_from_path
from subtitle import Subtitle
from tqdm import tqdm
import difflib
import os
import platform



def are_texts_similar(text1, text2, threshold=0.7):
    """比较两个文本的相似度，返回是否相似"""
    text1 = text1.replace(" ", "")
    text2 = text2.replace(" ", "")
    
    # text1s = text1.split("$!$")
    # text2s = text2.split("$!$")
    # sims = []
    # for t1 in text1s:
    #     for t2 in text2s:
    #         if len(t1) > 3 and len(t2) > 3:
    #             sim = difflib.SequenceMatcher(None, t1, t2).ratio()
    #             sims.append(sim)

    # 如果文本长度大于20个字符，只比较前10个字符
    if len(text1) > 30 or len(text2) > 30:
        min_len = min(len(text1), len(text2), 20)
        text1 = text1[:min_len]
        text2 = text2[:min_len]
    similarity = difflib.SequenceMatcher(None, text1, text2).ratio()
    # print(text1, text2, similarity)
    # sims.append(similarity)
    # max_sim = max(sims)
    return similarity > threshold

system = platform.system()
if system == 'Darwin':
    encoding = 'utf-8'
elif system == 'Windows':
    encoding = 'gbk'

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    base_path = sys._MEIPASS + r"\algorithm_model"
else:
    base_path = os.path.dirname(__file__)


total_frame = 0
processed_frame = 0
scan_status = '初始化'

def set_scan_status(processed, total, status: str = None):
    global total_frame, processed_frame, scan_status
    total_frame = total
    processed_frame = processed
    scan_status = status if status else "初始化"

def get_scan_status():
    global total_frame, processed_frame, scan_status
    return {
        'total': total_frame,
        'processed': processed_frame,
        'scan_status': scan_status
    }

def get_ocr_with_lang(lang: str):
    if lang in ['en', 'zh', 'ch']:
        det_model_dir = os.path.join("algorithm_model", "ch_PP-OCRv4_det_infer")
        rec_model_dir = os.path.join("algorithm_model", "ch_PP-OCRv4_rec_infer")
        cls_model_dir = os.path.join("algorithm_model", "ch_ppocr_mobile_v2.0_cls_infer")
        ocr = PaddleOCR(
            det_model_dir=det_model_dir, rec_model_dir=rec_model_dir,
            cls_model_dir=cls_model_dir,
            use_angle_cls=False, lang="ch")
        return ocr
    if lang == 'japan':
        det_model_dir = os.path.join("algorithm_model", "ch_PP-OCRv4_det_infer")
        rec_model_dir = os.path.join("algorithm_model", "japan_PP-OCRv3_rec")
        cls_model_dir = os.path.join("algorithm_model", "ch_ppocr_mobile_v2.0_cls_infer")
        ocr = PaddleOCR(
            det_model_dir=det_model_dir, rec_model_dir=rec_model_dir,
            cls_model_dir=cls_model_dir,
            use_angle_cls=False, lang="japan")
        return ocr
    if lang == "korean":
        det_model_dir = os.path.join("algorithm_model", "ch_PP-OCRv4_det_infer")
        rec_model_dir = os.path.join("algorithm_model", "korean_PP-OCRv3_rec")
        cls_model_dir = os.path.join("algorithm_model", "ch_ppocr_mobile_v2.0_cls_infer")
        ocr = PaddleOCR(
            det_model_dir=det_model_dir, rec_model_dir=rec_model_dir,
            cls_model_dir=cls_model_dir,
            use_angle_cls=False, lang="korean")
        return ocr

def scan_frame(inputpath: str, area: list, currenttime: int, video_length: str, langs: list):
    video = cv2.VideoCapture(inputpath)
    fps = video.get(cv2.CAP_PROP_FPS)
    height = video.get(cv2.CAP_PROP_FRAME_HEIGHT)
    width = video.get(cv2.CAP_PROP_FRAME_WIDTH)
    total_frame = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    currentframe = min(max(1, int(currenttime * fps)), total_frame)
    # print(currentframe)
    video.set(cv2.CAP_PROP_POS_FRAMES, currentframe)
    ret, frame = video.read()
    if not ret:
        return
    
    if not area:
        area = [0, height * 0.5, width, height]
        if video_length == "long":
            area = [0, height * 0.6, width, height]
    bottom_half = frame[area[1]:area[3], area[0]:area[2]]
    ocrs = {}
    for lang in langs:
        if lang == "en" or lang == "zh":
            if 'ch' not in ocrs:
                ocrs["ch"] = get_ocr_with_lang(lang)
        else:
            ocrs[lang] = get_ocr_with_lang(lang)
    
    results = []
    for lang, ocr in ocrs.items():
        rec_res = ocr.ocr(bottom_half, cls=True)
        if rec_res[0] is None:
            continue
        texts = [line[1][0] for line in rec_res[0] if line[1][1] >= 0.75]
        if lang in ["ch", "en"]:
            zhs = ""
            en = ""
            for text in texts:
                if re.search(r'[\u4e00-\u9fa5]', text):
                    zhs += text
                elif re.search(r'[a-zA-Z0-9]', text):
                    en += text
            if en:
                words = wordninja.split(en)
                new_en = ""
                for word in words:
                    if word in [".", ",", "?", "!", "..."]:
                        new_en += word
                    else:
                        new_en += (" " + word) 
                new_en = new_en.strip()
                en = new_en
            if zhs:
                results.append(zhs)
            if en:
                results.append(en)
        else:
            results.append(" ".join(texts))
    
    return "\n".join(results)

def start_scan(
    video_path,
    intro_duration=0,
    outro_duration=0,
):
    det_model_dir = os.path.join("algorithm_model", "ch_PP-OCRv4_det_infer")
    rec_model_dir = os.path.join("algorithm_model", "ch_PP-OCRv4_rec_infer")
    cls_model_dir = os.path.join("algorithm_model", "ch_ppocr_mobile_v2.0_cls_infer")
    path = Path(video_path)
    video_name = path.stem
    video_dir = path.parent
    # 记录开始时间
    start_time = time.time()
    # 初始化PaddleOCR
    ocr = PaddleOCR(
        det_model_dir=det_model_dir,
        rec_model_dir=rec_model_dir,
        cls_model_dir=cls_model_dir,
        use_angle_cls=False,
        lang="ch",
        show_log=False,
    )

    # 打开视频文件
    cap = cv2.VideoCapture(video_path)

    # 确定视频的总帧数和帧率
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = max(1, cap.get(cv2.CAP_PROP_FPS))  # 防止帧率为0的情况
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    video_length = "long" if width > height else "short"
    # 跳过片头和片尾的帧数
    intro_frames = int(intro_duration) * int(fps)
    outro_frames = int(outro_duration) * int(fps)
    speed = 1.5

    area = [0, height * 0.5, width, height]
    if video_length == "long":
        area = [0, height * 0.6, width, height]
    # 准备处理每秒的一帧
    frames_to_process = (total_frames - intro_frames - outro_frames) // int(speed * fps)
    # frames_to_process = total_frames - intro_frames - outro_frames
    textlines = []
    for frame_count in tqdm(
        range(frames_to_process), desc="提取字幕"
    ):
        set_scan_status(frame_count, frames_to_process + 1, "提取字幕中")
        # 设置要捕获的帧的编号
        current_frame_index = frame_count * int(speed * fps) + intro_frames
        # current_frame_index = frame_count + intro_frames

        if current_frame_index >= total_frames - outro_frames:
            break
        cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame_index)

        ret, frame = cap.read()
        if not ret:
            break

        # 计算当前帧的时间戳
        timestamp = current_frame_index / fps
        time_str = time.strftime("%H:%M:%S", time.gmtime(timestamp))
        if video_length == "long":
            # 只处理帧的下半部分
            h, w, _ = frame.shape
            bottom_half = frame[h * 3 // 4 :, :]
        else:
            h, w, _ = frame.shape
            start_index = int(h * 0.58)
            end_index = int(h * 0.72)
            bottom_half = frame[start_index:end_index, :]
        # 对选定的帧部分应用OC
        if area:
            # 只取用户指定的区域的y坐标
            start_y = int(area[1])
            end_y = int(area[3])
            bottom_half = frame[start_y:end_y, :]
        width = bottom_half.shape[1]
        height = bottom_half.shape[0]
        if width >= 720:
            resized_width = 720
            resized_height = int(height * (720 / width))
            bottom_half = cv2.resize(bottom_half, (resized_width, resized_height))
        rec_res = ocr.ocr(bottom_half, cls=True)
        if rec_res[0] is None:
            continue
        for line in rec_res[0]:
            # print(line)
            if line[1][1] < 0.91:
                continue
            text = line[1][0]
            textlines.append(f"{time_str}: {text}")
        # print(textlines)
    cap.release()

    # 记录结束时间
    end_time = time.time()

    # 计算并打印整体运行时间
    total_time = end_time - start_time

    # 生成SRT文件
    set_scan_status(0, 1, "生成字幕文件中")
    generate_srt(textlines, f"{video_dir}/{video_name}.srt")
    set_scan_status(1, 1, "处理完成")
    return str(video_dir)


def ocr_text(
    inputpath: str
):
    det_model_dir = os.path.join("algorithm_model", 'ch_PP-OCRv4_det_infer')
    rec_model_dir = os.path.join("algorithm_model", 'ch_PP-OCRv4_rec_infer')
    cls_model_dir = os.path.join("algorithm_model", 'ch_ppocr_mobile_v2.0_cls_infer')
    path = Path(inputpath)
    ocr = PaddleOCR(
        det_model_dir=det_model_dir, rec_model_dir=rec_model_dir,
        cls_model_dir=cls_model_dir,
        use_angle_cls=False, lang="ch")

    # 打开视频文件
    cap = cv2.VideoCapture(inputpath)

    # 确定视频的总帧数和帧率
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    # print(cap.get(cv2.CAP_PROP_FPS))
    fps = max(1, cap.get(cv2.CAP_PROP_FPS))  # 防止帧率为0的情况
    # print(fps)

    # 跳过片头和片尾的帧数
    intro_frames = 0
    outro_frames = 0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    area = [0, height * 0.5, width, height]
    video_length = "long" if width > height else "short"
    if video_length == "long":
        area = [0, height * 0.4, width, height]
    if video_length == "long":
        speed = 0.6
    else:
        speed = 0.6
    # 准备处理每秒的一帧
    frames_to_process = total_frames // int(speed*fps)
    # frames_to_process = total_frames - intro_frames - outro_frames
    result = []

    previous_ocr_text = ""
    for frame_count in tqdm(range(frames_to_process), desc="提取字幕"):
        set_scan_status(frame_count, frames_to_process + 1, '提取字幕中')
        # 设置要捕获的帧的编号
        current_frame_index = frame_count * int(speed*fps)
        # current_frame_index = frame_count + intro_frames

        if current_frame_index >= total_frames:
            break
        cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame_index)

        ret, frame = cap.read()
        if not ret:
            break

        # 计算当前帧的时间戳
        timestamp = current_frame_index / fps
        if video_length == "long":
            # 只处理帧的下半部分
            h, w, _ = frame.shape
            bottom_half = frame[h *3 // 4:, :]
        else:
            h, w, _ = frame.shape
            start_index = int(h * 0.58)
            end_index = int(h * 0.72)
            bottom_half = frame[start_index:end_index, :]
        # 对选定的帧部分应用OC
        if area:
            # 只取用户指定的区域的y坐标
            start_y = int(area[1])
            end_y = int(area[3])
            bottom_half = frame[start_y:end_y, :]
        width = bottom_half.shape[1]
        height = bottom_half.shape[0]
        if width >= 720:
            resized_width = 720
            resized_height = int(height * (720 / width))
            bottom_half = cv2.resize(bottom_half, (resized_width, resized_height))
        rec_res = ocr.ocr(bottom_half, cls=True)
        if rec_res[0] is None:
            continue
        for line in rec_res[0]:
            # print(line)
            if line[1][1] < 0.95:
                continue
            text = line[1][0]
            result.append(f'{current_frame_index}: {text}')
    # print(result)

    start = 0
    end = 0
    processed_texts = []
    for data in result:
        data = data.strip()
        if not data:
            continue
        time, text = data.split(": ", 1)
        if processed_texts:
            current_frame_index, last_text = processed_texts[-1].split(": ", 1)
            if is_similar(text, last_text):
                if len(text) > len(last_text):
                    processed_texts[-1] = f"{current_frame_index}: {text}"
                continue
        processed_texts.append(data)

    ocr_result = []
    if start == 0 and len(processed_texts) > 0:
        first = processed_texts[0]
        current_frame_index, last_text = first.split(": ", 1)
        start = max(0, int(int(current_frame_index) * 1000 // int(fps)) - 500)
        
    for processed_text in processed_texts:
        current_frame_index, text = processed_text.split(": ", 1)
        end = int(int(current_frame_index) * 1000 // int(fps))
        ocr_result.append({
            "start": start,
            "end": end,
            "raw_text": text
        })
        start = end
    print(ocr_result)
    
    return ocr_result
def process_and_update_file(lines):
    # 从文件读取文本数据
    text_data = lines
    processed_texts = []
    last_text = ""

    # 处理文本数据，保留长的重复文本
    for data in text_data:
        data = data.strip()
        if not data:
            continue
        unpacks = data.split(": ", 1)
        if len(unpacks) == 2:
            time, text = data.split(": ", 1)
        elif len(unpacks) == 1:
            continue
        else:
            time = unpacks[0]
            text = " ".join(unpacks[1:])

        if processed_texts:
            last_time, last_text = processed_texts[-1].split(": ", 1)
            if is_similar(text, last_text):
                if len(text) > len(last_text):
                    processed_texts[-1] = f"{time}: {text}"
                continue
        processed_texts.append(data)
    return processed_texts



def is_similar(a, b, threshold=0.90):
    # 计算两个字符串的相似度
    similarity = difflib.SequenceMatcher(None, a, b).ratio()
    return similarity >= threshold


def generate_srt(lines, output_file):
    processed_texts = process_and_update_file(lines)
    srt_content = []
    previous_text = ""
    entry_number = 1

    previous_start_time = ""
    for line in processed_texts:
        parts = line.strip().split(': ', 1)  # 假设时间后面紧跟着冒号和空格
        # print("parts:", parts)
        if len(parts) == 2:
            time_str, text_line = parts
            current_date = time.localtime()
            current_date_str = time.strftime('%Y-%m-%d', current_date)

            datetime_str = current_date_str + ' ' + time_str
            if text_line.isdigit():
                continue
            if previous_text and is_similar(text_line, previous_text):
                # 如果当前文本较长，则更新srt_content中的最后一条记录
                if len(text_line) > len(previous_text):
                    overtime = 1
                    overtime += len(text_line) * 0.2
                    overtime = min(overtime, 3)
                    end_time = time.strftime('%H:%M:%S', time.localtime(
                        time.mktime(time.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')) + overtime))
                    srt_content[-1] = f'{entry_number}\n{previous_start_time},000 --> {end_time},000\n{text_line}\n\n'
                else:
                    # 更新结束时间但保留之前的文本
                    srt_content[-1] = f'{entry_number}\n{previous_start_time},000 --> {time_str},000\n{previous_text}\n\n'
            else:
                overtime = 1
                overtime += len(text_line) * 0.2
                overtime = min(overtime, 3)
                end_time = time.strftime('%H:%M:%S', time.localtime(
                    time.mktime(time.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')) + overtime))
                srt_content.append(f'{entry_number}\n{time_str},000 --> {end_time},000\n{text_line}\n\n')
                entry_number += 1
                previous_start_time = time_str

            previous_text = text_line
    subtitle = Subtitle()
    subtitle.read_srt(''.join(srt_content))
    subtitle.adjust_time()
    subtitle.save_srt(output_file, encoding)
    # output_txt = output_file.replace('.srt', '.txt')
    # subtitle.save_txt(output_txt, encoding)
    # with open(output_file, 'w', encoding=encoding) as file:
    #     file.writelines(srt_content)

def analyze_audio(srt_path, video_path, gender_path):
    text = load_text_from_path(srt_path)
    subtitle = Subtitle()
    subtitle.read_srt(text)
    try:
        subtitle.audio_clip(video_path=video_path)
        subtitle.save_gender_file(gender_path)
    except Exception as e:
        print(f"An error occurred while analyzing the audio: {e}")
    finally:
        pass
        # subtitle.clear()

def get_ocr():
    det_model_dir = os.path.join("algorithm_model", 'ch_PP-OCRv4_det_infer')
    rec_model_dir = os.path.join("algorithm_model", 'ch_PP-OCRv4_rec_infer')
    cls_model_dir = os.path.join("algorithm_model", 'ch_ppocr_mobile_v2.0_cls_infer')
    ocr = PaddleOCR(
        det_model_dir=det_model_dir, rec_model_dir=rec_model_dir,
        cls_model_dir=cls_model_dir,
        use_angle_cls=False, lang="ch")
    return ocr

def start(job, db):
    params = job.params
    video_path = params.get("inputpath")
    video_length = params.get("video_length")
    intro_duration = params.get("intro_duration")
    outro_duration = params.get("outro_duration")
    area = params.get("area")
    genderCheck = params.get("genderCheck")
    blacklist = params.get("blacklist")
    langs = params.get("langs")
    path = Path(video_path)
    video_name = path.stem
    video_dir = path.parent
    print('忽略敏感词汇:', blacklist)
    # 记录开始时间
    start_time = time.time()
    # 初始化PaddleOCR
    ocrs = {}
    for lang in langs:
        if lang == "en" or lang == "zh":
            if 'ch' not in ocrs:
                ocrs["ch"] = get_ocr_with_lang(lang)
        else:
            ocrs[lang] = get_ocr_with_lang(lang)

    # 打开视频文件
    cap = cv2.VideoCapture(video_path)

    # 确定视频的总帧数和帧率
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = max(1, int(cap.get(cv2.CAP_PROP_FPS)))
    # print(fps)

    # 跳过片头和片尾的帧数
    # print(intro_duration)
    intro_frames = int(intro_duration * fps)
    outro_frames = int(outro_duration * fps)
    if video_length == "long":
        speed = 0.6
    else:
        speed = 0.4
    # 准备处理每秒的一帧
    frames_to_process = (total_frames - intro_frames - outro_frames) // int(speed*fps)
    result = {}
    # frames_to_process = total_frames - intro_frames - outro_frames
    previous_text = ""
    with open(f'{video_name}.txt', 'w', encoding=encoding) as file:
        for frame_count in tqdm(range(frames_to_process), desc="提取字幕"):
            if frame_count % 50 == 0:
                result = {"percentage": int(100 * frame_count / frames_to_process)}
                job.result = result
                db.session.commit()

            # 设置要捕获的帧的编号
            current_frame_index = frame_count * int(speed*fps) + intro_frames
            # current_frame_index = frame_count + intro_frames

            if current_frame_index >= total_frames - outro_frames:
                break
            cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame_index)

            ret, frame = cap.read()
            if not ret:
                break

            # 计算当前帧的时间戳
            timestamp = current_frame_index / fps
            time_str = time.strftime('%H:%M:%S', time.gmtime(timestamp))
            if video_length == "long":
                # 只处理帧的下半部分
                h, w, _ = frame.shape
                bottom_half = frame[h *3 // 4:, :]
            else:
                h, w, _ = frame.shape
                start_index = int(h * 0.58)
                end_index = int(h * 0.72)
                bottom_half = frame[start_index:end_index, :]
            # 对选定的帧部分应用OC
            if area:
                # 只取用户指定的区域的y坐标
                start_y = int(area[1])
                end_y = int(area[3])
                bottom_half = frame[start_y:end_y, :]

            results = []
            for lang, ocr in ocrs.items():
                rec_res = ocr.ocr(bottom_half, cls=True)
                # print(rec_res)
                if rec_res[0] is None:
                    continue
                
                texts = [line[1][0] for line in rec_res[0] if line[1][1] >= 0.5]
                if lang in ["ch", "en"]:
                    zhs = ""
                    en = ""
                    for text in texts:
                        if re.search(r'[\u4e00-\u9fa5]', text):
                            zhs += text
                        elif re.search(r'[a-zA-Z0-9]', text):
                            en += text
                    if en:
                        words = wordninja.split(en)
                        new_en = ""
                        for word in words:
                            if word in [".", ",", "?", "!", "..."]:
                                new_en += word
                            else:
                                new_en += (" " + word) 
                        new_en = new_en.strip()
                        en = new_en
                    if zhs:
                        results.append(zhs)
                    if en:
                        results.append(en)
                else:
                    results.append(" ".join(texts))
                    if not texts:
                        continue
            if not previous_text:
                previous_text = "$!$".join(results)
            if len(results) == 1:
                text = results[0]
                if are_texts_similar(text, previous_text):
                    if len(text) > len(previous_text):
                        previous_text = text
                    # print("similar--------------------")
                    continue
                else:
                    previous_text = " ".join(texts)

            else:
                text = "$!$".join(results)
                if are_texts_similar(text, previous_text):
                    if len(text) > len(previous_text):
                        previous_text = text    
                    # print("similar--------------------")
                    continue
            # print(results)
            # 将OCR结果写入文件，包括时间戳
            # text = "$!$".join(results)
            hasblackword =  False
            for blackword in blacklist:
                if blackword in previous_text:
                    hasblackword = True
                    break
            if not hasblackword:
                file.write(f'{time_str}: {previous_text}\n')
                print(f'{time_str}: {previous_text}')
            previous_text = "$!$".join(results)
        for blackword in blacklist:
            if blackword in previous_text:
                hasblackword = True
                break
        if not hasblackword:
            file.write(f'{time_str}: {previous_text}\n')
            print(f'{time_str}: {previous_text}')
        
        
    cap.release()

    # 记录结束时间
    end_time = time.time()

    # 计算并打印整体运行时间
    total_time = end_time - start_time
    print(f'Total runtime: {total_time} seconds')

    generate_srt(f'{video_name}.txt', f'{video_dir}/{video_name}.srt')
    if genderCheck == 'true' or genderCheck is True:
        gender_path = f'{video_dir}/{video_name}_gender.txt'
        analyze_audio(f'{video_dir}/{video_name}.srt', video_path, gender_path)
    os.remove(f'{video_name}.txt')
    return str(video_dir)
