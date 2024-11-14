import json
import os
from openai import OpenAI

from .check import check_json
from .conf import Config
from .utils import get_video_length
from .prompt import SCRIPT_PROMPT, SCRIPT_PROMPT_V2, SCRIPT_PROMPT_SUFFIX_V2, BADPROMPT
from _utils import load_text_from_path, report_token_usage
import difflib

def are_texts_similar(text1, text2, threshold=0.5):
    """比较两个文本的相似度，返回是否相似"""
    text1 = text1.replace(" ", "")
    text2 = text2.replace(" ", "")
    similarity = difflib.SequenceMatcher(None, text1, text2).ratio()
    # print(text1, text2, similarity)
    # sims.append(similarity)
    # max_sim = max(sims)
    return similarity > threshold

class Chat:

    def __init__(
        self, api_key=Config.api_key, base_url=Config.base_url, model=Config.model
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

    def chat(self, srt_path, video_path, style, context: str, script: str, user_id: str = ""):
        video_duration_formatted = get_video_length(video_path)
        prompt = load_text_from_path(srt_path)
        lines = prompt.split("\n")
        x = [x for x in lines if x]
        
        # 每100行处理一条

        results = [{
            "type": "解说",
            "content": "郭槐莞尔一笑,这个嘛我带到是听说,李娘娘确实生下过一胎, 至于生太子嘛, 我着实不知道. 王朝心咯噔了一下,转身就看向了陈林,紧接着他就开始让陈林回忆这件事儿的种种细节",
            "time": "00:00:00,000 --> 00:00:05,319"
        },
        {
            "type": "video",
            "time": "00:00:030,560 --> 00:00:35,120"
        },
        {
            "type": "解说",
            "content": "陈林回忆着二十年前的往事,他还记得那天寇珠怀中抱着一个孩子",
            "time": "00:00:47,200 --> 00:00:049310"
        }]
          
        step = 201
        for i in range(0, len(x), step):
            lines100 = x[i : i + step + 18]
            text = "\n".join(lines100)
            pre = json.dumps(results[-6:], ensure_ascii=False, indent=4)
            script_content = f"""
            ## 充分模仿下面的解说词案例进行解说,要模仿脚本的语气语法和排版. 
            - 语气: 比如很幽默活着很气愤
            - 排版:比如全部解说为固定每句七个字等等
            **解说词案例**
            {script}
            """
            oprompt = SCRIPT_PROMPT.format(pre=pre, context=context)
            messages = [
                {
                    "role": "system",
                    "content":  oprompt
                    + "\n"
                    + "## 全部剧情片段"
                    + context
                    + "\n"
                    + "## 当前剧情片段"
                    + "\n"
                    + text
                    + "\n"
                    + "## 风格"
                    + "\n搞笑,解说起来笑料十足能笑死人"
                    + "\n",
                }
            ]
            if script:
                messages.append({
                    "role": "user",
                    "content": script_content,
                })
            # print(">>>>>>>>>>>")
            # print(messages[0]['content'])
            # print(">>>>>>>>>>>")
            max_trys = 1
            while True:
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.3,
                    max_tokens=4096,
                )
                result = completion.choices[0].message.content
                result = result.replace("```json", "").replace("```", "")
                if check_json(result, video_duration_formatted) or max_trys > 3:
                    last = results[-1]
                    new_result = json.loads(result)
                    first = new_result[0]
                    if last['type'] == "解说" and first['type'] == "解说":
                        sim = are_texts_similar(first["content"], last["content"])
                        if sim:
                            results.pop()
                    
                    results.extend(new_result)
                    print(result)
                    break
                max_trys += 1
        results = results[3:]
        return results


    def chatv2(self, srt_path, video_path, style, context: str, script: str, user_id: str = ""):
        video_duration_formatted = get_video_length(video_path)
        subtitle = load_text_from_path(srt_path)
        prompt = SCRIPT_PROMPT_V2.format(subtitle=subtitle, context=context) + SCRIPT_PROMPT_SUFFIX_V2
        messages = [{ "role": "user","content": prompt }]
        result = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.3,
            max_tokens=8000,
        ).choices[0].message.content
        result = result.replace("```json", "").replace("```", "")
        print(result)
        return result
    
    def chatv3(self, srt_path, video_path, context: str, script: str, user_id: str = ""):
        video_duration_formatted = get_video_length(video_path)
        prompt = load_text_from_path(srt_path)
        lines = prompt.split("\n")
        x = [x for x in lines if x]
        
        # 每100行处理一条

        results = [{
            "type": "解说",
            "content": "郭槐莞尔一笑,这个嘛我带到是听说,李娘娘确实生下过一胎, 至于生太子嘛, 我着实不知道. 王朝心咯噔了一下,转身就看向了陈林,紧接着他就开始让陈林回忆这件事儿的种种细节,这剧情也太老套出戏了吧",
            "time": "00:00:00,000 --> 00:00:05,319"
        },
        {
            "type": "video",
            "time": "00:00:030,560 --> 00:00:35,120"
        },
        {
            "type": "解说",
            "content": "陈林回忆着二十年前的往事,他还记得那天寇珠怀中抱着一个孩子。说实话，后面的剧情就算我不看，也能猜到个大概了",
            "time": "00:00:47,200 --> 00:00:049310"
        }]
          
        step = 151
        for i in range(0, len(x), step):
            lines100 = x[i : i + step + 18]
            text = "\n".join(lines100)
            pre = json.dumps(results[-6:], ensure_ascii=False, indent=4)
            script_content = f"""
            ## 充分模仿下面的解说词案例进行解说,要模仿脚本的语气语法和排版. 
            - 语气: 比如很幽默活着很气愤
            - 排版:比如全部解说为固定每句七个字等等
            **解说词案例**
            {script}
            """
            oprompt = BADPROMPT.format(pre=pre, context=context)
            messages = [
                {
                    "role": "system",
                    "content":  oprompt
                    + "\n"
                    + "## 视频总长度"
                    + "\n"
                    + video_duration_formatted
                    + "\n"
                    + "## 全部剧情片段"
                    + context
                    + "\n"
                    + "## 当前剧情片段"
                    + "\n"
                    + text
                }
            ]
            if script:
                messages.append({
                    "role": "user",
                    "content": script_content,
                })
            max_trys = 1
            while True:
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.3,
                    max_tokens=4096,
                )
                result = completion.choices[0].message.content
                result = result.replace("```json", "").replace("```", "")
                if check_json(result, video_duration_formatted) or max_trys > 3:
                    last = results[-1]
                    new_result = json.loads(result)
                    first = new_result[0]
                    if last['type'] == "解说" and first['type'] == "解说":
                        sim = are_texts_similar(first["content"], last["content"])
                        if sim:
                            results.pop()
                    
                    results.extend(new_result)
                    print(result)
                    break
                max_trys += 1
        results = results[3:]
        return results