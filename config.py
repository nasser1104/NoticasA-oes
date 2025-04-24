class Config:
    # Telegram
    TOKEN = "7777625610:AAGZtOr9oLXIzbb2BnckEoFdsX8uzmAkDYI"
    
    # APIs
    ALPHA_VANTAGE_KEY = "0N8SMPFT7JVEXVH9"
    NEWSAPI_KEY = "18f24b29908f4bf3924bae6aee647e7b"
    
    # Lista de ações brasileiras
    STOCKS = [
        "PETR4", "VALE3", "ITUB4", "BBDC4", "BBAS3", "B3SA3", "ABEV3", "WEGE3",
        "SUZB3", "RENT3", "PETR3", "BPAC11", "ELET3", "ELET6", "GGBR4", "HAPV3",
        "ITSA4", "JBSS3", "LREN3", "MGLU3", "NTCO3", "PCAR3", "QUAL3", "RADL3",
        "RAIL3", "SANB11", "TAEE11", "VBBR3", "VIIA3", "VIVT3", "AZUL4", "CCRO3",
        "CMIG4", "CSAN3", "CYRE3", "ECOR3", "EGIE3", "EMBR3", "ENBR3", "EQTL3",
        "FLRY3", "GNDI3", "GOAU4", "HYPE3", "IRBR3", "KLBN11", "LAME4", "MRFG3",
        "MRVE3", "MULT3"
    ]
    
    # Sites para scraping (prioritários)
    NEWS_SOURCES = [
        "infomoney",
        "valor",
        "investing",
        "sunoresearch",
        "moneytimes",
        "economias",
        "investnews",
        "dinheirorural"
    ]
    
    # Intervalo de verificação (minutos)
    CHECK_INTERVAL = 15