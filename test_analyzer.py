#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试音频音调分析功能
"""

import numpy as np
import soundfile as sf
from audio_pitch_analyzer import AudioPitchAnalyzer
import os

def create_test_audio(frequency, duration=2, sr=22050, filename="test_audio.wav"):
    """创建测试音频文件"""
    t = np.linspace(0, duration, int(sr * duration))
    # 生成正弦波
    audio = 0.5 * np.sin(2 * np.pi * frequency * t)
    
    # 保存为WAV文件
    sf.write(filename, audio, sr)
    print(f"创建测试音频: {filename}, 频率: {frequency} Hz")
    return filename

def test_pitch_analysis():
    """测试音调分析功能"""
    print("开始测试音频音调分析功能...\n")
    
    # 创建测试音频文件
    test_files = []
    frequencies = [440, 523.25, 440]  # A4, C5, A4 (第三个和第一个相同)
    notes = ["A4", "C5", "A4"]
    
    for i, (freq, note) in enumerate(zip(frequencies, notes)):
        filename = f"test_{note.replace('#', 'sharp')}.wav"
        create_test_audio(freq, duration=1, filename=filename)
        test_files.append(filename)
    
    # 初始化分析器
    analyzer = AudioPitchAnalyzer(tolerance=0.05)
    
    # 分析每个文件
    results = []
    for file in test_files:
        try:
            result = analyzer.analyze_pitch(file, method='multi')
            results.append(result)
            
            pitch = result['overall_pitch']
            print(f"文件: {file}")
            print(f"  检测频率: {pitch['frequency']:.2f} Hz")
            print(f"  检测音符: {pitch['note']}")
            print(f"  置信度: {pitch['confidence']:.2f}\n")
            
        except Exception as e:
            print(f"分析文件 {file} 时出错: {e}")
    
    # 测试比较功能
    if len(results) >= 2:
        print("=" * 50)
        print("测试音调比较功能")
        print("=" * 50)
        
        # 比较第一个和第二个文件（不同音调）
        comparison1 = analyzer.compare_pitches(results[0], results[1])
        print(f"比较 {results[0]['file_name']} vs {results[1]['file_name']}:")
        print(f"  音调是否相同: {comparison1['is_same_pitch']}")
        print(f"  频率差异: {comparison1['frequency_difference']:.2f} Hz")
        print(f"  相对误差: {comparison1['relative_error']:.1%}\n")
        
        # 比较第一个和第三个文件（相同音调）
        if len(results) >= 3:
            comparison2 = analyzer.compare_pitches(results[0], results[2])
            print(f"比较 {results[0]['file_name']} vs {results[2]['file_name']}:")
            print(f"  音调是否相同: {comparison2['is_same_pitch']}")
            print(f"  频率差异: {comparison2['frequency_difference']:.2f} Hz")
            print(f"  相对误差: {comparison2['relative_error']:.1%}\n")
    
    # 清理测试文件
    for file in test_files:
        try:
            os.remove(file)
            print(f"清理测试文件: {file}")
        except:
            pass
    
    print("\n测试完成！")

if __name__ == "__main__":
    test_pitch_analysis()
