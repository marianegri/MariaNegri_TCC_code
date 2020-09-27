#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 22:30:54 2020

@author: maria
"""

import numpy as np
import wfdb

def numero_picos(record):
    annsamp, anntype, subtype, chan, num, aux, annfs = wfdb.rdann(record, 'atr')


    count = 0
    
    sampann = []
    
    for i in range(len(anntype)):
#        if anntype[i] == 'V':
#            count = count + 1
#        elif anntype[i] == 'r':
#            count = count + 1
        if anntype[i] == '+':
            count = count + 1        
        elif anntype[i] == '~':
            count = count + 1
        elif anntype[i] == '|':
            count = count + 1
        elif anntype[i] == '!':
            count = count + 1
        elif anntype[i] == '[':
            count = count + 1
        elif anntype[i] == ']':
            count = count + 1
        elif anntype[i] == 'x':
            count = count + 1
        elif anntype[i] == 'U':
            count = count + 1
        elif anntype[i] == '(':
            count = count + 1
        else:
            sampann.append(annsamp[i]) 
            
    num_beat_true = len(anntype) - count
    return sampann, num_beat_true;

def numero_arritmia(record):
    annsamp, anntype, subtype, chan, num, aux, annfs = wfdb.rdann(record, 'atr')


    count = 0
    
    teste = []
    
    for i in range(len(anntype)):
        if anntype[i] == 'A':
#            print("A")
            count = count + 1 
            teste.append(annsamp[i])
        elif anntype[i] == 'a':
#            print("a")
            count = count + 1
            teste.append(annsamp[i])
        elif anntype[i] == 'V': # J? R?
#            print("V")
            count = count + 1
            teste.append(annsamp[i])
#    print(anntype)


    return teste, count;

def segmentation(real_peaks, ecg_filt, t):
    tam_sig = len(t) 
    window = 120 #60 amostras pra cada lado
    
    result = np.zeros(tam_sig)
    
    l = 0
    for k in range(tam_sig):
        if round(t[k],3) == round(real_peaks[l],3):
            result[k] = ecg_filt[k]
            for w in range(int(window/2)):
                if (k + w) < tam_sig:
                    result[k + w] = ecg_filt[k+ w]
                if (k - w) > 0:
                    result[k - w] = ecg_filt[k- w]
                        
            l = l + 1
            if l == len(real_peaks)-1:
                break;
    return result;

def compara_arrit(my_peaks, real_peaks, t):
    tam_sig = len(t) 
    fs = 360
    window = 0.4*fs #tamanho média de um complexo QRS
    
#    my_peaks = np.concatenate((my_peaks, np.zeros(30)), axis=0)
#    real_peaks = np.concatenate((real_peaks, np.zeros(30)), axis=0)
    


    deteccao = np.zeros(tam_sig)
    gabarito = np.zeros(tam_sig)
    l = 0
    for k in range(tam_sig):
        if round(t[k],3) == round(my_peaks[l],3):
            deteccao[k] = 1
            l = l + 1
            if l == len(my_peaks):
                break;

 
    l = 0
    
    if len(real_peaks) > 0:
        for k in range(tam_sig):
            if round(t[k],3) == round(real_peaks[l],3):
                gabarito[k] = 1
                for w in range(int(window/2)):
                    if (k + w) < tam_sig:
                        gabarito[k + w] = 1
                    if (k - w) > 0:
                        gabarito[k - w] = 1
                            
                l = l + 1
                if l == len(real_peaks):
                    break;

#    plt.figure()
#    plt.plot(gabarito,'*')
#    plt.plot(deteccao,'o')
    
    VP = 0 # verdadeiro positivo
    FP = 0 # falso positivo
    VN = 0 # verdadeiro negativo
    FN = 0 # falso negativo
    
    VP_t = 0
    
    flag = 0

    for i in range(len(gabarito)):
        
        if( gabarito[i] == 1 ):
            flag = 1
            if( deteccao[i] == gabarito[i] ):
                VP = VP + 1
                VP_t = 1
            else:
                VN = VN + 1
        elif( gabarito[i] == 0 ):
            if flag == 1:
                if VP_t != 1:
                    FN = FN + 1
                flag = 0
                VP_t = 0

            if( deteccao[i] == gabarito[i] ):
                VN = VN + 1
            else:
                FP = FP + 1
            
                
    
#    print('Verdadeiro positiso: ',VP)
#    print('Falso      positiso: ',FP)
#    print('Verdadeiro negativo: ',VN - FN)
#    print('Falso      negativo: ',FN)
#    print(' ')
#    print('Nº Total  de  picos: ',VP + FN)
    
    
    VN = VN - FN
    return VP, FP, VN, FN;
                
def compara_picos(my_peaks, real_peaks, t):
    tam_sig = len(t) 
    fs = 360
    window = 0.1*fs
    
#    my_peaks = np.concatenate((my_peaks, np.zeros(30)), axis=0)
#    real_peaks = np.concatenate((real_peaks, np.zeros(30)), axis=0)
    


    deteccao = np.zeros(tam_sig)
    gabarito = np.zeros(tam_sig)
    l = 0
    for k in range(tam_sig):
        if round(t[k],3) == round(my_peaks[l],3):
            deteccao[k] = 1
            l = l + 1
            if l == len(my_peaks):
                break;

 
    l = 0
    for k in range(tam_sig):
        if round(t[k],3) == round(real_peaks[l],3):
            gabarito[k] = 1
            for w in range(int(window/2)):
                if (k + w) < tam_sig:
                    gabarito[k + w] = 1
                if (k - w) > 0:
                    gabarito[k - w] = 1
                        
            l = l + 1
            if l == len(real_peaks):
                break;

#    plt.figure()
#    plt.plot(gabarito,'*')
#    plt.plot(deteccao,'o')
    
    VP = 0 # verdadeiro positivo
    FP = 0 # falso positivo
    VN = 0 # verdadeiro negativo
    FN = 0 # falso negativo
    
    VP_t = 0
    
    flag = 0

    for i in range(len(gabarito)):
        
        if( gabarito[i] == 1 ):
            flag = 1
            if( deteccao[i] == gabarito[i] ):
                VP = VP + 1
                VP_t = 1
            else:
                VN = VN + 1
        elif( gabarito[i] == 0 ):
            if flag == 1:
                if VP_t != 1:
                    FN = FN + 1
                flag = 0
                VP_t = 0

            if( deteccao[i] == gabarito[i] ):
                VN = VN + 1
            else:
                FP = FP + 1
            
                
    
#    print('Verdadeiro positiso: ',VP)
#    print('Falso      positiso: ',FP)
#    print('Verdadeiro negativo: ',VN - FN)
#    print('Falso      negativo: ',FN)
#    print(' ')
#    print('Nº Total  de  picos: ',VP + FN)
    
    
    VN = VN - FN
    return VP, FP, VN, FN; 

def get_struct(struct, name):
    vetor = []
    for i in struct:
        vetor.append(i[name])
    return vetor;