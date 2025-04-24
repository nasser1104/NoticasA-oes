import yfinance as yf
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
import pandas as pd
from config import Config

class StockAnalyzer:
    def __init__(self):
        self.ts = TimeSeries(key=Config.ALPHA_VANTAGE_KEY, output_format='pandas')
        self.ti = TechIndicators(key=Config.ALPHA_VANTAGE_KEY, output_format='pandas')
    
    def format_ticker(self, ticker):
        return f"{ticker}.SA" if not ticker.endswith(".SA") else ticker
    
    def get_current_data(self, ticker):
        """Obtém dados atualizados de preço e volume"""
        try:
            yf_ticker = self.format_ticker(ticker)
            stock = yf.Ticker(yf_ticker)
            data = stock.history(period="1d")
            
            if data.empty:
                return None
                
            return {
                'ticker': ticker,
                'price': data['Close'].iloc[-1],
                'open': data['Open'].iloc[-1],
                'high': data['High'].iloc[-1],
                'low': data['Low'].iloc[-1],
                'volume': data['Volume'].iloc[-1],
                'currency': 'BRL'
            }
        except Exception as e:
            print(f"Erro ao obter dados do Yahoo Finance: {e}")
            return None
    
    def get_technical_analysis(self, ticker):
        """Obtém análise técnica com Alpha Vantage"""
        try:
            yf_ticker = self.format_ticker(ticker)
            
            # SMA (20 dias)
            sma, _ = self.ti.get_sma(symbol=yf_ticker, interval='daily', time_period=20)
            # RSI (14 dias)
            rsi, _ = self.ti.get_rsi(symbol=yf_ticker, interval='daily', time_period=14)
            # MACD
            macd, _ = self.ti.get_macd(symbol=yf_ticker, interval='daily')
            
            return {
                'sma': sma.iloc[-1]['SMA'],
                'rsi': rsi.iloc[-1]['RSI'],
                'macd': macd.iloc[-1]['MACD'],
                'signal': macd.iloc[-1]['MACD_Signal']
            }
        except Exception as e:
            print(f"Erro na análise técnica: {e}")
            return None
    
    def get_full_analysis(self, ticker):
        """Combina dados fundamentais e análise técnica"""
        current = self.get_current_data(ticker)
        if not current:
            return None
            
        technical = self.get_technical_analysis(ticker)
        
        analysis = current.copy()
        if technical:
            analysis.update(technical)
            
            # Gera recomendação simples
            analysis['recommendation'] = self.generate_recommendation(
                current['price'],
                technical['sma'],
                technical['rsi']
            )
        
        return analysis
    
    def generate_recommendation(self, price, sma, rsi):
        """Lógica simples de recomendação"""
        if price > sma and rsi < 70:
            return "COMPRAR"
        elif price < sma and rsi > 30:
            return "VENDER"
        else:
            return "NEUTRO"