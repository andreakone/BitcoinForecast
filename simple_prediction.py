#!/usr/bin/env python3
"""
Previsione Bitcoin semplificata usando solo librerie standard Python
"""

import json
import urllib.request
import urllib.error
import time
import random
import math

def get_bitcoin_price():
    """
    Ottiene il prezzo attuale di Bitcoin usando API pubbliche
    """
    apis = [
        "https://api.coindesk.com/v1/bpi/currentprice.json",
        "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    ]
    
    for api_url in apis:
        try:
            print(f"Tentativo di connessione a {api_url.split('/')[2]}...")
            
            with urllib.request.urlopen(api_url, timeout=10) as response:
                data = json.loads(response.read().decode())
                
            if "coindesk" in api_url:
                price_str = data['bpi']['USD']['rate'].replace(',', '').replace('$', '')
                price = float(price_str)
                return price, "CoinDesk"
            elif "coingecko" in api_url:
                price = float(data['bitcoin']['usd'])
                return price, "CoinGecko"
                
        except Exception as e:
            print(f"Errore con {api_url.split('/')[2]}: {e}")
            continue
    
    return None, None

def simple_trend_analysis(current_price):
    """
    Analisi di trend semplificata basata su pattern matematici
    """
    # Simula un'analisi tecnica basica usando funzioni matematiche
    time_factor = time.time() % 3600  # Usa l'ora corrente come fattore
    
    # Calcola diversi indicatori simulati
    rsi_sim = 50 + 30 * math.sin(time_factor / 600)  # RSI simulato
    ma_trend = math.cos(time_factor / 1800) * 0.02   # Media mobile simulata
    volatility = abs(math.sin(time_factor / 300)) * 0.01  # Volatilità simulata
    
    return rsi_sim, ma_trend, volatility

def make_prediction(current_price):
    """
    Genera una previsione basata su analisi tecnica semplificata
    """
    rsi, trend, volatility = simple_trend_analysis(current_price)
    
    # Logica di previsione semplificata
    base_change = trend * current_price
    
    # Fattore RSI (se RSI > 70 = ipercomprato, se RSI < 30 = ipervenduto)
    if rsi > 70:
        rsi_factor = -0.005  # Tendenza al ribasso
    elif rsi < 30:
        rsi_factor = 0.005   # Tendenza al rialzo
    else:
        rsi_factor = 0       # Neutrale
    
    # Aggiungi volatilità
    volatility_factor = random.uniform(-volatility, volatility) * current_price
    
    # Calcola previsione finale
    predicted_change = base_change + (rsi_factor * current_price) + volatility_factor
    predicted_price = current_price + predicted_change
    
    return predicted_price, rsi, trend, volatility

def format_prediction_report(current_price, predicted_price, source, rsi, trend, volatility):
    """
    Formatta il report della previsione
    """
    change = predicted_price - current_price
    change_pct = (change / current_price) * 100
    
    print("\n" + "="*60)
    print("🪙 PREVISIONE BITCOIN - ANALISI TECNICA SEMPLIFICATA")
    print("="*60)
    print(f"📊 Fonte dati: {source}")
    print(f"💰 Prezzo attuale: ${current_price:,.2f}")
    print(f"🔮 Previsione (9 min): ${predicted_price:,.2f}")
    print("-"*60)
    
    if change > 0:
        print(f"📈 Variazione prevista: +${change:.2f} (+{change_pct:.2f}%)")
        trend_emoji = "🚀"
    else:
        print(f"📉 Variazione prevista: ${change:.2f} ({change_pct:.2f}%)")
        trend_emoji = "📉"
    
    print("-"*60)
    print("🔍 INDICATORI TECNICI:")
    print(f"   RSI Simulato: {rsi:.1f} {'(Ipercomprato)' if rsi > 70 else '(Ipervenduto)' if rsi < 30 else '(Neutrale)'}")
    print(f"   Trend: {trend:.4f} {'(Rialzista)' if trend > 0 else '(Ribassista)' if trend < 0 else '(Laterale)'}")
    print(f"   Volatilità: {volatility:.4f}")
    
    print("-"*60)
    print(f"🎯 OUTLOOK: {trend_emoji}")
    
    if abs(change_pct) < 0.5:
        outlook = "Movimento laterale previsto"
    elif change_pct > 2:
        outlook = "Forte movimento rialzista previsto"
    elif change_pct < -2:
        outlook = "Forte movimento ribassista previsto"
    elif change_pct > 0:
        outlook = "Leggero movimento rialzista previsto"
    else:
        outlook = "Leggero movimento ribassista previsto"
    
    print(f"   {outlook}")
    print("="*60)
    
    # Disclaimer
    print("⚠️  DISCLAIMER:")
    print("   Questa è una previsione semplificata a scopo educativo.")
    print("   Non utilizzare per decisioni di investimento reali.")
    print("   I mercati crypto sono estremamente volatili e imprevedibili.")
    print("="*60)

def main():
    """
    Funzione principale
    """
    print("🔄 Avvio sistema di previsione Bitcoin...")
    
    # Ottieni prezzo attuale
    current_price, source = get_bitcoin_price()
    
    if current_price is None:
        print("❌ Impossibile ottenere il prezzo di Bitcoin.")
        print("   Verifica la connessione internet e riprova.")
        return
    
    print(f"✅ Prezzo ottenuto: ${current_price:,.2f}")
    
    # Genera previsione
    print("🧮 Elaborazione analisi tecnica...")
    predicted_price, rsi, trend, volatility = make_prediction(current_price)
    
    # Mostra risultati
    format_prediction_report(current_price, predicted_price, source, rsi, trend, volatility)
    
    # Salva risultati
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open("predictions.log", "a") as f:
        f.write(f"{timestamp},{current_price:.2f},{predicted_price:.2f},{predicted_price-current_price:.2f}\n")
    
    print(f"\n📝 Previsione salvata in predictions.log")

if __name__ == "__main__":
    main()