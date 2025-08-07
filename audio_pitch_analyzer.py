import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Optional, List, Dict, Any
from pitch_detector import PitchDetector
from audio_utils import AudioUtils
import os

class AudioPitchAnalyzer:
    """音频音调分析器主类"""
    
    def __init__(self, sr: int = 22050, tolerance: float = 0.05):
        """
        初始化音调分析器
        
        Args:
            sr: 采样率
            tolerance: 音调比较容差（相对误差）
        """
        self.sr = sr
        self.tolerance = tolerance
        self.pitch_detector = PitchDetector(sr=sr)
        
    def analyze_pitch(self, file_path: str, method: str = 'multi', 
                     start_time: Optional[str] = None, 
                     end_time: Optional[str] = None) -> Dict[str, Any]:
        """
        分析音频文件的音调
        
        Args:
            file_path: 音频文件路径
            method: 检测方法 ('multi', 'piptrack', 'yin', 'autocorr')
            start_time: 开始时间，支持格式 "1:30" 或 "90"
            end_time: 结束时间，支持格式 "1:30" 或 "90"
            
        Returns:
            Dict[str, Any]: 分析结果
        """
        if not AudioUtils.is_supported_format(file_path):
            raise ValueError(f"不支持的音频格式: {file_path}")
        
        # 解析时间参数
        offset = 0.0
        duration = None
        
        if start_time is not None:
            offset = AudioUtils.parse_time_string(start_time)
        
        if end_time is not None:
            end_seconds = AudioUtils.parse_time_string(end_time)
            if offset > 0:
                duration = end_seconds - offset
            else:
                duration = end_seconds
            
            if duration <= 0:
                raise ValueError("结束时间必须大于开始时间")
        
        # 加载音频
        time_info = ""
        if start_time or end_time:
            if start_time and end_time:
                time_info = f" (从 {start_time} 到 {end_time})"
            elif start_time:
                time_info = f" (从 {start_time} 开始)"
            elif end_time:
                time_info = f" (到 {end_time} 结束)"
        
        print(f"正在分析: {os.path.basename(file_path)}{time_info}")
        y, sr = AudioUtils.load_audio(file_path, sr=self.sr, duration=duration, offset=offset)
        
        # 预处理
        y_processed = AudioUtils.preprocess_audio(y, sr)
        
        # 获取音频信息
        audio_info = AudioUtils.get_audio_info(file_path)
        
        # 检测音调
        if method == 'multi':
            frequency, confidence = self.pitch_detector.detect_pitch_multi_method(y_processed)
        elif method == 'piptrack':
            frequency, confidence = self.pitch_detector.detect_fundamental_frequency(y_processed)
        elif method == 'yin':
            frequency = self.pitch_detector.detect_pitch_yin(y_processed)
            confidence = 0.8 if frequency > 0 else 0.0
        elif method == 'autocorr':
            frequency = self.pitch_detector.autocorrelation_pitch(y_processed)
            confidence = 0.6 if frequency > 0 else 0.0
        else:
            raise ValueError(f"未知的检测方法: {method}")
        
        # 转换为音符
        note = self.pitch_detector.frequency_to_note(frequency)
        
        # 找到有声片段
        voiced_segments = AudioUtils.find_voiced_segments(y_processed, sr)
        
        # 分析每个有声片段
        segment_pitches = []
        for start_time, end_time in voiced_segments[:5]:  # 最多分析前5个片段
            try:
                segment = AudioUtils.extract_audio_segment(y_processed, sr, start_time, end_time)
                if len(segment) > sr * 0.05:  # 至少50ms
                    seg_freq, seg_conf = self.pitch_detector.detect_pitch_multi_method(segment)
                    if seg_freq > 0:
                        segment_pitches.append({
                            'start_time': start_time,
                            'end_time': end_time,
                            'frequency': seg_freq,
                            'confidence': seg_conf,
                            'note': self.pitch_detector.frequency_to_note(seg_freq)
                        })
            except Exception:
                continue
        
        result = {
            'file_path': file_path,
            'file_name': os.path.basename(file_path),
            'audio_info': audio_info,
            'time_range': {
                'start_time': start_time,
                'end_time': end_time,
                'offset_seconds': offset,
                'duration_seconds': duration,
                'actual_duration': len(y) / sr
            },
            'overall_pitch': {
                'frequency': frequency,
                'confidence': confidence,
                'note': note,
                'method': method
            },
            'voiced_segments': voiced_segments,
            'segment_pitches': segment_pitches,
            'analysis_params': {
                'sample_rate': sr,
                'method': method,
                'tolerance': self.tolerance
            }
        }
        
        return result
    
    def compare_pitches(self, result1: Dict[str, Any], result2: Dict[str, Any]) -> Dict[str, Any]:
        """
        比较两个音调分析结果
        
        Args:
            result1: 第一个音频的分析结果
            result2: 第二个音频的分析结果
            
        Returns:
            Dict[str, Any]: 比较结果
        """
        freq1 = result1['overall_pitch']['frequency']
        freq2 = result2['overall_pitch']['frequency']
        conf1 = result1['overall_pitch']['confidence']
        conf2 = result2['overall_pitch']['confidence']
        
        # 基本有效性检查
        if freq1 <= 0 or freq2 <= 0:
            return {
                'is_same_pitch': False,
                'confidence': 0.0,
                'frequency_difference': abs(freq1 - freq2),
                'relative_error': float('inf'),
                'note1': result1['overall_pitch']['note'],
                'note2': result2['overall_pitch']['note'],
                'reason': '无法检测到有效音调'
            }
        
        # 计算频率差异
        freq_diff = abs(freq1 - freq2)
        relative_error = freq_diff / max(freq1, freq2)
        
        # 判断是否相同
        is_same = relative_error <= self.tolerance
        
        # 计算整体置信度
        overall_confidence = min(conf1, conf2) * (1 - relative_error)
        
        # 比较音符
        note1 = result1['overall_pitch']['note']
        note2 = result2['overall_pitch']['note']
        same_note = note1 == note2
        
        # 分析片段级别的一致性
        segment_similarity = self._analyze_segment_similarity(result1, result2)
        
        return {
            'is_same_pitch': is_same,
            'same_note': same_note,
            'confidence': overall_confidence,
            'frequency1': freq1,
            'frequency2': freq2,
            'frequency_difference': freq_diff,
            'relative_error': relative_error,
            'tolerance': self.tolerance,
            'note1': note1,
            'note2': note2,
            'segment_similarity': segment_similarity,
            'files': [result1['file_name'], result2['file_name']]
        }
    
    def _analyze_segment_similarity(self, result1: Dict[str, Any], result2: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析片段级别的音调相似性
        
        Args:
            result1: 第一个音频的分析结果
            result2: 第二个音频的分析结果
            
        Returns:
            Dict[str, Any]: 片段相似性分析
        """
        segments1 = result1['segment_pitches']
        segments2 = result2['segment_pitches']
        
        if not segments1 or not segments2:
            return {
                'avg_similarity': 0.0,
                'matching_segments': 0,
                'total_comparisons': 0
            }
        
        similarities = []
        matching_count = 0
        
        # 比较所有片段组合
        for seg1 in segments1:
            for seg2 in segments2:
                freq1 = seg1['frequency']
                freq2 = seg2['frequency']
                
                if freq1 > 0 and freq2 > 0:
                    relative_error = abs(freq1 - freq2) / max(freq1, freq2)
                    similarity = 1 - relative_error
                    similarities.append(similarity)
                    
                    if relative_error <= self.tolerance:
                        matching_count += 1
        
        avg_similarity = np.mean(similarities) if similarities else 0.0
        
        return {
            'avg_similarity': avg_similarity,
            'matching_segments': matching_count,
            'total_comparisons': len(similarities),
            'match_ratio': matching_count / len(similarities) if similarities else 0.0
        }
    
    def visualize_pitch_analysis(self, result: Dict[str, Any], save_path: Optional[str] = None):
        """
        可视化音调分析结果
        
        Args:
            result: 分析结果
            save_path: 保存路径（可选）
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f"Pitch Analysis: {result['file_name']}", fontsize=16)
        
        # 加载音频用于可视化
        y, sr = AudioUtils.load_audio(result['file_path'], sr=self.sr)
        y_processed = AudioUtils.preprocess_audio(y, sr)
        
        # 1. 波形图
        time = np.linspace(0, len(y_processed) / sr, len(y_processed))
        axes[0, 0].plot(time, y_processed)
        axes[0, 0].set_title('Audio Waveform')
        axes[0, 0].set_xlabel('Time (seconds)')
        axes[0, 0].set_ylabel('Amplitude')
        axes[0, 0].grid(True)
        
        # 标记有声片段
        for start, end in result['voiced_segments'][:3]:
            axes[0, 0].axvspan(start, end, alpha=0.3, color='yellow', label='Voiced Segments')
        
        # 2. 频谱图
        import librosa.display
        S = librosa.stft(y_processed)
        S_db = librosa.amplitude_to_db(np.abs(S), ref=np.max)
        img = librosa.display.specshow(S_db, x_axis='time', y_axis='hz', sr=sr, ax=axes[0, 1])
        axes[0, 1].set_title('Spectrogram')
        plt.colorbar(img, ax=axes[0, 1], format='%+2.0f dB')
        
        # 3. 音调检测结果
        overall_pitch = result['overall_pitch']
        axes[1, 0].bar(['Frequency (Hz)', 'Confidence'], 
                      [overall_pitch['frequency'], overall_pitch['confidence'] * 100])
        axes[1, 0].set_title(f"Overall Pitch: {overall_pitch['note']}")
        axes[1, 0].set_ylabel('Value')
        
        # 4. 片段音调分布
        if result['segment_pitches']:
            segment_freqs = [seg['frequency'] for seg in result['segment_pitches']]
            axes[1, 1].hist(segment_freqs, bins=10, alpha=0.7, edgecolor='black')
            axes[1, 1].axvline(overall_pitch['frequency'], color='red', linestyle='--', 
                              label=f"Overall Pitch: {overall_pitch['frequency']:.1f} Hz")
            axes[1, 1].set_title('Segment Pitch Distribution')
            axes[1, 1].set_xlabel('Frequency (Hz)')
            axes[1, 1].set_ylabel('Segment Count')
            axes[1, 1].legend()
            axes[1, 1].grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Chart saved to: {save_path}")
        
        plt.show()
    
    def compare_multiple_files(self, file_paths: List[str], 
                              start_time: Optional[str] = None,
                              end_time: Optional[str] = None) -> Dict[str, Any]:
        """
        比较多个音频文件的音调
        
        Args:
            file_paths: 音频文件路径列表
            start_time: 开始时间
            end_time: 结束时间
            
        Returns:
            Dict[str, Any]: 比较结果
        """
        if len(file_paths) < 2:
            raise ValueError("至少需要两个音频文件进行比较")
        
        # 分析所有文件
        results = []
        for file_path in file_paths:
            try:
                result = self.analyze_pitch(file_path, start_time=start_time, end_time=end_time)
                results.append(result)
            except Exception as e:
                print(f"分析文件 {file_path} 时出错: {e}")
                continue
        
        if len(results) < 2:
            raise ValueError("成功分析的音频文件少于2个")
        
        # 进行两两比较
        comparisons = []
        for i in range(len(results)):
            for j in range(i + 1, len(results)):
                comparison = self.compare_pitches(results[i], results[j])
                comparisons.append(comparison)
        
        # 统计分析
        same_pitch_count = sum(1 for comp in comparisons if comp['is_same_pitch'])
        avg_confidence = np.mean([comp['confidence'] for comp in comparisons])
        
        return {
            'file_count': len(results),
            'individual_results': results,
            'pairwise_comparisons': comparisons,
            'summary': {
                'same_pitch_pairs': same_pitch_count,
                'total_pairs': len(comparisons),
                'same_pitch_ratio': same_pitch_count / len(comparisons),
                'average_confidence': avg_confidence
            }
        }
