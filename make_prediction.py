#!/usr/bin/env python3
"""
Script per fare una previsione del prezzo Bitcoin
"""

import util
import numpy as np
import os
from keras.models import Sequential
from keras.layers import Dense, Dropout, GRU, Reshape
from keras.layers.normalization import BatchNormalization

def buildNet(w_init="glorot_uniform", act="tanh"):
    net = Sequential()
    net.add(Dense(12, kernel_initializer=w_init, input_dim=12, activation='linear'))
    net.add(Reshape((1, 12)))
    net.add(BatchNormalization())
    net.add(GRU(40, kernel_initializer=w_init, activation=act, return_sequences=True))
    net.add(Dropout(0.4))
    net.add(GRU(70, kernel_initializer=w_init, activation=act, return_sequences=True))
    net.add(Dropout(0.3))
    net.add(GRU(70, kernel_initializer=w_init, activation=act, return_sequences=True))
    net.add(Dropout(0.4))
    net.add(GRU(40, kernel_initializer=w_init, activation=act, return_sequences=False))
    net.add(Dropout(0.4))
    net.add(Dense(1, kernel_initializer=w_init, activation='linear'))
    net.compile(optimizer='nadam', loss='mse')
    return net

def make_prediction():
    # Verifica se esistono i file necessari
    if not os.path.exists('model.h5'):
        print("Modello non trovato! Esegui prima quick_train.py")
        return
    
    if not os.path.exists('dataset.csv'):
        print("Dataset non trovato! Esegui prima download_data.py")
        return
    
    # Carica il modello
    net = buildNet()
    net.load_weights('model.h5')
    print("Modello caricato!")
    
    # Carica i dati per la normalizzazione
    print("Caricamento dati per normalizzazione...", end="")
    with open('dataset.csv', 'r') as d:
        lines = d.readlines()[1:]  # Salta l'header
        data_content = "\n".join(lines)
    
    class StringFile:
        def __init__(self, content):
            self.content = content
        def read(self):
            return self.content
    
    data, labels = util.loadData(StringFile(data_content))
    data = util.reduceMatRows(data)
    labels, m1, m2 = util.reduceVector(labels, getVal=True)
    print("fatto!")
    
    try:
        # Ottieni dati attuali
        print("Ottenendo dati Bitcoin attuali...")
        actual, latest_price = util.getCurrentData(label=True)
        actual = np.array(util.reduceCurrent(actual)).reshape(1, 12)
        
        # Fai la previsione
        print("Facendo previsione...")
        pred_normalized = net.predict(actual, verbose=0)[0]
        pred = util.augmentValue(pred_normalized, m1, m2)
        pred_price = float(int(pred[0] * 100) / 100)
        
        # Mostra risultati
        print("\n" + "="*50)
        print("PREVISIONE BITCOIN")
        print("="*50)
        print(f"Prezzo attuale: ${latest_price:.2f}")
        print(f"Previsione (prossimi 9 minuti): ${pred_price:.2f}")
        
        change = pred_price - latest_price
        change_pct = (change / latest_price) * 100
        
        if change > 0:
            print(f"Variazione prevista: +${change:.2f} (+{change_pct:.2f}%) 📈")
        else:
            print(f"Variazione prevista: ${change:.2f} ({change_pct:.2f}%) 📉")
        
        print("="*50)
        
        # Ottieni dati aggiuntivi
        try:
            cex_data = util.getCEXData()
            print(f"CEX.io Ask: ${float(cex_data['ask']):.2f}")
            print(f"CEX.io Bid: ${float(cex_data['bid']):.2f}")
        except:
            print("Dati CEX.io non disponibili")
        
        return pred_price, latest_price
        
    except Exception as e:
        print(f"Errore durante la previsione: {e}")
        print("Verifica la connessione internet e riprova.")
        return None, None

if __name__ == "__main__":
    make_prediction()