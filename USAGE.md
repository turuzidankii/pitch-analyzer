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

# 分析1:00到1:25的片段
python main.py audio1.wav --start-time 1:00 --end-time 1:25 --analyze-only

# 分析60秒到85秒的片段
python main.py audio1.wav --start-time 60 --end-time 85 --analyze-only
```

### 9. 音程变化分析 🆕
```bash
# 基本音程分析（分析0-10秒的音程变化）
python main.py audio1.wav --pitch-contour --start-time 0 --end-time 10

# 高精度音程分析（0.05秒帧大小）
python main.py audio1.wav --pitch-contour --start-time 0 --end-time 10 --frame-size 0.05

# 分析1分钟到1分30秒的音程变化
python main.py audio1.wav --pitch-contour --start-time 1:00 --end-time 1:30

# 详细音程分析输出
python main.py audio1.wav --pitch-contour --start-time 0 --end-time 10 -v
```

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

# 音程变化分析 🆕
contour_result = analyzer.analyze_pitch_contour("audio1.wav", 0, 10, frame_size=0.1)
analyzer.visualize_pitch_contour(contour_result, "contour.png")

print(f"音程范围: {contour_result['statistics']['interval_range']:.1f} 半音")
print(f"平均频率: {contour_result['statistics']['avg_frequency']:.1f} Hz")
```

## 音程分析功能详解 🆕

### 什么是音程分析？
音程分析功能可以分析音频在指定时间范围内的音调变化，以半音为单位显示音程的变化趋势。

### 核心参数
- **start_time**: 开始时间（秒或 mm:ss 格式）
- **end_time**: 结束时间（秒或 mm:ss 格式）
- **frame_size**: 分析帧大小（秒），影响分析精度
  - 较小值（0.05s）: 高精度，适合快速变化的音调
  - 较大值（0.2s）: 低精度，适合缓慢变化的音调

### 输出说明
音程分析会生成包含三个子图的可视化图表：
1. **音程变化折线图**: 显示相对于起始音符的音程变化（半音）
2. **频率变化图**: 显示绝对频率的变化（Hz）
3. **置信度图**: 显示检测结果的可靠性

### 应用场景
- 分析歌手的音准变化
- 检测音调滑动和颤音
- 分析乐器演奏的音程准确性
- 音乐教学中的音程训练

### 可视化图表说明 🆕
音程分析会生成一个包含三个子图的科学音高记号法图表：

1. **主音程折线图**
   - 蓝色折线：音程变化曲线（以半音为单位）
   - 左侧Y轴：相对音程（半音数）
   - 右侧Y轴：科学音高记号法（C4, D#4, F5等）
   - 黄色标注：显著音程变化点的音符名称
   - 红色基线：起始音符参考线

2. **频率变化图**
   - 绿色折线：绝对频率变化（Hz）
   - 显示音频的实际频率变化

3. **置信度图**
   - 红色折线：检测结果的可靠性
   - 值域：0-1，越高表示检测越可靠

### 科学音高记号法特性
- **自适应标记范围**：根据音程范围自动调整Y轴标记
- **智能标注**：仅在显著变化点标注音符，避免图表过于拥挤
- **标准音符格式**：使用国际标准的科学音高记号（C4=中央C）
- **双轴显示**：同时显示半音数和音符名称，便于不同用户理解
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
