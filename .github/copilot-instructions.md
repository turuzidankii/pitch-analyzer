<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# 音频音调分析项目指南

这是一个用于音频音调检测和比较的Python项目。

## 项目结构
- `audio_pitch_analyzer.py`: 主要的音调分析类
- `pitch_detector.py`: 音调检测算法实现
- `audio_utils.py`: 音频处理工具函数
- `main.py`: 命令行界面程序

## 开发指南

### 音频处理
- 使用 librosa 作为主要的音频处理库
- 支持多种音频格式：WAV, MP3, FLAC, M4A等
- 默认采样率：22050 Hz
- 音频预处理包括：去静音、归一化、高通滤波

### 音调检测方法
1. **piptrack**: librosa的基音跟踪算法
2. **YIN**: 自相关基音检测算法
3. **autocorr**: 基于自相关的方法
4. **multi**: 结合多种方法的综合检测

### 代码规范
- 使用类型提示（typing）
- 函数和类都要有详细的docstring
- 错误处理要完善，提供有意义的错误信息
- 音频分析结果返回结构化的字典

### 性能考虑
- 大文件加载时考虑内存使用
- 音频预处理要高效
- 支持批量文件处理
- 可视化功能可选，避免强制依赖

### 用户体验
- 提供详细的进度提示
- 错误信息要用户友好
- 支持不同详细程度的输出
- 命令行参数要直观易用
