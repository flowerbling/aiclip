# 解说自动剪辑
短剧自动化剪辑
1. 从视频中提取字幕 PaddleOCR
2. 根据视频字幕生成解说文案 大模型
3. 根据解说文案生成解说音频 edge-tts
4. 根据视频和音频合成和裁剪视频 ffmpeg

# 可优化
加入VL模型来获取更多视频信息 将更多信息提交给大模型处理可提高准确率和提升效果

# 源码路径
https://github.com/flowerbling/aiclip

# 打包好的可运行文件文件下载地址
windows：

# 环境配置

```BASH
git clone https://github.com/flowerbling/aiclip.git
cd aiclip


conda create -n aiclip python=3.10
conda activate aiclip
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 下载ffmpeg.exe 到ffmpeg目录下
python app.py
```

# 如果需要需要打包

```BASH
pip install pyinsatller
pyinstaller pack.spec
```