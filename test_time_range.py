#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试时间范围功能
"""

import numpy as np
import soundfile as sf
from audio_pitch_analyzer import AudioPitchAnalyzer
from audio_utils import AudioUtils

def create_test_audio_with_segments():
    """创建带有不同音调段落的测试音频"""
    sr = 22050
    segment_duration = 10  # 每段10秒
    
    # 创建三段不同音调的音频
    segments = [
        {"freq": 440, "note": "A4"},   # 0-10秒
        {"freq": 523.25, "note": "C5"}, # 10-20秒  
        {"freq": 659.25, "note": "E5"}, # 20-30秒
    ]
    
    print("创建测试音频文件...")
    
    # 生成完整音频
    full_audio = []
    for i, seg in enumerate(segments):
        t = np.linspace(0, segment_duration, int(sr * segment_duration))
        audio_seg = 0.3 * np.sin(2 * np.pi * seg["freq"] * t)
        
        # 添加渐变效果，避免突然的音调变化
        fade_samples = int(sr * 0.5)  # 0.5秒渐变
        if i > 0:  # 不是第一段，添加淡入
            audio_seg[:fade_samples] *= np.linspace(0, 1, fade_samples)
        if i < len(segments) - 1:  # 不是最后一段，添加淡出
            audio_seg[-fade_samples:] *= np.linspace(1, 0, fade_samples)
        
        full_audio.extend(audio_seg)
        print(f"段落 {i+1}: {seg['note']} ({seg['freq']} Hz) - {i*segment_duration}s 到 {(i+1)*segment_duration}s")
    
    # 保存音频文件
    filename = "test_multi_segments.wav"
    sf.write(filename, np.array(full_audio), sr)
    print(f"\n创建测试文件: {filename} (总时长: {len(segments)*segment_duration}秒)")
    return filename

def test_time_range_analysis():
    """测试时间范围分析功能"""
    print("=" * 60)
    print("测试时间范围音调分析功能")
    print("=" * 60)
    
    # 创建测试音频
    test_file = create_test_audio_with_segments()
    
    # 初始化分析器
    analyzer = AudioPitchAnalyzer()
    
    # 测试不同时间范围
    test_cases = [
        {"name": "完整音频", "start": None, "end": None},
        {"name": "第一段 (0-10秒)", "start": "0", "end": "10"},
        {"name": "第二段 (10-20秒)", "start": "10", "end": "20"},
        {"name": "第三段 (20-30秒)", "start": "20", "end": "30"},
        {"name": "前半部分 (0-15秒)", "start": "0", "end": "15"},
        {"name": "使用分:秒格式 (0:05-0:15)", "start": "0:05", "end": "0:15"},
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n{'='*40}")
        print(f"测试: {test_case['name']}")
        print(f"{'='*40}")
        
        try:
            result = analyzer.analyze_pitch(
                test_file, 
                start_time=test_case['start'],
                end_time=test_case['end']
            )
            results.append((test_case['name'], result))
            
            # 显示结果
            pitch = result['overall_pitch']
            time_range = result['time_range']
            
            print(f"检测结果:")
            print(f"  音调: {pitch['frequency']:.2f} Hz ({pitch['note']})")
            print(f"  置信度: {pitch['confidence']:.2f}")
            print(f"  实际分析时长: {time_range['actual_duration']:.2f}秒")
            
            if time_range['start_time'] or time_range['end_time']:
                start = time_range['start_time'] or "开始"
                end = time_range['end_time'] or "结束"
                print(f"  时间范围: {start} - {end}")
            
        except Exception as e:
            print(f"分析出错: {e}")
    
    # 测试时间解析功能
    print(f"\n{'='*40}")
    print("测试时间解析功能")
    print(f"{'='*40}")
    
    time_test_cases = [
        "1:30",     # 1分30秒
        "0:45",     # 45秒
        "2:15.5",   # 2分15.5秒
        "90",       # 90秒
        "120.5",    # 120.5秒
    ]
    
    for time_str in time_test_cases:
        try:
            seconds = AudioUtils.parse_time_string(time_str)
            formatted = AudioUtils.format_time(seconds)
            print(f"  {time_str} -> {seconds}秒 -> {formatted}")
        except Exception as e:
            print(f"  {time_str} -> 解析错误: {e}")
    
    # 清理测试文件
    import os
    try:
        os.remove(test_file)
        print(f"\n清理测试文件: {test_file}")
    except:
        pass
    
    print("\n时间范围分析测试完成！")

if __name__ == "__main__":
    test_time_range_analysis()
