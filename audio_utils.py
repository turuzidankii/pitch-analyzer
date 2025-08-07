import numpy as np
import librosa
import soundfile as sf
from pydub import AudioSegment
import os
from typing import Tuple, Optional
import warnings

warnings.filterwarnings('ignore')

class AudioUtils:
    """音频处理工具类"""
    
    @staticmethod
    def load_audio(file_path: str, sr: int = 22050, duration: Optional[float] = None, 
                   offset: float = 0.0) -> Tuple[np.ndarray, int]:
        """
        加载音频文件
        
        Args:
            file_path: 音频文件路径
            sr: 目标采样率
            duration: 加载时长（秒），None为全部加载
            offset: 开始时间偏移（秒）
            
        Returns:
            Tuple[np.ndarray, int]: (音频数据, 采样率)
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"音频文件不存在: {file_path}")
        
        try:
            # 使用librosa加载音频，支持offset和duration
            y, sr_original = librosa.load(file_path, sr=sr, duration=duration, 
                                        offset=offset, mono=True)
            return y, sr
        except Exception as e:
            print(f"使用librosa加载失败，尝试使用pydub: {e}")
            return AudioUtils._load_audio_with_pydub(file_path, sr, duration, offset)
    
    @staticmethod
    def _load_audio_with_pydub(file_path: str, sr: int = 22050, 
                              duration: Optional[float] = None, 
                              offset: float = 0.0) -> Tuple[np.ndarray, int]:
        """
        使用pydub加载音频文件（备用方案）
        
        Args:
            file_path: 音频文件路径
            sr: 目标采样率
            duration: 加载时长（秒）
            offset: 开始时间偏移（秒）
            
        Returns:
            Tuple[np.ndarray, int]: (音频数据, 采样率)
        """
        try:
            # 使用pydub加载
            audio = AudioSegment.from_file(file_path)
            
            # 转换为单声道
            if audio.channels > 1:
                audio = audio.set_channels(1)
            
            # 重采样
            if audio.frame_rate != sr:
                audio = audio.set_frame_rate(sr)
            
            # 计算开始和结束位置（毫秒）
            start_ms = int(offset * 1000)
            end_ms = len(audio)
            if duration is not None:
                end_ms = min(start_ms + int(duration * 1000), len(audio))
            
            # 截取指定片段
            if start_ms > 0 or end_ms < len(audio):
                audio = audio[start_ms:end_ms]
            
            # 转换为numpy数组
            y = np.array(audio.get_array_of_samples(), dtype=np.float32)
            y = y / (2**15)  # 归一化到[-1, 1]
            
            return y, sr
        except Exception as e:
            raise Exception(f"无法加载音频文件 {file_path}: {e}")
    
    @staticmethod
    def preprocess_audio(y: np.ndarray, sr: int) -> np.ndarray:
        """
        预处理音频信号
        
        Args:
            y: 音频信号
            sr: 采样率
            
        Returns:
            np.ndarray: 预处理后的音频信号
        """
        # 移除静音部分
        y_trimmed, _ = librosa.effects.trim(y, top_db=20)
        
        # 如果音频太短，返回原始音频
        if len(y_trimmed) < sr * 0.1:  # 少于0.1秒
            y_trimmed = y
        
        # 归一化
        if np.max(np.abs(y_trimmed)) > 0:
            y_trimmed = y_trimmed / np.max(np.abs(y_trimmed))
        
        # 高通滤波器，移除低频噪声
        y_filtered = librosa.effects.preemphasis(y_trimmed)
        
        return y_filtered
    
    @staticmethod
    def get_audio_info(file_path: str) -> dict:
        """
        获取音频文件信息
        
        Args:
            file_path: 音频文件路径
            
        Returns:
            dict: 音频信息
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"音频文件不存在: {file_path}")
        
        try:
            # 使用soundfile获取信息
            info = sf.info(file_path)
            return {
                'duration': info.duration,
                'sample_rate': info.samplerate,
                'channels': info.channels,
                'format': info.format,
                'subtype': info.subtype,
                'frames': info.frames
            }
        except Exception:
            try:
                # 备用方案：使用pydub
                audio = AudioSegment.from_file(file_path)
                return {
                    'duration': len(audio) / 1000.0,  # 转换为秒
                    'sample_rate': audio.frame_rate,
                    'channels': audio.channels,
                    'format': 'unknown',
                    'subtype': 'unknown',
                    'frames': len(audio.get_array_of_samples())
                }
            except Exception as e:
                raise Exception(f"无法获取音频文件信息: {e}")
    
    @staticmethod
    def extract_audio_segment(y: np.ndarray, sr: int, start_time: float, end_time: float) -> np.ndarray:
        """
        提取音频片段
        
        Args:
            y: 音频信号
            sr: 采样率
            start_time: 开始时间（秒）
            end_time: 结束时间（秒）
            
        Returns:
            np.ndarray: 提取的音频片段
        """
        start_sample = int(start_time * sr)
        end_sample = int(end_time * sr)
        
        # 确保索引在有效范围内
        start_sample = max(0, start_sample)
        end_sample = min(len(y), end_sample)
        
        if start_sample >= end_sample:
            raise ValueError("无效的时间范围")
        
        return y[start_sample:end_sample]
    
    @staticmethod
    def calculate_rms_energy(y: np.ndarray, frame_length: int = 2048, hop_length: int = 512) -> np.ndarray:
        """
        计算音频的RMS能量
        
        Args:
            y: 音频信号
            frame_length: 帧长度
            hop_length: 帧移
            
        Returns:
            np.ndarray: RMS能量数组
        """
        return librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
    
    @staticmethod
    def find_voiced_segments(y: np.ndarray, sr: int, min_duration: float = 0.1) -> list:
        """
        找到有声音的片段
        
        Args:
            y: 音频信号
            sr: 采样率
            min_duration: 最小片段长度（秒）
            
        Returns:
            list: 有声片段的时间范围列表 [(start1, end1), (start2, end2), ...]
        """
        # 计算RMS能量
        rms = AudioUtils.calculate_rms_energy(y)
        
        # 计算能量阈值
        energy_threshold = np.mean(rms) * 0.1
        
        # 找到高能量帧
        voiced_frames = rms > energy_threshold
        
        # 转换为时间
        hop_length = 512
        frame_times = librosa.frames_to_time(np.arange(len(voiced_frames)), sr=sr, hop_length=hop_length)
        
        # 找到连续的有声片段
        segments = []
        start_time = None
        
        for i, is_voiced in enumerate(voiced_frames):
            if is_voiced and start_time is None:
                start_time = frame_times[i]
            elif not is_voiced and start_time is not None:
                end_time = frame_times[i]
                if end_time - start_time >= min_duration:
                    segments.append((start_time, end_time))
                start_time = None
        
        # 处理最后一个片段
        if start_time is not None:
            end_time = frame_times[-1]
            if end_time - start_time >= min_duration:
                segments.append((start_time, end_time))
        
        return segments
    
    @staticmethod
    def supported_formats() -> list:
        """
        返回支持的音频格式列表
        
        Returns:
            list: 支持的文件扩展名列表
        """
        return ['.wav', '.mp3', '.flac', '.m4a', '.aac', '.ogg', '.wma']
    
    @staticmethod
    def is_supported_format(file_path: str) -> bool:
        """
        检查文件格式是否支持
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否支持
        """
        _, ext = os.path.splitext(file_path.lower())
        return ext in AudioUtils.supported_formats()
    
    @staticmethod
    def parse_time_string(time_str: str) -> float:
        """
        解析时间字符串为秒数
        
        Args:
            time_str: 时间字符串，支持格式：
                     - "1:30" (1分30秒)
                     - "1:30.5" (1分30.5秒)
                     - "90" (90秒)
                     - "90.5" (90.5秒)
                     
        Returns:
            float: 时间（秒）
        """
        if ':' in time_str:
            # 解析 mm:ss 或 mm:ss.sss 格式
            parts = time_str.split(':')
            if len(parts) != 2:
                raise ValueError(f"无效的时间格式: {time_str}")
            
            try:
                minutes = int(parts[0])
                seconds = float(parts[1])
                return minutes * 60 + seconds
            except ValueError:
                raise ValueError(f"无效的时间格式: {time_str}")
        else:
            # 直接解析为秒数
            try:
                return float(time_str)
            except ValueError:
                raise ValueError(f"无效的时间格式: {time_str}")
    
    @staticmethod
    def format_time(seconds: float) -> str:
        """
        将秒数格式化为时间字符串
        
        Args:
            seconds: 时间（秒）
            
        Returns:
            str: 格式化的时间字符串
        """
        if seconds < 60:
            return f"{seconds:.1f}秒"
        else:
            minutes = int(seconds // 60)
            remaining_seconds = seconds % 60
            return f"{minutes}:{remaining_seconds:05.2f}"
