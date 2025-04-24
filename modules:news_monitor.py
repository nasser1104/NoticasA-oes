from newsapi import NewsApiClient
from bs4 import BeautifulSoup
import requests
import re
from textblob import TextBlob
from config import Config
import pandas as pd
from datetime import datetime, timedelta

class NewsMonitor:
    def __init__(self):
        self.newsapi = NewsApiClient(api_key=Config.NEWSAPI_KEY)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_news_from_api(self, ticker):
        """Obtém notícias da NewsAPI"""
        try:
            # Busca notícias dos últimos 2 dias
            from_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
            
            # Primeiro busca em português
            news_pt = self.newsapi.get_everything(
                q=ticker,
                language='pt',
                from_param=from_date,
                sort_by='relevancy'
            )
            
            # Depois em inglês (para ações com ticker internacional)
            news_en = self.newsapi.get_everything(
                q=ticker,
                language='en',
                from_param=from_date,
                sort_by='relevancy'
            )
            
            return news_pt['articles'] + news_en['articles']
        except Exception as e:
            print(f"Erro ao buscar notícias da API: {e}")
            return []
    
    def scrape_news(self, ticker, source):
        """Scraping direto para sites específicos"""
        try:
            if source == "infomoney":
                return self._scrape_infomoney(ticker)
            elif source == "valor":
                return self._scrape_valor(ticker)
            # Adicione outros métodos para cada fonte
            else:
                return []
        except Exception as e:
            print(f"Erro no scraping {source}: {e}")
            return []
    
    def _scrape_infomoney(self, ticker):
        """Scraping específico para InfoMoney"""
        url = f"https://www.infomoney.com.br/?s={ticker}"
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            articles = soup.find_all('article', limit=5)
            news = []
            
            for art in articles:
                title = art.find('h3').get_text(strip=True)
                link = art.find('a')['href']
                time_tag = art.find('time')
                
                news.append({
                    'title': title,
                    'url': link,
                    'source': 'InfoMoney',
                    'publishedAt': time_tag['datetime'] if time_tag else None,
                    'content': None
                })
            
            return news
        except Exception as e:
            print(f"Erro no scraping do InfoMoney: {e}")
            return []
    
    def _scrape_valor(self, ticker):
        """Scraping específico para Valor Econômico"""
        url = f"https://valor.globo.com/busca/?q={ticker}"
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            articles = soup.select('.widget--info__title', limit=5)
            news = []
            
            for art in articles:
                title = art.get_text(strip=True)
                link = art['href']
                
                news.append({
                    'title': title,
                    'url': link,
                    'source': 'Valor Econômico',
                    'publishedAt': None,
                    'content': None
                })
            
            return news
        except Exception as e:
            print(f"Erro no scraping do Valor: {e}")
            return []
    
    def analyze_sentiment(self, text):
        """Análise de sentimento com TextBlob"""
        analysis = TextBlob(text)
        polarity = analysis.sentiment.polarity
        
        if polarity > 0.1:
            return {'sentiment': 'POSITIVO', 'score': polarity}
        elif polarity < -0.1:
            return {'sentiment': 'NEGATIVO', 'score': polarity}
        else:
            return {'sentiment': 'NEUTRO', 'score': polarity}
    
    def get_all_news(self, ticker):
        """Combina notícias de todas as fontes"""
        news = []
        
        # Primeiro da NewsAPI
        news.extend(self.get_news_from_api(ticker))
        
        # Depois scraping dos sites
        for source in Config.NEWS_SOURCES:
            news.extend(self.scrape_news(ticker, source))
        
        # Remove duplicatas
        seen = set()
        unique_news = []
        for item in news:
            identifier = (item['title'], item['source'])
            if identifier not in seen:
                seen.add(identifier)
                unique_news.append(item)
        
        # Analisa sentimento para cada notícia
        for item in unique_news:
            sentiment = self.analyze_sentiment(item['title'])
            item.update(sentiment)
        
        return unique_news
    
    def get_news_summary(self, ticker):
        """Resumo do sentimento das notícias"""
        news = self.get_all_news(ticker)
        if not news:
            return None
        
        # Calcula média de sentimentos
        scores = [n['score'] for n in news]
        avg_score = sum(scores) / len(scores)
        
        # Classifica geral
        if avg_score > 0.2:
            overall = "MUITO POSITIVO"
        elif avg_score > 0.1:
            overall = "POSITIVO"
        elif avg_score < -0.2:
            overall = "MUITO NEGATIVO"
        elif avg_score < -0.1:
            overall = "NEGATIVO"
        else:
            overall = "NEUTRO"
        
        return {
            'ticker': ticker,
            'news_count': len(news),
            'average_score': avg_score,
            'overall_sentiment': overall,
            'latest_news': news[:3]  # 3 notícias mais recentes
        }