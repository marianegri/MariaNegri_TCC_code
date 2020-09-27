#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  1 16:40:36 2020

@author: maria
"""

import math
import numpy as np

## avg_peaks:janela de busca
       
def determina_janela_busca(data, threshold_, window_size ):
    threshold_ = 1 - threshold_
    
    total_i     = math.ceil(len(data)/window_size)
    
    max_idx     = np.zeros(int(total_i)+1)
    
    for i in range(math.ceil(total_i)):
        for j in range(window_size):
            max_idx[i] = i*window_size + (data[i*window_size:(i+1)*window_size]).argmax()
    
    # Define thresholds para cada 10 picos e cria vetor onde se encontram os segmentos de pico
    avg_peaks = np.zeros(data.size)
    i = 0
    k = 0
    
    #Procurar 35 vezes os 10 picos
    while i <= (len(max_idx)/10-1):
        threshold = 0
        j = 0
        #Fazer a soma dos 10 picos
        while j < 10:
            idx = int(max_idx[int(10*i+j)])
            threshold = threshold + data[idx] 
            j += 1
        #Encontrar  o threshold para aqueles 10 picos
        threshold = threshold_*(threshold/10)
        while k < idx:
            value = data[k] - threshold
            #Colocar em um novo vetor os valores possíveisde pico (acima do threshold)
            if value > 0:
                avg_peaks[k] = 1            
            k += 1
        i += 1
    while k<len(data):
        value = data[k] - threshold
        #Colocar em um novo vetor os valores possíveisde pico (acima do threshold)
        if value > 0:
            avg_peaks[k] = 1            
        k += 1

    return avg_peaks

def num_peaks(avg_peaks):
    # Identifica numero de picos.
    i = 0
    num_peaks = 0
    flag = 0
    while i < avg_peaks.size:
        if avg_peaks[i] == 1:
            if flag == 0:
                num_peaks += 1
            flag = 1
        else:
            flag = 0
        i += 1
    return num_peaks

def detect_peaks(data, avg_peaks, num_peaks, fs):
    # Cria matriz com um vetor para os indices de ocorrencia dos picos, e outro para suas amplitudes correspondentes.
    peaks = np.zeros(2*num_peaks).reshape(2,num_peaks)
    
    # Cria vetor para variabilidade do período cardíaco.
    delta_T = []
    
    # Detecta picos e preenche vetores de indices e valores de amplitude na matriz peaks.
    
    i = 0
    n = 0
    flag = 0
    peak_idx = 0
    max_value = 0
    delta_i = 0
#    delta_prv = 0
    num_beat_false = 0
    num_ectopic = 0
    ect_peaks = []
    ect_indx = []
#    flag_200ms = 1
    
    for i in range(len(avg_peaks)):
   
        # Se avg_peaks[i] tiver valor zero, significa que está fora da janela de busca
        if avg_peaks[i] == 0:
            if flag:
                delta_i = abs(abs(peak_idx) - abs(peaks[0,n-1]))
#                delta_prv = abs(abs(peaks[0,n-1]) - abs(peaks[0,n-2]))
    
            # Um novo pico não pode ser detectado até que pelo menos 200ms tenham decorrido. 
            # Se ocorrer uma detecção positiva dentro nesse período o algoritmo assume que a batida atual deve ser falsa.
            if flag:
                if delta_i < 0.2*fs:
                    num_beat_false += 1
                    flag = 0
                    
            
            # Se a flag estiver setada, significa que acabou de realizar uma busca
            if flag:
                
                
                # Armazena os valores encontrados nos vetores correspondentes
                peaks[0,n] = peak_idx # Índice correspondente ao último pico encontrado
                peaks[1,n] = max_value # Amplitude do último pico encontrado
                
                
                # Armazena variação do período cardíaco em delta_T
                delta_T.append(delta_i/fs)
                
    
                n += 1
                
                flag = 0
                max_value = 0
                #peak_idx = 0
        
        # Quando avg_peaks[i] possui valor maior que zero, inicia uma busca
        else:
            # Compara os valores de amplitude e encontra o máximo local
            if (data[i] >= max_value):
                peak_idx = i
                max_value = data[i]
            flag = 1
#            print(flag)
    num = 0        
   
    for index in range(len(peaks[0])):
        if peaks[0,index] == 0:
            if peaks[1,index] == 0:
                num += 1
#    print('num : ',num)
#    print(peaks[1])
    peaks_new = np.zeros(2*(len(peaks[0]) - num)).reshape(2,len(peaks[0]) - num)
    peaks_new[0] = peaks[0, 0:len(peaks[0]) - num]
    peaks_new[1] = peaks[1, 0:len(peaks[0]) - num]
    
#    print(len(delta_T))
#    print(len(peaks[1]))
#    print(len(peaks_new[1]))
    
    delta_T = np.delete(delta_T, 0) #deleta primeiro intervalo por causa que é do 0 ao primeiro pico
    
    num_peaks = len(peaks[0]) - num
    return (delta_T, peaks_new, num_beat_false, num_ectopic, num_peaks, ect_indx, ect_peaks)