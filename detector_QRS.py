#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  1 16:39:13 2020

@author: maria
"""

import wfdb
import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as sg
from scipy import interpolate
import math
import findPeaks as fp
import Resultados as result
import os
import pre_processamento as filt
import statistics
import scipy.fftpack

## Numero de linha e colunas dos subplots (depende do numero de registros)
NUM_LINHA = 4
NUM_COLUNA = 5

## derivação de ECG : MLII
## REGISTROS 102 E 104 NÃO TEM ESSA DERIVAÇÃO
## REGISTRO 114 A DERIVAÇÃO MLII ESTÁ NO SEGUNDO CANAL

plt.close("all")

## PHYSIONET

os.chdir('sample-data/')
plt.rcParams.update({'font.size': 10})

arquivos = ['100', '101', '103', '105', '106', '107', '109', '111', '112',
            '113', '114', '115', '116', '117', '118', '119', '121', '122',
            '123', '124']

#arquivos = ['113'] # APBs

paremetros = {
            'yRR': [],
            'xRR': [],
            'sensitivity': np.zeros(len(arquivos)),
            'positive_predictivity': np.zeros(len(arquivos)),
            'accuracy': np.zeros(len(arquivos)),
            'LF': float,
            'HF': float
            }
banco_de_dados = []


for i in range(len(arquivos)):
    banco_de_dados.append(paremetros.copy())

fig = plt.figure()
fig.suptitle('Curva RR', fontsize=12)
fig.subplots_adjust(left = 0.03, right = 0.995, bottom = 0.035, top=0.945, wspace = 0.2, hspace = 0.4)

fig_poincare = plt.figure()
fig_poincare.suptitle('Plot Poincaré', fontsize=12)
fig_poincare.subplots_adjust(left = 0.03, right = 0.995, bottom = 0.035, top=0.945, wspace = 0.2, hspace = 0.4)

fig_FFT = plt.figure()
fig_FFT.suptitle('FFT da curva RR', fontsize=12)
fig_FFT.subplots_adjust(left = 0.03, right = 0.995, bottom = 0.035, top=0.945, wspace = 0.2, hspace = 0.4)

fig_ruido = plt.figure()
fig_ruido.suptitle('ECG antes da remoção de artefatos', fontsize=12)
fig_ruido.subplots_adjust(left = 0.03, right = 0.995, bottom = 0.035, top=0.945, wspace = 0.2, hspace = 0.4)

fig_sem_ruido = plt.figure()
fig_sem_ruido.suptitle('ECG filtrado', fontsize=12)
fig_sem_ruido.subplots_adjust(left = 0.03, right = 0.995, bottom = 0.035, top=0.945, wspace = 0.2, hspace = 0.4)

for idx in range(len(arquivos)):
    print(idx)
            
    real_peaks, num_beat_true = result.numero_picos(arquivos[idx])
    
    s, att = wfdb.rdsamp(arquivos[idx])
    
    sName = att['signame']
    sNum = sName.index('MLII')
    fs = att['fs']
    ecg_raw = s[:,sNum]
    
    n_raw = np.linspace(0,(ecg_raw.size/fs), ecg_raw.size)
    
    ax_ruido = fig_ruido.add_subplot(NUM_LINHA,NUM_COLUNA,idx+1)
    ax_ruido.plot(n_raw, ecg_raw)
    ax_ruido.set_xlim([155, 185])
    ax_ruido.set_xlabel('tempo (s)', labelpad=0)
    ax_ruido.set_ylabel('Amplitude (V)', labelpad=0)
    ax_ruido.set_title(arquivos[idx])
    
#    plt.figure()
#    plt.plot(n_raw, ecg_raw)
    
    #%%-------------------------Remoção de Artefatos---------------------------------
    
    ecg_filt = filt.filtro_pre_processamento(ecg_raw, fs)
    
    ax_sem_ruido = fig_sem_ruido.add_subplot(NUM_LINHA,NUM_COLUNA,idx+1)
    ax_sem_ruido.plot(n_raw, ecg_filt)
    ax_sem_ruido.set_xlim([0, 50])
    ax_sem_ruido.set_xlabel('tempo (s)', labelpad=0)
    ax_sem_ruido.set_ylabel('Amplitude (V)', labelpad=0)
    
    #%%----------------------------Detecção QRS------------------------------------
     #%%----------------------------1ª ETAPA ------------------------------------
    # FILTRO #
    Fpass_low = 15    # Desired cutoff frequency, Hz
    Fstop_low = 25 #45
    numtaps_low = 337      # Size of the FIR filter.
        
    b_3 = sg.remez(numtaps_low, [0, Fpass_low, Fstop_low, fs/2], [1, 0], [1, 48.25],Hz=fs) #1.925
    
    w_3, h_3 = sg.freqz(b_3, [1], worN=2000)
    a_3 = [1]
    
    ecg_filt_tompk = sg.filtfilt(b_3, a_3,  ecg_filt)
    
    # DERIVADA # - provides QRS slope information.
    ecg_filt_tompk = ecg_filt_tompk / max(ecg_filt_tompk)
    
    derivative = np.ediff1d(ecg_filt_tompk, to_begin=0)
    
    
    # QUADRATURA # - intensifies values received in derivative.
    squaring = derivative ** 2
    
    # INTEGRAÇÃO DA JANELA MÓVEL#
    integration_window_ms = 80 #80
    integration_window = math.ceil((integration_window_ms/1000)*fs)
    integrated_ecg_measurements = sg.filtfilt(np.ones(integration_window),[1], squaring)
    
    
     #%%----------------------------2ª ETAPA------------------------------------    
    ecg_avg     = integrated_ecg_measurements
    t           = np.linspace(0,(ecg_avg.size/fs), ecg_avg.size)
    # Monta vetor de índices que indicam picos em ecg_avg
    #Vetor pega o incia do maior pico em cada janela. Janelas de 0,9 segundos
    
    #de 150 a 250 ms
    window_time = 720 #1000 #720 # in miliseconds
    window_size = math.ceil((window_time/1000)*fs)
    
#    print('tamanho da janela = ', window_size)
    
    porcent_threshold = 80/100
    
    
    avg_peaks = fp.determina_janela_busca(ecg_avg, porcent_threshold, window_size)
    
    # Identifica numero de picos.
    num_peaks = fp.num_peaks(avg_peaks)
    
#    print('numero possivel de picos  :',num_peaks)
    
    delta_T, peaks, num_beat_false, num_ectopic, num_peaks, ect_indx, ect_peaks = fp.detect_peaks(ecg_filt, avg_peaks, num_peaks, fs)
    
    peaks[0,:] = peaks[0,:]
    ect_indx = np.array(ect_indx)
    
    t_delta = peaks[0,0:num_peaks-1]    
    
    my_peaks = peaks[0,0:num_peaks]
    
    
    ax_sem_ruido.set_title(arquivos[idx])
    ax_sem_ruido.stem(peaks[0,0:num_peaks]/fs,peaks[1,0:num_peaks], basefmt='None', linefmt='None', markerfmt='.', use_line_collection = 'false')
    
    #%%----------------------------Avaliação da detecção QRS------------------------------------    
    
    NN = np.arange(len(n_raw))
    
    VP, FP, VN, FN = result.compara_picos(my_peaks, real_peaks, NN)
    
#    porcentagem_acertos[idx] = (VP/num_beat_true)*100
    
    banco_de_dados[idx]['sensitivity'] = (VP/(VP + FN))*100
    banco_de_dados[idx]['positive_predictivity'] = (VP/(VP + FP))*100
    banco_de_dados[idx]['accuracy'] = (VP/(VP + FN + FP))*100
    
    banco_de_dados[idx]['yRR'] = delta_T.copy()
    banco_de_dados[idx]['xRR'] = t_delta.copy()
    
    #%%---------------------------- Poincaré------------------------------------

    xp = banco_de_dados[idx]['yRR'].copy()
    xp = np.insert(xp, -1, 0)
    xm = banco_de_dados[idx]['yRR'].copy()
    xm = np.insert(xm, 0, 0)
    
    ax_1 = fig_poincare.add_subplot(NUM_LINHA,NUM_COLUNA,idx+1)

    ax_1.scatter(xm, xp)
    ax_1.set_xlabel('x(n)', labelpad=0)
    ax_1.set_ylabel('x(n+1)', labelpad=0)
    ax_1.set_xlim([0, 1.5])
    ax_1.set_ylim([0, 1.5])
    ax_1.set_title(arquivos[idx])

            
    ax = fig.add_subplot(NUM_LINHA,NUM_COLUNA,idx+1)
    ax.plot(banco_de_dados[idx]['xRR']/(60*fs), banco_de_dados[idx]['yRR'], '*-', c='#2ca02c')
    ax.set_title(arquivos[idx])
    ax.set_xlabel('Tempo (s)', labelpad=0)
    ax.set_ylabel('Amplitude (s)', labelpad=0)
    ax.set_ylim([0, 2])
#    plt.xlim(250, 300)
    

    #%% Interpolação para FFT
    
    banco_de_dados[idx]['xRR'] = [float(i) for i in banco_de_dados[idx]['xRR']]
    
    
    n_ream   = 20
    
    new_yRR = np.linspace(0, banco_de_dados[idx]['xRR'][-1], len(banco_de_dados[idx]['xRR'])*n_ream)
    RR_int  = interpolate.interp1d( banco_de_dados[idx]['xRR'], banco_de_dados[idx]['yRR'], kind='cubic', fill_value="extrapolate")(new_yRR)
    
    
    #%% FFT
    N = len(RR_int)
    N_FFT    = 2**(math.ceil(math.log2(math.floor(N))))
    freq_FFT = np.linspace(0, n_ream/2, N_FFT/2)
     
    Y        = (2/N)*scipy.fftpack.fft(RR_int, N_FFT)
    Mg       = np.abs(Y[0: round((N_FFT/2))]) #20*np.log10(abs(Y)) #
    Mg[0]    = Mg[0]/2
    Mg       = Mg**2
    
    ax_FFT = fig_FFT.add_subplot(NUM_LINHA,NUM_COLUNA,idx+1)
    ax_FFT.plot(freq_FFT, Mg)
    ax_FFT.set_xlim([-0.01, 0.5])
    ax_FFT.set_ylim([0, 0.005])
    ax_FFT.set_xlabel('freq (Hz)', labelpad=0)
    ax_FFT.set_ylabel('Mg', labelpad=0)
    ax_FFT.set_title(arquivos[idx])
    
    #%% High freq and Low Freq
    banco_de_dados[idx]['HF'] = 0
    for i in range(len(freq_FFT)):
        if freq_FFT[i] > 0.15:
            if freq_FFT[i] < 0.4:
                banco_de_dados[idx]['HF'] = banco_de_dados[idx]['HF'] + Mg[i]
    
    banco_de_dados[idx]['LF'] = 0
    for i in range(len(freq_FFT)):
        if freq_FFT[i] > 0.04:
            if freq_FFT[i] < 0.15:
                banco_de_dados[idx]['LF'] = banco_de_dados[idx]['LF'] + Mg[i]

#%%
print(' ')
#print('porcentagem_acertos: ', statistics.mean(porcentagem_acertos), '%')
print('sensibilidade: ', statistics.mean(result.get_struct(banco_de_dados, 'sensitivity')), '%') # PORCENTAGEM DE ACERTOS PELO TOTAL
print('preditivo positivo: ', statistics.mean(result.get_struct(banco_de_dados, 'positive_predictivity')), '%') #probabilidade de um pico avaliado e com resultado positivo ser realmente um pico
print('precisão: ', statistics.mean(result.get_struct(banco_de_dados, 'accuracy')), '%')
print(' ')

