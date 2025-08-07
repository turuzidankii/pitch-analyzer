import numpy as np
import librosa
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from typing import Tuple, Optional
import warnings

warnings.filterwarnings('ignore')

class PitchDetector:
    """音调检测器类"""
    
    def __init__(self, sr: int = 22050, hop_length: int = 512):
        """
        初始化音调检测器
        
        Args:
            sr: 采样率
            hop_length: 帧移长度
        """
        self.sr = sr
        self.hop_length = hop_length
    
    def detect_fundamental_frequency(self, y: np.ndarray) -> Tuple[float, float]:
        """
        检测音频的基音频率
        
        Args:
            y: 音频信号数组
            
        Returns:
            Tuple[float, float]: (基音频率, 置信度)
        """
        # 使用librosa的piptrack进行基音检测
        pitches, magnitudes = librosa.piptrack(
            y=y, 
            sr=self.sr, 
            hop_length=self.hop_length,
            threshold=0.1,
            fmin=80,   # 最低频率80Hz
            fmax=2000  # 最高频率2000Hz
        )
        
        # 提取最强的基音
        fundamental_frequencies = []
        confidences = []
        
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            confidence = magnitudes[index, t]
            
            if pitch > 0:
                fundamental_frequencies.append(pitch)
                confidences.append(confidence)
        
        if not fundamental_frequencies:
            return 0.0, 0.0
        
        # 计算加权平均基音频率
        fundamental_frequencies = np.array(fundamental_frequencies)
        confidences = np.array(confidences)
        
        weighted_frequency = np.average(fundamental_frequencies, weights=confidences)
        avg_confidence = np.mean(confidences)
        
        return float(weighted_frequency), float(avg_confidence)
    
    def detect_pitch_yin(self, y: np.ndarray) -> float:
        """
        使用YIN算法检测音调
        
        Args:
            y: 音频信号数组
            
        Returns:
            float: 基音频率
        """
        # 使用librosa的yin算法
        f0 = librosa.yin(
            y, 
            fmin=80, 
            fmax=2000,
            sr=self.sr,
            hop_length=self.hop_length
        )
        
        # 过滤掉0值并计算中位数
        f0_filtered = f0[f0 > 0]
        if len(f0_filtered) == 0:
            return 0.0
        
        return float(np.median(f0_filtered))
    
    def autocorrelation_pitch(self, y: np.ndarray) -> float:
        """
        使用自相关方法检测音调
        
        Args:
            y: 音频信号数组
            
        Returns:
            float: 基音频率
        """
        # 归一化音频信号
        y = y / np.max(np.abs(y))
        
        # 计算自相关
        correlation = np.correlate(y, y, mode='full')
        correlation = correlation[len(correlation)//2:]
        
        # 寻找自相关峰值
        min_period = int(self.sr / 2000)  # 最小周期对应最高频率2000Hz
        max_period = int(self.sr / 80)    # 最大周期对应最低频率80Hz
        
        if max_period >= len(correlation):
            return 0.0
        
        # 在有效范围内寻找峰值
        peaks, _ = find_peaks(
            correlation[min_period:max_period], 
            height=0.1 * np.max(correlation)
        )
        
        if len(peaks) == 0:
            return 0.0
        
        # 选择最强的峰值
        peak_heights = correlation[min_period:max_period][peaks]
        strongest_peak_idx = peaks[np.argmax(peak_heights)]
        period = strongest_peak_idx + min_period
        
        frequency = self.sr / period
        return float(frequency)
    
    def detect_pitch_multi_method(self, y: np.ndarray) -> Tuple[float, float]:
        """
        使用多种方法检测音调并返回最可靠的结果
        
        Args:
            y: 音频信号数组
            
        Returns:
            Tuple[float, float]: (基音频率, 置信度)
        """
        # 方法1: piptrack
        freq1, conf1 = self.detect_fundamental_frequency(y)
        
        # 方法2: YIN算法
        freq2 = self.detect_pitch_yin(y)
        
        # 方法3: 自相关
        freq3 = self.autocorrelation_pitch(y)
        
        # 收集有效的频率结果
        frequencies = []
        if freq1 > 0:
            frequencies.append((freq1, conf1))
        if freq2 > 0:
            frequencies.append((freq2, 0.8))  # YIN算法给予较高置信度
        if freq3 > 0:
            frequencies.append((freq3, 0.6))  # 自相关给予中等置信度
        
        if not frequencies:
            return 0.0, 0.0
        
        # 如果只有一个有效结果，直接返回
        if len(frequencies) == 1:
            return frequencies[0]
        
        # 多个结果时，选择最一致的
        freqs = [f[0] for f in frequencies]
        confs = [f[1] for f in frequencies]
        
        # 计算频率的一致性
        freq_std = np.std(freqs)
        if freq_std < 10:  # 频率差异小于10Hz，认为一致
            # 返回加权平均
            weighted_freq = np.average(freqs, weights=confs)
            avg_conf = np.mean(confs)
            return float(weighted_freq), float(avg_conf)
        else:
            # 返回置信度最高的结果
            max_conf_idx = np.argmax(confs)
            return frequencies[max_conf_idx]
    
    def frequency_to_note(self, frequency: float) -> str:
        """
        将频率转换为音符名称
        
        Args:
            frequency: 频率值
            
        Returns:
            str: 音符名称 (如 C4, A4等)
        """
        if frequency <= 0:
            return "Unknown"
        
        # A4 = 440Hz
        A4_freq = 440.0
        A4_note_number = 69
        
        # 计算相对于A4的半音数
        note_number = round(12 * np.log2(frequency / A4_freq) + A4_note_number)
        
        # 音符名称
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        octave = (note_number - 12) // 12
        note_name = note_names[note_number % 12]
        
        return f"{note_name}{octave}"
