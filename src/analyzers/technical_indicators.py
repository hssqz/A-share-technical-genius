"""
技术指标分析模块
包含各种技术指标的分析逻辑
"""
from typing import Dict, Any
import pandas as pd
import numpy as np
from .indicators import analyze_macd

def analyze_indicators(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """
    分析技术指标数据，使用历史数据进行更全面的分析
    
    参数:
        df (pd.DataFrame): 包含技术指标数据的DataFrame
        
    返回:
        Dict[str, Dict[str, Any]]: 各个技术指标的分析结果
    """
    # 使用不同的时间窗口进行分析
    long_term = df.tail(40)    # 约2个月的交易日
    medium_term = df.tail(20)  # 约1个月的交易日
    short_term = df.tail(10)   # 约2周的交易日
    latest = df.iloc[-1]       # 最新一天
    
    analysis = {}
    
    # MACD分析
    analysis['MACD'] = analyze_macd(df, long_term, medium_term, short_term)
    
    # KDJ分析
    analysis['KDJ'] = {
        'K': latest['kdj_k'],
        'D': latest['kdj_d'],
        'J': latest['kdj_j'],
        'signal': _analyze_kdj_trend(medium_term)
    }
    
    # RSI分析
    analysis['RSI'] = {
        'RSI6': latest['rsi_6'],
        'RSI12': latest['rsi_12'],
        'RSI24': latest['rsi_24'],
        'signal': _analyze_rsi_trend(medium_term)
    }
    
    # BOLL分析
    analysis['BOLL'] = {
        'UPPER': latest['boll_upper'],
        'MID': latest['boll_mid'],
        'LOWER': latest['boll_lower'],
        'signal': _analyze_boll_trend(medium_term)
    }
    
    return analysis

def _analyze_kdj_trend(data: pd.DataFrame) -> str:
    """
    分析KDJ趋势
    
    参数:
        data (pd.DataFrame): 最近的价格数据
        
    返回:
        str: KDJ趋势分析结果
    """
    latest = data.iloc[-1]
    
    # 计算KDJ区间
    k_mean = data['kdj_k'].mean()
    k_std = data['kdj_k'].std()
    
    # 判断超买超卖
    if latest['kdj_j'] > 100:
        strength = '强烈' if latest['kdj_j'] > 110 else '一般'
        return f'{strength}超买'
    elif latest['kdj_j'] < 0:
        strength = '强烈' if latest['kdj_j'] < -10 else '一般'
        return f'{strength}超卖'
    elif latest['kdj_k'] > k_mean + k_std:
        return '偏多'
    elif latest['kdj_k'] < k_mean - k_std:
        return '偏空'
    else:
        return '盘整'

def _analyze_rsi_trend(data: pd.DataFrame) -> str:
    """
    分析RSI趋势
    
    参数:
        data (pd.DataFrame): 最近的价格数据
        
    返回:
        str: RSI趋势分析结果
    """
    latest = data.iloc[-1]
    
    # 分析RSI趋势
    rsi6_trend = data['rsi_6'].tail(5)
    trend = '上升' if rsi6_trend.is_monotonic_increasing else '下降' if rsi6_trend.is_monotonic_decreasing else '震荡'
    
    # 判断超买超卖
    if latest['rsi_6'] > 80:
        return f'超买（{trend}趋势）'
    elif latest['rsi_6'] < 20:
        return f'超卖（{trend}趋势）'
    elif latest['rsi_6'] > 60:
        return f'偏强（{trend}趋势）'
    elif latest['rsi_6'] < 40:
        return f'偏弱（{trend}趋势）'
    else:
        return f'盘整（{trend}趋势）'

def _analyze_boll_trend(data: pd.DataFrame) -> str:
    """
    分析布林带趋势
    
    参数:
        data (pd.DataFrame): 最近的价格数据
        
    返回:
        str: 布林带趋势分析结果
    """
    latest = data.iloc[-1]
    recent = data.tail(5)  # 最近5天数据
    
    # 计算布林带宽度趋势
    band_widths = (recent['boll_upper'] - recent['boll_lower']) / recent['boll_mid'] * 100
    bandwidth_trend = '扩大' if band_widths.is_monotonic_increasing else '收窄' if band_widths.is_monotonic_decreasing else '平稳'
    
    # 分析价格位置
    if latest['close'] > latest['boll_upper']:
        return f'突破上轨（带宽{bandwidth_trend}）'
    elif latest['close'] < latest['boll_lower']:
        return f'突破下轨（带宽{bandwidth_trend}）'
    elif latest['close'] > latest['boll_mid']:
        return f'运行于上轨区间（带宽{bandwidth_trend}）'
    else:
        return f'运行于下轨区间（带宽{bandwidth_trend}）' 