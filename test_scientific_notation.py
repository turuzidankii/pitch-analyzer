#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试科学音高记号法的音程分析功能
"""

import os
import sys
from audio_pitch_analyzer import AudioPitchAnalyzer

def test_scientific_notation():
    """测试科学音高记号法显示"""
    
    # 检查测试文件
    test_files = [
        "sample_scale.wav",
        "sample_pitch_changing.wav", 
        "sample_A4.wav"
    ]
    
    available_files = [f for f in test_files if os.path.exists(f)]
    
    if not available_files:
        print("未找到测试文件，创建测试样本...")
        os.system("python create_complex_samples.py")
        available_files = [f for f in test_files if os.path.exists(f)]
    
    if not available_files:
        print("无法创建测试文件")
        return False
    
    analyzer = AudioPitchAnalyzer(sr=22050)
    
    print("🎵 科学音高记号法音程分析测试")
    print("=" * 60)
    
    for test_file in available_files:
        print(f"\n📁 分析文件: {test_file}")
        
        try:
            # 确定分析时间范围
            if "scale" in test_file:
                start_time, end_time = 0, 4
                frame_size = 0.1
            elif "changing" in test_file:
                start_time, end_time = 0, 5
                frame_size = 0.05
            else:
                start_time, end_time = 0, 3
                frame_size = 0.1
            
            print(f"⏱️  时间范围: {start_time}s - {end_time}s (帧大小: {frame_size}s)")
            
            # 分析音程变化
            contour_result = analyzer.analyze_pitch_contour(
                test_file, start_time, end_time, frame_size)
            
            # 显示基本统计
            stats = contour_result['statistics']
            print(f"📊 统计信息:")
            print(f"   平均频率: {stats['avg_frequency']:.1f} Hz")
            print(f"   音程范围: {stats['interval_range']:.1f} 半音")
            print(f"   最高音程: +{stats['max_interval']:.1f} 半音")
            print(f"   最低音程: {stats['min_interval']:.1f} 半音")
            print(f"   置信度: {stats['avg_confidence']:.2f}")
            
            # 生成科学音高记号法图表
            save_path = f"{os.path.splitext(test_file)[0]}_scientific_notation.png"
            analyzer.visualize_pitch_contour(contour_result, save_path)
            print(f"🎨 科学音高记号法图表已保存: {save_path}")
            
            # 显示部分音符数据
            data = contour_result['analysis_data']
            notes = data['notes']
            valid_notes = [note for note in notes if note != 'Silent']
            
            if valid_notes:
                unique_notes = sorted(list(set(valid_notes)))
                print(f"🎼 检测到的音符: {', '.join(unique_notes[:10])}")
                if len(unique_notes) > 10:
                    print(f"   ... 共 {len(unique_notes)} 个不同音符")
            
        except Exception as e:
            print(f"❌ 分析失败: {e}")
            continue
    
    print(f"\n✅ 科学音高记号法测试完成!")
    print(f"📝 改进说明:")
    print(f"   • 右侧Y轴显示科学音高记号（C4, D4, E4等）")
    print(f"   • 音程变化点自动标注音符名称")
    print(f"   • 更清晰的音程参考线")
    print(f"   • 适应性的音符标记范围")
    
    return True

def demo_usage():
    """演示科学音高记号法的使用方法"""
    print(f"\n🚀 使用方法演示:")
    print(f"=" * 40)
    
    commands = [
        "python main.py sample_scale.wav --pitch-contour --start-time 0 --end-time 4",
        "python main.py sample_pitch_changing.wav --pitch-contour --start-time 0 --end-time 5 --frame-size 0.05",
        "python main.py audio.wav --pitch-contour --start-time 1:00 --end-time 1:30 -v"
    ]
    
    for i, cmd in enumerate(commands, 1):
        print(f"{i}. {cmd}")
    
    print(f"\n📈 图表说明:")
    print(f"   • 主折线图: 以半音为单位的音程变化")
    print(f"   • 右侧轴: 科学音高记号法（C4, D#4, F5等）")
    print(f"   • 黄色标注: 显著音程变化点的音符名称")
    print(f"   • 红色基线: 起始音符参考线")

if __name__ == "__main__":
    success = test_scientific_notation()
    demo_usage()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
