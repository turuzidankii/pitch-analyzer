# 科学音高记号法音程分析功能

## 🎵 功能概览

音频音调分析工具现已支持科学音高记号法（Scientific Pitch Notation）显示音程变化，让音程分析更加直观和专业。

## 🆕 新增功能

### 1. 科学音高记号法 Y 轴
- **右侧 Y 轴**：显示标准音符记号（C4, D#4, F5等）
- **自适应范围**：根据音程变化自动调整显示范围
- **标准格式**：使用国际标准的科学音高记号（C4=中央C，440Hz）

### 2. 智能音符标注
- **黄色标注框**：在显著音程变化点自动标注音符名称
- **智能筛选**：仅显示最重要的变化点，避免图表过于拥挤
- **变化阈值**：超过2个半音的变化才会被标注

### 3. 增强的可视化效果
- **双轴显示**：同时显示半音数和音符名称
- **颜色编码**：紫色表示科学音高记号轴
- **参考线网格**：每半个八度添加参考线
- **红色基线**：突出显示起始音符位置

## 🎼 科学音高记号法说明

### 音符命名规则
```
C4  = 中央C (261.63 Hz)
A4  = 标准音A (440 Hz)
C5  = 高音C (523.25 Hz)
C3  = 低音C (130.81 Hz)
```

### 升降音表示
```
C#4 = C升4 (C sharp)
Db4 = D降4 (D flat)
F#5 = F升5
Bb3 = B降3
```

## 🚀 使用方法

### 命令行用法
```bash
# 基本音程分析
python main.py audio.wav --pitch-contour --start-time 0 --end-time 10

# 高精度分析
python main.py audio.wav --pitch-contour --start-time 1:00 --end-time 1:30 --frame-size 0.05

# 详细输出
python main.py audio.wav --pitch-contour --start-time 0 --end-time 10 -v
```

### Python API 用法
```python
from audio_pitch_analyzer import AudioPitchAnalyzer

# 创建分析器
analyzer = AudioPitchAnalyzer()

# 分析音程变化
contour_result = analyzer.analyze_pitch_contour("audio.wav", 0, 10, frame_size=0.1)

# 生成科学音高记号法图表
analyzer.visualize_pitch_contour(contour_result, "contour_chart.png")

# 获取检测到的音符
notes = contour_result['analysis_data']['notes']
unique_notes = sorted(list(set([note for note in notes if note != 'Silent'])))
print(f"检测到的音符: {', '.join(unique_notes)}")
```

## 📊 图表解读

### 主音程折线图
- **X轴**：时间（秒）
- **左Y轴**：音程变化（半音数，相对于起始音符）
- **右Y轴**：科学音高记号（绝对音高）
- **蓝色折线**：音程变化曲线
- **红色基线**：起始音符参考（0半音）
- **黄色标注**：重要音程变化点

### 统计信息
```
平均频率: 440.2 Hz          # 分析时段的平均基频
音程范围: 12.0 半音         # 最高音程 - 最低音程
最高音程: +12.0 半音        # 相对于起始音符的最高点
最低音程: 0.0 半音          # 相对于起始音符的最低点
平均置信度: 0.85            # 检测结果的平均可靠性
```

## 🎯 应用场景

### 1. 声乐训练
- 分析歌手的音准稳定性
- 检测音调滑动和颤音
- 监控音域范围变化

### 2. 乐器演奏分析
- 检查演奏音准
- 分析滑音技巧
- 评估音程跳跃精度

### 3. 音乐教育
- 可视化音程概念
- 训练音程识别
- 分析音阶演奏

### 4. 音乐制作
- 分析人声音调变化
- 检测音频质量
- 辅助音高校正

## 🧪 测试样本

项目包含多种测试样本：

### 1. 单音调样本
- `sample_A4.wav` - 标准A4音调
- 展示稳定音调的科学记号法显示

### 2. 音阶样本  
- `sample_scale.wav` - C大调音阶
- 展示音程阶梯式变化

### 3. 滑音样本
- `sample_pitch_changing.wav` - A4到A5的连续滑音
- 展示平滑音程变化

### 测试命令
```bash
# 测试所有科学音高记号法功能
python test_scientific_notation.py

# 单独测试音阶
python main.py sample_scale.wav --pitch-contour --start-time 0 --end-time 4

# 单独测试滑音
python main.py sample_pitch_changing.wav --pitch-contour --start-time 0 --end-time 5 --frame-size 0.05
```

## 🔧 技术细节

### 音符转换算法
```python
# 频率转音符的核心算法
def frequency_to_note(frequency):
    A4_freq = 440.0
    A4_note_number = 69
    note_number = round(12 * log2(frequency / A4_freq) + A4_note_number)
    octave = (note_number - 12) // 12
    note_name = note_names[note_number % 12]
    return f"{note_name}{octave}"
```

### 智能标注逻辑
- 检测阈值：音程变化 > 2半音
- 最大标注数：8个点（避免过度拥挤）
- 优先级：按变化幅度排序选择最显著的点

### 可视化参数
- 图表尺寸：14×12 英寸
- 分辨率：300 DPI
- 字体大小：9-14pt
- 颜色方案：蓝色（主线）、紫色（科学记号）、黄色（标注）

## 📈 性能优化

- **自适应Y轴范围**：仅显示有用的音程范围
- **智能标注筛选**：避免标注过密
- **高效频率计算**：缓存重复计算结果
- **内存优化**：及时释放大数组

这个科学音高记号法功能让音程分析更加专业和直观，特别适合音乐教育、声乐训练和专业音频分析场景！
