# 音频音调分析工具

这是一个用于分析和比较音频文件音调的Python工具。

## 功能特性

- 支持多种音频格式（WAV、MP3、FLAC等）
- 基音频率检测
- 音调比较分析
- 可视化频谱分析
- 命令行界面

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本使用

```python
from audio_pitch_analyzer import AudioPitchAnalyzer

# 创建分析器实例
analyzer = AudioPitchAnalyzer()

# 分析两个音频文件的音调
pitch1 = analyzer.analyze_pitch("audio1.wav")
pitch2 = analyzer.analyze_pitch("audio2.wav")

# 比较音调
is_same = analyzer.compare_pitches(pitch1, pitch2)
print(f"音调是否相同: {is_same}")
```

### 命令行使用

```bash
# 基本音调比较
python main.py audio1.wav audio2.wav

# 分析单个文件
python main.py audio1.wav --analyze-only

# 音程变化分析（新功能）
python main.py audio1.wav --pitch-contour --start-time 0 --end-time 10

# 高精度音程分析
python main.py audio1.wav --pitch-contour --start-time 1:00 --end-time 1:30 --frame-size 0.05
```

### 音程分析功能

新增的音程分析功能可以分析音频在指定时间范围内的音调变化：

- **时间范围分析**: 指定开始和结束时间
- **音程可视化**: 生成折线图显示音程变化
- **详细统计**: 提供音程范围、平均频率等统计信息
- **高精度分析**: 可调节分析帧大小

```python
# 使用API进行音程分析
analyzer = AudioPitchAnalyzer()
contour_result = analyzer.analyze_pitch_contour("audio.wav", 0, 10, frame_size=0.1)
analyzer.visualize_pitch_contour(contour_result, "contour.png")
```

## 项目结构

```
music/
├── audio_pitch_analyzer.py  # 核心音调分析类
├── pitch_detector.py        # 音调检测算法
├── audio_utils.py          # 音频处理工具
├── main.py                 # 命令行入口
├── requirements.txt        # 依赖包列表
└── README.md              # 项目说明
```

## 技术原理

1. **音频预处理**: 使用librosa库加载和预处理音频文件
2. **基音检测**: 采用自相关函数和倒谱分析检测基音频率
3. **音调比较**: 基于频率比较和容差设置判断音调相似性
4. **可视化**: 使用matplotlib绘制频谱图和波形图

## 注意事项

- 支持采样率：8kHz-48kHz
- 建议音频长度：1-30秒
- 最佳效果：单音源、清晰录音

## 许可证

MIT License
