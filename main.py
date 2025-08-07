#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音频音调比较工具
主程序入口，提供命令行界面
"""

import argparse
import sys
import os
from typing import List
from audio_pitch_analyzer import AudioPitchAnalyzer

def print_analysis_result(result: dict, verbose: bool = False):
    """打印分析结果"""
    overall = result['overall_pitch']
    time_range = result.get('time_range', {})
    
    print(f"\n{'='*50}")
    print(f"文件: {result['file_name']}")
    
    # 显示时间范围信息
    if time_range.get('start_time') or time_range.get('end_time'):
        start = time_range.get('start_time', '开始')
        end = time_range.get('end_time', '结束')
        actual_duration = time_range.get('actual_duration', 0)
        print(f"时间范围: {start} - {end} (实际分析时长: {actual_duration:.2f}秒)")
    
    print(f"{'='*50}")
    print(f"检测到的音调:")
    print(f"  频率: {overall['frequency']:.2f} Hz")
    print(f"  音符: {overall['note']}")
    print(f"  置信度: {overall['confidence']:.2f}")
    print(f"  检测方法: {overall['method']}")
    
    if verbose and result['segment_pitches']:
        print(f"\n有声片段详情:")
        for i, seg in enumerate(result['segment_pitches'], 1):
            print(f"  片段 {i}: {seg['frequency']:.2f} Hz ({seg['note']}) "
                  f"[{seg['start_time']:.2f}s - {seg['end_time']:.2f}s]")

def print_comparison_result(comparison: dict):
    """打印比较结果"""
    print(f"\n{'='*50}")
    print(f"音调比较结果")
    print(f"{'='*50}")
    print(f"文件1: {comparison['files'][0]}")
    print(f"文件2: {comparison['files'][1]}")
    print(f"\n音调信息:")
    print(f"  文件1: {comparison['frequency1']:.2f} Hz ({comparison['note1']})")
    print(f"  文件2: {comparison['frequency2']:.2f} Hz ({comparison['note2']})")
    print(f"  频率差异: {comparison['frequency_difference']:.2f} Hz")
    print(f"  相对误差: {comparison['relative_error']:.1%}")
    
    print(f"\n比较结果:")
    if comparison['is_same_pitch']:
        print(f"  ✓ 音调相同 (误差 ≤ {comparison['tolerance']:.1%})")
    else:
        print(f"  ✗ 音调不同 (误差 > {comparison['tolerance']:.1%})")
    
    if comparison['same_note']:
        print(f"  ✓ 音符相同")
    else:
        print(f"  ✗ 音符不同")
    
    print(f"  置信度: {comparison['confidence']:.2f}")
    
    # 片段相似性
    seg_sim = comparison['segment_similarity']
    if seg_sim['total_comparisons'] > 0:
        print(f"\n片段级分析:")
        print(f"  平均相似度: {seg_sim['avg_similarity']:.2f}")
        print(f"  匹配片段比例: {seg_sim['match_ratio']:.1%}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="音频音调比较工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py audio1.wav audio2.wav                    # 比较两个音频文件
  python main.py audio1.wav audio2.wav -v                 # 详细输出
  python main.py audio1.wav audio2.wav -t 0.1             # 设置10%的容差
  python main.py audio1.wav audio2.wav -m yin             # 使用YIN算法
  python main.py *.wav                                     # 比较多个文件
  python main.py audio1.wav --analyze-only                # 仅分析不比较
  python main.py audio1.wav --visualize                   # 生成可视化图表
  python main.py audio1.wav --start-time 1:00             # 从1分钟开始分析
  python main.py audio1.wav --start-time 1:00 --end-time 1:25  # 分析1:00到1:25
  python main.py audio1.wav --start-time 60 --end-time 85      # 分析60秒到85秒
        """
    )
    
    parser.add_argument(
        'files',
        nargs='+',
        help='音频文件路径（支持 wav, mp3, flac 等格式）'
    )
    
    parser.add_argument(
        '-t', '--tolerance',
        type=float,
        default=0.05,
        help='音调比较容差（相对误差，默认: 0.05 即 5%%）'
    )
    
    parser.add_argument(
        '-m', '--method',
        choices=['multi', 'piptrack', 'yin', 'autocorr'],
        default='multi',
        help='音调检测方法（默认: multi）'
    )
    
    parser.add_argument(
        '-sr', '--sample-rate',
        type=int,
        default=22050,
        help='采样率（默认: 22050）'
    )
    
    parser.add_argument(
        '--start-time',
        type=str,
        help='开始时间，格式: "1:30" 或 "90" (秒)'
    )
    
    parser.add_argument(
        '--end-time',
        type=str,
        help='结束时间，格式: "1:30" 或 "90" (秒)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='详细输出'
    )
    
    parser.add_argument(
        '--analyze-only',
        action='store_true',
        help='仅分析音调，不进行比较'
    )
    
    parser.add_argument(
        '--visualize',
        action='store_true',
        help='生成可视化图表'
    )
    
    args = parser.parse_args()
    
    # 检查文件
    valid_files = []
    for file_path in args.files:
        if not os.path.exists(file_path):
            print(f"警告: 文件不存在: {file_path}")
            continue
        valid_files.append(file_path)
    
    if not valid_files:
        print("错误: 没有找到有效的音频文件")
        sys.exit(1)
    
    if len(valid_files) == 1 and not args.analyze_only:
        print("提示: 只有一个文件，将进行音调分析（不进行比较）")
        args.analyze_only = True
    
    # 创建分析器
    try:
        analyzer = AudioPitchAnalyzer(sr=args.sample_rate, tolerance=args.tolerance)
    except Exception as e:
        print(f"错误: 无法创建分析器: {e}")
        sys.exit(1)
    
    try:
        if args.analyze_only or len(valid_files) == 1:
            # 仅分析模式
            for file_path in valid_files:
                try:
                    print(f"\n正在分析: {file_path}")
                    result = analyzer.analyze_pitch(file_path, method=args.method,
                                                   start_time=args.start_time,
                                                   end_time=args.end_time)
                    print_analysis_result(result, verbose=args.verbose)
                    
                    if args.visualize:
                        save_path = f"{os.path.splitext(file_path)[0]}_analysis.png"
                        analyzer.visualize_pitch_analysis(result, save_path)
                        
                except Exception as e:
                    print(f"分析文件 {file_path} 时出错: {e}")
                    continue
        
        elif len(valid_files) == 2:
            # 双文件比较模式
            print(f"正在比较两个音频文件...")
            
            try:
                result1 = analyzer.analyze_pitch(valid_files[0], method=args.method,
                                                start_time=args.start_time,
                                                end_time=args.end_time)
                result2 = analyzer.analyze_pitch(valid_files[1], method=args.method,
                                                start_time=args.start_time,
                                                end_time=args.end_time)
                
                if args.verbose:
                    print_analysis_result(result1, verbose=True)
                    print_analysis_result(result2, verbose=True)
                
                comparison = analyzer.compare_pitches(result1, result2)
                print_comparison_result(comparison)
                
                if args.visualize:
                    save_path1 = f"{os.path.splitext(valid_files[0])[0]}_analysis.png"
                    save_path2 = f"{os.path.splitext(valid_files[1])[0]}_analysis.png"
                    analyzer.visualize_pitch_analysis(result1, save_path1)
                    analyzer.visualize_pitch_analysis(result2, save_path2)
                
            except Exception as e:
                print(f"比较文件时出错: {e}")
                sys.exit(1)
        
        else:
            # 多文件比较模式
            print(f"正在比较 {len(valid_files)} 个音频文件...")
            
            try:
                results = analyzer.compare_multiple_files(valid_files,
                                                         start_time=args.start_time,
                                                         end_time=args.end_time)
                
                # 打印每个文件的分析结果
                if args.verbose:
                    for result in results['individual_results']:
                        print_analysis_result(result, verbose=True)
                
                # 打印比较摘要
                summary = results['summary']
                print(f"\n{'='*50}")
                print(f"多文件比较摘要")
                print(f"{'='*50}")
                print(f"文件数量: {results['file_count']}")
                print(f"比较对数: {summary['total_pairs']}")
                print(f"音调相同的对数: {summary['same_pitch_pairs']}")
                print(f"相同音调比例: {summary['same_pitch_ratio']:.1%}")
                print(f"平均置信度: {summary['average_confidence']:.2f}")
                
                # 详细比较结果
                if args.verbose:
                    print(f"\n详细比较结果:")
                    for i, comp in enumerate(results['pairwise_comparisons'], 1):
                        print(f"\n比较 {i}: {comp['files'][0]} vs {comp['files'][1]}")
                        print(f"  结果: {'相同' if comp['is_same_pitch'] else '不同'}")
                        print(f"  频率: {comp['frequency1']:.1f} Hz vs {comp['frequency2']:.1f} Hz")
                        print(f"  误差: {comp['relative_error']:.1%}")
                
            except Exception as e:
                print(f"多文件比较时出错: {e}")
                sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n用户取消操作")
        sys.exit(0)
    except Exception as e:
        print(f"程序执行出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
