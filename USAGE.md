# 音频音调分析工具使用示例

## 基本使用方法

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 分析单个音频文件
```bash
python main.py audio1.wav --analyze-only
```

### 3. 比较两个音频文件的音调
```bash
python main.py audio1.wav audio2.wav
```

### 4. 比较多个音频文件
```bash
python main.py audio1.wav audio2.wav audio3.wav
```

### 5. 详细输出模式
```bash
python main.py audio1.wav audio2.wav -v
```

### 6. 生成可视化图表
```bash
python main.py audio1.wav --analyze-only --visualize
```

### 7. 调整检测参数
```bash
# 使用YIN算法
python main.py audio1.wav audio2.wav -m yin

# 设置10%的音调容差
python main.py audio1.wav audio2.wav -t 0.1

# 设置采样率为44100Hz
python main.py audio1.wav audio2.wav -sr 44100
```

### 8. 时间范围分析 🆕
```bash
# 从1分钟开始分析到结束
python main.py audio1.wav --start-time 1:00 --analyze-only

# 分析1分钟到1分25秒的片段
python main.py audio1.wav --start-time 1:00 --end-time 1:25 --analyze-only

# 使用秒数格式：分析60秒到85秒
python main.py audio1.wav --start-time 60 --end-time 85 --analyze-only

# 比较两个音频文件的相同时间段
python main.py audio1.wav audio2.wav --start-time 0:30 --end-time 1:00

# 分析音频的最后30秒（假设音频长度为2分钟）
python main.py audio1.wav --start-time 1:30 --analyze-only
```

### 时间格式说明
支持以下时间格式：
- `"1:30"` - 1分30秒
- `"0:45"` - 45秒  
- `"2:15.5"` - 2分15.5秒
- `"90"` - 90秒
- `"120.5"` - 120.5秒

## Python API使用

```python
from audio_pitch_analyzer import AudioPitchAnalyzer

# 创建分析器
analyzer = AudioPitchAnalyzer(tolerance=0.05)

# 分析音频文件
result1 = analyzer.analyze_pitch("audio1.wav")
result2 = analyzer.analyze_pitch("audio2.wav")

# 比较音调
comparison = analyzer.compare_pitches(result1, result2)

print(f"音调是否相同: {comparison['is_same_pitch']}")
print(f"频率差异: {comparison['frequency_difference']:.2f} Hz")
print(f"相对误差: {comparison['relative_error']:.1%}")

# 生成可视化
analyzer.visualize_pitch_analysis(result1, "analysis1.png")
```

## 支持的音频格式
- WAV (.wav)
- MP3 (.mp3)
- FLAC (.flac)
- M4A (.m4a)
- AAC (.aac)
- OGG (.ogg)
- WMA (.wma)

## 技术参数
- 默认采样率: 22050 Hz
- 频率检测范围: 80-2000 Hz
- 默认音调容差: 5%
- 支持的检测算法: piptrack, YIN, autocorr, multi

## 注意事项
1. 音频文件应为单音源（如单个乐器或人声）效果最佳
2. 建议音频长度在1-30秒之间
3. 清晰的录音质量会提高检测准确性
4. 背景噪声可能影响检测结果

## 测试功能
运行内置测试：
```bash
python test_analyzer.py
```

这将创建测试音频文件并验证分析功能。
