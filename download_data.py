#!/usr/bin/env python3
"""
Script per scaricare dati Bitcoin per un periodo limitato
Versione modificata di grabber.py per raccogliere dati rapidamente
"""

import requests
import time
import sys

def download_bitcoin_data(filename="dataset.csv", samples=100):
    """
    Scarica dati Bitcoin per un numero limitato di campioni
    """
    print(f"Scaricando {samples} campioni di dati Bitcoin...")
    
    f = open(filename, "w")
    keys = ["price_usd","24h_volume_usd","market_cap_usd","available_supply","total_supply","percent_change_1h","percent_change_24h","percent_change_7d"]
    
    # Scrivi header (opzionale)
    header = ",".join(keys) + ",bitstamp_volume,bitstamp_vwap,blockchain_sell,blockchain_buy,blockchain_15m\n"
    f.write(header)
    
    for i in range(samples):
        try:
            print(f"Campione {i+1}/{samples}...", end=" ")
            
            # Ottieni dati da diverse API
            data = requests.get("https://api.coinmarketcap.com/v1/ticker/bitcoin/", timeout=10).json()[0]
            bstamp = requests.get("https://www.bitstamp.net/api/v2/ticker/btcusd/", timeout=10).json() 
            bkc = requests.get("https://blockchain.info/ticker", timeout=10).json()
            
            vals = []
            for key in keys:
                if key in data:
                    vals.append(str(data[key]) if data[key] is not None else "0")
                else:
                    vals.append("0")
            
            # Aggiungi dati Bitstamp
            vals.append(str(bstamp.get("volume", "0")))
            vals.append(str(bstamp.get("vwap", "0")))
            
            # Aggiungi dati Blockchain.info
            usd_data = bkc.get("USD", {})
            vals.append(str(usd_data.get("sell", "0")))
            vals.append(str(usd_data.get("buy", "0")))
            vals.append(str(usd_data.get("15m", "0")))
            
            # Scrivi la riga
            f.write(",".join(vals) + "\n")
            f.flush()
            
            print("✓")
            
            # Pausa tra le richieste per evitare rate limiting
            if i < samples - 1:  # Non aspettare dopo l'ultimo campione
                time.sleep(2)  # 2 secondi invece di 9 minuti
                
        except Exception as e:
            print(f"Errore nel campione {i+1}: {e}")
            # Scrivi una riga con valori di default in caso di errore
            default_vals = ["0"] * 12
            f.write(",".join(default_vals) + "\n")
            f.flush()
    
    f.close()
    print(f"\nDati salvati in {filename}")
    return filename

if __name__ == "__main__":
    # Scarica 50 campioni per il test
    download_bitcoin_data("dataset.csv", 50)