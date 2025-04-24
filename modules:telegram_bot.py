from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext
import logging
from config import Config
from modules.stock_analyzer import StockAnalyzer
from modules.news_monitor import NewsMonitor
import schedule
import time
from threading import Thread

class TelegramBot:
    def __init__(self):
        self.updater = Updater(token=Config.TOKEN, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.stock_analyzer = StockAnalyzer()
        self.news_monitor = NewsMonitor()
        
        # Configura handlers
        self.dispatcher.add_handler(CommandHandler("start", self.start))
        self.dispatcher.add_handler(CommandHandler("acao", self.stock_analysis))
        self.dispatcher.add_handler(CommandHandler("noticias", self.news_analysis))
        self.dispatcher.add_handler(CommandHandler("monitorar", self.monitor_stock))
        
        # Inicia monitoramento periódico
        self.schedule_monitoring()
    
    def start(self, update: Update, context: CallbackContext):
        """Mensagem de boas-vindas"""
        help_text = """
        📈 *Bot de Análise de Ações Brasileiras* 📉

        *Comandos disponíveis:*
        /acao TICKER - Análise completa de uma ação (ex: /acao PETR4)
        /noticias TICKER - Análise de notícias recentes
        /monitorar TICKER - Monitora a ação e envia alertas

        Exemplos:
        /acao VALE3
        /noticias ITUB4
        /monitorar BBDC4
        """
        update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
    
    def stock_analysis(self, update: Update, context: CallbackContext):
        """Análise completa de uma ação"""
        if not context.args:
            update.message.reply_text("⚠️ Por favor, informe um ticker. Ex: /acao PETR4")
            return
        
        ticker = context.args[0].upper()
        if ticker not in Config.STOCKS:
            update.message.reply_text("⚠️ Ticker não encontrado na lista monitorada.")
            return
        
        # Obtém análise
        analysis = self.stock_analyzer.get_full_analysis(ticker)
        news_summary = self.news_monitor.get_news_summary(ticker)
        
        if not analysis:
            update.message.reply_text("⚠️ Erro ao obter dados da ação.")
            return
        
        # Formata resposta
        response = (
            f"📊 *Análise Completa - {ticker}*\n\n"
            f"💰 *Preço*: R$ {analysis['price']:.2f}\n"
            f"📈 *Variação*: {analysis.get('change', 'N/A')}\n"
            f"📉 *Média Móvel (20 dias)*: {analysis.get('sma', 'N/A'):.2f}\n"
            f"📊 *RSI (14 dias)*: {analysis.get('rsi', 'N/A'):.2f}\n\n"
        )
        
        if 'recommendation' in analysis:
            response += f"✅ *Recomendação Técnica*: {analysis['recommendation']}\n\n"
        
        if news_summary:
            response += (
                f"📰 *Análise de Notícias*\n"
                f"🔄 *Quantidade*: {news_summary['news_count']}\n"
                f"📌 *Sentimento*: {news_summary['overall_sentiment']}\n"
                f"🔍 *Últimas Notícias*:\n"
            )
            for news in news_summary['latest_news']:
                response += f"  • {news['title']} ({news['source']})\n"
        
        update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
    
    def news_analysis(self, update: Update, context: CallbackContext):
        """Análise de notícias de uma ação"""
        if not context.args:
            update.message.reply_text("⚠️ Por favor, informe um ticker. Ex: /noticias PETR4")
            return
        
        ticker = context.args[0].upper()
        news_summary = self.news_monitor.get_news_summary(ticker)
        
        if not news_summary or news_summary['news_count'] == 0:
            update.message.reply_text(f"ℹ️ Nenhuma notícia recente encontrada para {ticker}.")
            return
        
        response = (
            f"📰 *Análise de Notícias - {ticker}*\n\n"
            f"📌 *Sentimento Geral*: {news_summary['overall_sentiment']}\n"
            f"🔄 *Quantidade de Notícias*: {news_summary['news_count']}\n\n"
            f"📋 *Últimas Notícias*:\n"
        )
        
        for idx, news in enumerate(news_summary['latest_news'], 1):
            response += (
                f"\n{idx}. *{news['title']}*\n"
                f"   🏷️ *Fonte*: {news['source']}\n"
                f"   📊 *Sentimento*: {news['sentiment']}\n"
                f"   🔗 [Link]({news['url']})\n"
            )
        
        update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    
    def monitor_stock(self, update: Update, context: CallbackContext):
        """Inicia monitoramento de uma ação"""
        if not context.args:
            update.message.reply_text("⚠️ Por favor, informe um ticker. Ex: /monitorar PETR4")
            return
        
        ticker = context.args[0].upper()
        if ticker not in Config.STOCKS:
            update.message.reply_text("⚠️ Ticker não encontrado na lista monitorada.")
            return
        
        chat_id = update.message.chat_id
        self.start_monitoring(ticker, chat_id)
        update.message.reply_text(f"🔔 Monitorando {ticker}. Você receberá atualizações periódicas.")
    
    def start_monitoring(self, ticker, chat_id):
        """Agenda monitoramento periódico"""
        def job():
            analysis = self.stock_analyzer.get_full_analysis(ticker)
            news_summary = self.news_monitor.get_news_summary(ticker)
            
            if not analysis:
                return
            
            # Verifica se há mudanças significativas
            # (Implemente lógica de comparação com último estado)
            
            # Envia atualização
            response = (
                f"🔔 *Atualização - {ticker}*\n\n"
                f"💰 Preço: R$ {analysis['price']:.2f}\n"
                f"📊 Recomendação: {analysis.get('recommendation', 'N/A')}\n"
            )
            
            if news_summary and news_summary['news_count'] > 0:
                response += f"📰 Sentimento Notícias: {news_summary['overall_sentiment']}\n"
            
            self.updater.bot.send_message(chat_id=chat_id, text=response, parse_mode=ParseMode.MARKDOWN)
        
        # Agenda para rodar a cada X minutos
        schedule.every(Config.CHECK_INTERVAL).minutes.do(job)
    
    def schedule_monitoring(self):
        """Roda o agendador em thread separada"""
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(1)
        
        Thread(target=run_scheduler, daemon=True).start()
    
    def run(self):
        """Inicia o bot"""
        self.updater.start_polling()
        self.updater.idle()