import re
import os
from pydantic import BaseModel
from _utils import get_encoding, chat_openai, add_suffix
import cv2
import numpy as np
from moviepy.editor import VideoFileClip
from algorithm_model import baidu_translate as fanyi
from tqdm import tqdm


encoding = get_encoding()


class Caption(BaseModel):
    start: float = 0
    end: float = 0
    text: str = ""
    index: int = 0
    time: str = ""
    path: str = ""
    gender: str = ""


class Subtitle:
    user_id: str = ""
    captions: list[Caption] = []

    def __init__(self, user_id: str = ""):
        self.captions = []
        self.user_id = user_id

    def read_srt(self, file_content: str):
        lines = file_content.split("\n")
        caption = {}
        try:
            lines = [x for x in lines if x.strip()]
            for line_num, line in enumerate(lines):
                line = line.strip()

                if line_num % 3 == 1:
                    start, end = line.split("-->")
                    start = start.strip()
                    end = end.strip()
                    caption["stime"] = start
                    caption["time"] = line
                    # 转换为秒
                    start = (
                        int(start[:2]) * 3600
                        + int(start[3:5]) * 60
                        + int(start[6:8])
                        + int(start[9:]) / 1000
                    )
                    end = (
                        int(end[:2]) * 3600
                        + int(end[3:5]) * 60
                        + int(end[6:8])
                        + int(end[9:]) / 1000
                    )

                    caption["start"] = start
                    caption["end"] = end
                elif line_num % 3 == 0:
                    items = line.split(" ")
                    index = int(items[0])
                    speaker = items[-1] if len(items) > 1 else ""
                    caption["index"] = index

                elif line_num % 3 == 2:
                    if "text" in caption:
                        caption["text"] += "\n" + line
                    else:
                        caption["text"] = line

                if (
                    caption
                    and "index" in caption
                    and "time" in caption
                    and "text" in caption
                ):
                    self.captions.append(Caption.model_validate(caption))
                    caption = {}
            if caption:
                self.captions.append(Caption.model_validate(caption))
        except:
            self.captions = []
            splits = file_content.strip().split("\n\n")
            for split in splits:
                lines = split.split("\n")
                # print(lines)
                start, end = lines[1].split("-->")
                stime = start
                start = start.strip()
                end = end.strip()
                caption["stime"] = start
                caption["time"] = lines[1]
                # 转换为秒
                start = (
                    int(start[:2]) * 3600
                    + int(start[3:5]) * 60
                    + int(start[6:8])
                    + int(start[9:]) / 1000
                )
                end = (
                    int(end[:2]) * 3600
                    + int(end[3:5]) * 60
                    + int(end[6:8])
                    + int(end[9:]) / 1000
                )

                caption = {
                    "index": int(lines[0].strip()),
                    "start": start,
                    "end": end,
                    "text": " ".join(lines[2:]),
                    "time": lines[1],
                    "stime": stime,
                }
                self.captions.append(Caption.model_validate(caption))

    def modify_caption(self, index, new_text):
        for caption in self.captions:
            if caption["index"] == index:
                caption["text"] = new_text
                break
        else:
            print(f"No caption found with index {index}")

    def save_srt(self, filename, encoding):
        with open(filename, "w", encoding=encoding) as file:
            for caption in self.captions:
                text = caption.text.replace("$!$", "\n")
                file.write(f"{caption.index}\n")
                file.write(f"{caption.time}\n")
                file.write(f"{text}\n\n")

    def save_txt(self, filename, encoding):
        with open(filename, "w", encoding=encoding) as file:
            for caption in self.captions:
                text = caption.text.replace("$!$", "\n")
                file.write(f"{text}\n")


    def audio_clip(self, video_path: str):
        from moviepy.editor import AudioFileClip
        from tempfile import NamedTemporaryFile

        clip = AudioFileClip(video_path)
        for caption in self.captions:
            # 检查 caption.start 和 caption.end 是否有有效值
            gender = "未知"
            try:
                if caption.start is not None and caption.end is not None:
                    subclip = clip.subclip(caption.start)
                    subclip.duration = min(
                        max(1, caption.end - caption.start),
                        clip.duration - caption.start,
                    )
                    # 当前目录下面保存
                    if not os.path.exists("tmp/"):
                        os.makedirs("tmp/")
                    with NamedTemporaryFile(
                        suffix=".wav", dir="tmp/", delete=False
                    ) as f:
                        # 使用正确的方法写入音频文件
                        subclip.write_audiofile(f.name, codec="pcm_s16le")
                        filename = f.name

                    os.unlink(filename)
                    caption.path = f.name
                else:
                    print("Warning: Caption has no valid start or end time, skipping.")

            except Exception as e:
                print(f"Error processing caption: {e}")

    def save_gender_file(self, filepath: str):
        with open(filepath, "w", encoding=encoding) as f:
            for caption in self.captions:
                f.write(f"{caption.gender}: {caption.text}\n")

    def clear(self):
        # 删除台词临时wav文件
        for caption in self.captions:
            if caption.path and os.path.exists(caption.path):
                os.unlink(caption.path)

    def _format_time(self, timefloat: float) -> str:
        time = int(timefloat)
        hours = time // 3600
        minutes = (time % 3600) // 60
        seconds = time % 60
        milliseconds = int((timefloat - time) * 1000)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

    def adjust_time(self):
        # 让字幕的时间 不再重叠
        for i, caption in enumerate(self.captions):
            if i < len(self.captions) - 1:
                if caption.end > self.captions[i + 1].start:
                    caption.end = self.captions[i + 1].start - 0.1

                caption.time = f"{self._format_time(caption.start)} --> {self._format_time(caption.end)}"

        # 合并开始时间相同的字幕
        to_poped_index = []
        for i, caption in enumerate(self.captions):
            if i < len(self.captions) - 1:
                if caption.start == self.captions[i + 1].start:
                    self.captions[i + 1].text = (
                        caption.text + " " + self.captions[i + 1].text
                    )
                    to_poped_index.append(i)
        self.captions = [
            caption
            for i, caption in enumerate(self.captions)
            if i not in to_poped_index
        ]

        for i, caption in enumerate(self.captions):
            caption.index = i + 1


def has_text(roi):
    edges = cv2.Canny(roi, 100, 200)
    edge_count = np.count_nonzero(edges)
    # print(edge_count)
    if edge_count > 200:  # 阈值可以根据实际情况调整
        #  区域内白色占比
        return True
    else:
        return False


def subtitle_blur(
    input_path: str,
    area: tuple,
    level: int,
    need_audio=True,
    white_threshold: int = 220,
    method: str = "gl",
    queued=None,
    db=None,
) -> str:
    # 视频路径和指定的字幕区域
    cap = cv2.VideoCapture(input_path)
    x_min, y_min, x_max, y_max = area
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    input_path_mp4 = input_path.split(".")[0] + ".mp4"
    final_path = add_suffix(input_path_mp4, method + "_" + "blur")
    tmp_path = add_suffix(input_path_mp4, "tmp")
    out_path = final_path
    if need_audio:
        out_path = tmp_path

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(
        out_path,
        fourcc,
        cap.get(cv2.CAP_PROP_FPS),
        (
            int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        ),
    )
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if need_audio:
        frame_count = frame_count + 1
    current_frame = 0
    ignore_det_left = 0
    progress_bar = tqdm(total=frame_count, desc="Bluring")
    while cap.isOpened():
        ret, frame = cap.read()
        current_frame += 1
        progress_bar.update(1)
        if not ret:
            break
        x_mid = int(width // 2)
        x_mid_left = int(x_mid - width * 0.05)
        x_mid_right = int(x_mid + width * 0.05)
        dec_roi = frame[y_min:y_max, x_mid_left:x_mid_right]
        if ignore_det_left > 0 or has_text(dec_roi):
            if ignore_det_left > 0:
                ignore_det_left -= 1
            else:
                ignore_det_left = 7
            if method == "bd":
                x_min, y_min, x_max, y_max = area
                if x_max - x_min > width * 0.95:
                    x_min = 0
                    x_max = width
                if y_max > height * 0.98:
                    y_max = height

                roi = [x_min, y_min, x_max - x_min, y_max - y_min]
                w = (y_max - y_min) // 5
                mask = generate_subtitle_mask(frame, roi, w)
                new_frame = inpaint_image(frame, mask, area)
                frame[y_min:y_max, x_min:x_max] = new_frame[y_min:y_max, x_min:x_max]

            elif method == "gl":
                roi = frame[y_min:y_max, x_min:x_max]
                # 转换为灰度图像
                gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                _, mask = cv2.threshold(gray, white_threshold, 255, cv2.THRESH_BINARY)

                # 扩展边界去除黑色边框
                # 字幕为横向的 所以颜色扩展纵向更多一点 效果更好
                # (10, 17)
                w = (y_max - y_min) // 5
                kernel = np.ones((w, int(w * 1.5)), np.uint8)
                mask = cv2.dilate(mask, kernel, iterations=1)

                # 使用均值滤波替代被遮挡部分
                inpainted = cv2.inpaint(roi, mask, 1, cv2.INPAINT_TELEA)

                brightness_diff = np.mean(gray) - np.mean(gray[mask == 0])
                contrast_diff = np.std(gray) - np.std(gray[mask == 0])
                inpainted = cv2.addWeighted(
                    inpainted,
                    1,
                    np.full_like(roi, brightness_diff + contrast_diff),
                    0,
                    0,
                )
                inpainted = cv2.GaussianBlur(inpainted, (7, 7), 0)
                frame[y_min:y_max, x_min:x_max] = inpainted

            elif method == "gs":
                kernel_size = width // 20 * 2 + 1
                small_kernel_size = width // 50 * 2 + 1
                little_kernel_size = width // 100 * 2 + 1
                roi = frame[y_min:y_max, x_min:x_max]
                borderType = cv2.BORDER_DEFAULT
                blurred_roi = cv2.blur(
                    roi, (kernel_size, kernel_size), borderType=borderType
                )
                frame[y_min:y_max, x_min:x_max] = blurred_roi

                over_roi = frame[
                    max(0, y_min - 20) : min(y_max + 20, height),
                    max(0, x_min - 20) : min(x_max + 20, width),
                ]
                over_blurred_roi = cv2.blur(
                    over_roi,
                    (small_kernel_size, small_kernel_size),
                    borderType=borderType,
                )
                frame[
                    max(0, y_min - 20) : min(y_max + 20, height),
                    max(0, x_min - 20) : min(x_max + 20, width),
                ] = over_blurred_roi

                little_roi = frame[
                    max(0, y_min - 30) : min(y_max + 30, height),
                    max(0, x_min - 30) : min(x_max + 30, width),
                ]
                little_blurred_roi = cv2.blur(
                    little_roi,
                    (little_kernel_size, little_kernel_size),
                    borderType=borderType,
                )
                frame[
                    max(0, y_min - 30) : min(y_max + 30, height),
                    max(0, x_min - 30) : min(x_max + 30, width),
                ] = little_blurred_roi
        # 写入输出视频
        out.write(frame)
        if current_frame % 50 == 0:
            if queued and db:
                queued.result = {"percentage": int(current_frame * 100 / frame_count)}
                db.session.commit()

    cap.release()
    out.release()
    cv2.destroyAllWindows()

    if need_audio:
        # # 使用moviepy处理音频
        clip = VideoFileClip(input_path)
        audio = clip.audio

        # 读取处理过的视频
        clip_processed = VideoFileClip(tmp_path)

        # 将原始音频与处理过的视频结合起来
        final_clip = clip_processed.set_audio(audio)
        final_clip.write_videofile(final_path)
        os.remove(tmp_path)

    return final_path


def dilate_mask(mask: np.ndarray, kernel_size) -> np.ndarray:
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    mask = cv2.dilate(mask, kernel)
    return mask


def generate_single_mask(img: np.ndarray, roi: list) -> np.ndarray:
    roi_img = np.zeros((img.shape[0], img.shape[1]), np.uint8)
    start_x, end_x = int(roi[1]), int(roi[1] + roi[3])
    start_y, end_y = int(roi[0]), int(roi[0] + roi[2])
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    roi_img[start_x:end_x, start_y:end_y] = gray[start_x:end_x, start_y:end_y]
    _, mask = cv2.threshold(roi_img, 80, 255, cv2.THRESH_BINARY)
    return mask


def generate_subtitle_mask(frame: np.ndarray, roi: list, kernel_size) -> np.ndarray:
    mask = generate_single_mask(
        frame, [0, roi[1], frame.shape[1], roi[3]]
    )  # 仅使用ROI横坐标区域
    return dilate_mask(mask, kernel_size)


def inpaint_image(img: np.ndarray, mask: np.ndarray, area: list) -> np.ndarray:
    inpainted = cv2.inpaint(img, mask, 1, cv2.INPAINT_TELEA)
    return inpainted
