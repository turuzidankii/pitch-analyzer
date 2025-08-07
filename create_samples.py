#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建示例音频文件用于测试
"""

import numpy as np
import soundfile as sf
import os

def create_sample_audio():
    """创建示例音频文件"""
    print("正在创建示例音频文件...")
    
    # 音频参数
    sr = 22050  # 采样率
    duration = 2  # 时长（秒）
    t = np.linspace(0, duration, int(sr * duration))
    
    # 创建不同音调的音频文件
    samples = [
        {"freq": 440, "note": "A4", "filename": "sample_A4.wav"},
        {"freq": 523.25, "note": "C5", "filename": "sample_C5.wav"},
        {"freq": 659.25, "note": "E5", "filename": "sample_E5.wav"},
        {"freq": 440, "note": "A4_copy", "filename": "sample_A4_copy.wav"},
    ]
    
    for sample in samples:
        # 生成正弦波
        audio = 0.3 * np.sin(2 * np.pi * sample["freq"] * t)
        
        # 添加一些包络，使音频更自然
        envelope = np.exp(-t * 0.5)  # 指数衰减
        audio = audio * envelope
        
        # 保存音频文件
        sf.write(sample["filename"], audio, sr)
        print(f"创建: {sample['filename']} - {sample['note']} ({sample['freq']} Hz)")
    
    print(f"\n示例音频文件已创建在当前目录")
    print("您可以使用以下命令测试:")
    print("python main.py sample_A4.wav sample_C5.wav")
    print("python main.py sample_A4.wav sample_A4_copy.wav")

if __name__ == "__main__":
    create_sample_audio()
