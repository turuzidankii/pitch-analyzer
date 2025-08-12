#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建变化音调的测试样本
"""

import numpy as np
import soundfile as sf

def create_pitch_changing_sample():
    """创建音调变化的测试样本"""
    
    # 参数
    sr = 22050
    duration = 5.0  # 5秒
    
    # 时间轴
    t = np.linspace(0, duration, int(sr * duration))
    
    # 创建频率变化的音调
    # 从 A4 (440Hz) 到 A5 (880Hz) 再回到 A4
    freq_start = 440  # A4
    freq_peak = 880   # A5
    
    # 创建频率变化模式（正弦波形式的变化）
    freq_variation = freq_start + (freq_peak - freq_start) * np.sin(2 * np.pi * 0.2 * t)
    
    # 生成音频信号
    phase = np.cumsum(2 * np.pi * freq_variation / sr)
    audio = 0.3 * np.sin(phase)
    
    # 添加包络以避免突然的开始和结束
    envelope = np.ones_like(audio)
    fade_samples = int(0.1 * sr)  # 0.1秒淡入淡出
    envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
    envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
    audio *= envelope
    
    # 保存文件
    filename = "sample_pitch_changing.wav"
    sf.write(filename, audio, sr)
    print(f"创建音调变化样本: {filename}")
    
    return filename

def create_scale_sample():
    """创建音阶样本"""
    
    # 参数
    sr = 22050
    note_duration = 0.5  # 每个音符0.5秒
    
    # C大调音阶的频率 (C4 到 C5)
    frequencies = [
        261.63,  # C4
        293.66,  # D4
        329.63,  # E4
        349.23,  # F4
        392.00,  # G4
        440.00,  # A4
        493.88,  # B4
        523.25   # C5
    ]
    
    audio = []
    
    for freq in frequencies:
        # 为每个音符生成音频
        t = np.linspace(0, note_duration, int(sr * note_duration))
        note_audio = 0.3 * np.sin(2 * np.pi * freq * t)
        
        # 添加包络
        fade_samples = int(0.05 * sr)  # 0.05秒淡入淡出
        envelope = np.ones_like(note_audio)
        envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
        envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
        note_audio *= envelope
        
        audio.extend(note_audio)
    
    audio = np.array(audio)
    
    # 保存文件
    filename = "sample_scale.wav"
    sf.write(filename, audio, sr)
    print(f"创建音阶样本: {filename}")
    
    return filename

if __name__ == "__main__":
    print("创建音调变化测试样本...")
    
    # 创建样本
    changing_file = create_pitch_changing_sample()
    scale_file = create_scale_sample()
    
    print(f"\n测试命令:")
    print(f"python main.py {changing_file} --pitch-contour --start-time 0 --end-time 5 --frame-size 0.05")
    print(f"python main.py {scale_file} --pitch-contour --start-time 0 --end-time 4 --frame-size 0.05")
