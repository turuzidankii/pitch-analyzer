#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试音程变化分析功能
"""

import os
import sys
from audio_pitch_analyzer import AudioPitchAnalyzer
from audio_utils import AudioUtils

def test_pitch_contour():
    """测试音程分析功能"""
    
    # 检查是否有测试音频文件
    test_files = [
        "tom_chang1.wav",
        "CRYCHIC - 春日影_vocals_karaoke_noreverb_dry.wav"
    ]
    
    available_files = [f for f in test_files if os.path.exists(f)]
    
    if not available_files:
        print("未找到测试音频文件，创建合成音频进行测试...")
        # 使用create_samples创建测试音频
        os.system("python create_samples.py")
        available_files = [f for f in test_files if os.path.exists(f)]
    
    if not available_files:
        print("无法创建或找到测试音频文件")
        return False
    
    # 选择第一个可用文件
    test_file = available_files[0]
    print(f"使用测试文件: {test_file}")
    
    # 获取音频信息
    try:
        audio_info = AudioUtils.get_audio_info(test_file)
        duration = audio_info['duration']
        print(f"音频时长: {duration:.1f}秒")
        
        # 选择分析区间（前10秒或全部）
        start_time = 0
        end_time = min(10, duration - 1)
        
        if end_time <= start_time:
            print("音频文件太短，无法进行音程分析")
            return False
            
    except Exception as e:
        print(f"获取音频信息失败: {e}")
        return False
    
    # 创建分析器
    try:
        analyzer = AudioPitchAnalyzer(sr=22050)
        print(f"\n开始分析音程变化: {start_time}s - {end_time}s")
        
        # 分析音程变化
        contour_result = analyzer.analyze_pitch_contour(
            test_file, start_time, end_time, frame_size=0.1)
        
        # 打印结果
        print(f"\n{'='*50}")
        print(f"音程分析测试结果")
        print(f"{'='*50}")
        
        stats = contour_result['statistics']
        print(f"平均频率: {stats['avg_frequency']:.1f} Hz")
        print(f"音程范围: {stats['interval_range']:.1f} 半音")
        print(f"最高音程: +{stats['max_interval']:.1f} 半音")
        print(f"最低音程: {stats['min_interval']:.1f} 半音")
        print(f"平均置信度: {stats['avg_confidence']:.2f}")
        
        # 生成可视化图表
        save_path = f"{os.path.splitext(test_file)[0]}_contour_test.png"
        analyzer.visualize_pitch_contour(contour_result, save_path)
        
        print(f"\n✓ 测试成功完成")
        print(f"✓ 图表已保存: {save_path}")
        
        # 显示部分数据
        data = contour_result['analysis_data']
        print(f"\n数据样本 (前5个数据点):")
        for i in range(min(5, len(data['times']))):
            time = data['times'][i]
            freq = data['frequencies'][i]
            interval = data['intervals'][i]
            note = data['notes'][i]
            conf = data['confidences'][i]
            print(f"  {time:.1f}s: {freq:.1f}Hz ({note}) {interval:+.1f}半音 置信度:{conf:.2f}")
        
        return True
        
    except Exception as e:
        print(f"音程分析测试失败: {e}")
        return False

def test_command_line():
    """测试命令行功能"""
    test_files = [
        "tom_chang1.wav",
        "CRYCHIC - 春日影_vocals_karaoke_noreverb_dry.wav"
    ]
    
    available_files = [f for f in test_files if os.path.exists(f)]
    if not available_files:
        print("未找到测试音频文件")
        return False
    
    test_file = available_files[0]
    
    print(f"\n{'='*50}")
    print(f"测试命令行音程分析功能")
    print(f"{'='*50}")
    
    # 构建命令
    cmd = f"python main.py {test_file} --pitch-contour --start-time 0 --end-time 5 --frame-size 0.1 -v"
    print(f"执行命令: {cmd}")
    
    # 执行命令
    result = os.system(cmd)
    
    if result == 0:
        print("✓ 命令行测试成功")
        return True
    else:
        print("✗ 命令行测试失败")
        return False

if __name__ == "__main__":
    print("音程变化分析功能测试")
    print("=" * 50)
    
    # 测试核心功能
    success1 = test_pitch_contour()
    
    # 测试命令行功能
    success2 = test_command_line()
    
    if success1 and success2:
        print(f"\n🎉 所有测试通过！")
        sys.exit(0)
    else:
        print(f"\n❌ 测试失败")
        sys.exit(1)
