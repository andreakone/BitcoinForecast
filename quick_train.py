#!/usr/bin/env python3
"""
Script per training rapido del modello Bitcoin
"""

import util
import numpy as np
import matplotlib.pyplot as plt
from keras.models import Sequential
from keras.layers import Dense, Dropout, GRU, Reshape
from keras.layers.normalization import BatchNormalization
import os

def buildNet(w_init="glorot_uniform", act="tanh"):
    print("Costruendo la rete neurale...", end="")
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
    print("fatto!")
    return net

def train_model():
    # Verifica se esiste il dataset
    if not os.path.exists('dataset.csv'):
        print("Dataset non trovato! Esegui prima download_data.py")
        return
    
    # Costruisci la rete
    net = buildNet()
    
    # Carica i dati
    print("Caricamento dati...", end="")
    with open('dataset.csv', 'r') as d:
        lines = d.readlines()[1:]  # Salta l'header
        if len(lines) < 10:
            print(f"\nDati insufficienti! Trovate solo {len(lines)} righe.")
            return
        
        # Ricostruisci il formato atteso da util.loadData
        data_content = "\n".join(lines)
        
    # Simula un file object per util.loadData
    class StringFile:
        def __init__(self, content):
            self.content = content
        def read(self):
            return self.content
    
    data, labels = util.loadData(StringFile(data_content))
    
    if len(data) < 5:
        print(f"Dati insufficienti per il training! Trovati {len(data)} campioni.")
        return
        
    data = util.reduceMatRows(data)
    labels, m1, m2 = util.reduceVector(labels, getVal=True)
    print(f"{len(labels)} campioni caricati!")
    
    # Training con poche epoche per test rapido
    epochs = 5
    print(f"Training per {epochs} epoche...")
    
    # Usa tutti i dati tranne gli ultimi 2 per il test
    el = max(1, len(data) - 2)
    
    try:
        net.fit(np.array(data[:el]), np.array(labels[:el]), 
                epochs=epochs, batch_size=min(10, len(data[:el])), verbose=1)
        
        print("Training completato!\nSalvataggio modello...", end="")
        net.save_weights("model.h5")
        print("salvato!")
        
        # Test del modello
        print("\nTest del modello:")
        reals, preds = [], []
        
        test_start = max(0, len(data) - 10)
        for i in range(test_start, len(data)):
            x = np.array(data[i]).reshape(1, 12)
            predicted = util.augmentValue(net.predict(x, verbose=0)[0], m1, m2)[0]
            real = util.augmentValue(labels[i], m1, m2)
            preds.append(predicted)
            reals.append(real)
            print(f"Reale: ${real:.2f}, Predetto: ${predicted:.2f}")
        
        # Crea grafico
        plt.figure(figsize=(10, 6))
        plt.plot(reals, color='g', label='Valori Reali', marker='o')
        plt.plot(preds, color='r', label='Valori Predetti', marker='s')
        plt.ylabel('BTC/USD')
        plt.xlabel('Campioni di Test')
        plt.title('Previsione Bitcoin - Test del Modello')
        plt.legend()
        plt.grid(True)
        plt.savefig("training_results.png", dpi=150, bbox_inches='tight')
        print(f"\nGrafico salvato come training_results.png")
        
        return net, m1, m2
        
    except Exception as e:
        print(f"Errore durante il training: {e}")
        return None, None, None

if __name__ == "__main__":
    train_model()