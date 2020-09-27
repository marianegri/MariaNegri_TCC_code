
import matplotlib.pyplot as plt
import WTdelineator as wav
import wfdb
import os
import numpy as np
import pre_processamento as filt
import Resultados as result
import statistics
import heapq


plt.close("all")

os.chdir('sample-data/')

arquivos = ['113']

porcentagem_acertos = np.zeros(len(arquivos))
sensitivity = np.zeros(len(arquivos))
positive_predictivity = np.zeros(len(arquivos))
accuracy = np.zeros(len(arquivos))

plt.rcParams.update({'font.size': 25})

fig = plt.figure()

for idx in range(len(arquivos)):
    print(idx)

    s, att = wfdb.rdsamp(arquivos[idx])
    
    sName = att['signame']
    sNum = sName.index('MLII')
    
    #%% Filtro
    fs = att['fs']
    sig = s[:,sNum]
    N = sig.size
    t = np.arange(0,N/fs,1/fs)
    
    
    ecg_filt = filt.filtro_pre_processamento(sig, fs)
    
    
    
    #%% Wavelet Transform delineation
    
    real_peaks, num_beat_true = result.numero_picos(arquivos[idx])
        
    NN = np.arange(len(t))

    res = result.segmentation(real_peaks, ecg_filt, NN)
    
    real_peaks = np.array(real_peaks)
    

    ax = fig.add_subplot(1,1,idx+1)
    ax.plot(t, ecg_filt)


    cA, cD1, cD2, cD3= wav.waveletDecomp(res) # Perform signal decomposition
    
    real_arrhyt, num_arrhyt = result.numero_arritmia(arquivos[idx])

    Detalhes = cD3
    ax.plot(t[0:len(Detalhes)]*2, Detalhes)
    
    limiar = heapq.nlargest(1000,abs(Detalhes))
    limiar = ((np.mean(limiar) + max(abs(Detalhes)))/ 2)*0.9 #+ max(abs(Detalhes)) )/ 2

    i = 0
    y_list = []
    for k in Detalhes:
        if abs(k) >= limiar:
            y_list.append(i)
        i += 1
#    plt.figure()
    ax.plot(t[y_list]*2,Detalhes[y_list], '*')
    ax.plot(t[real_arrhyt], ecg_filt[real_arrhyt]/10, '+')
#    ax.set_xlim([6.57*60, 6.59*60])
    ax.set_xlabel('Tempo (s)', labelpad=0);
    ax.set_ylabel('Amplitude (n.u.)', labelpad=0);


    
#    ax.legend(['Resultado Wavelet', 'Desordem detectada', 'Anotações physionet'], loc='lower right') #loc='lower right'
    ax.legend(['ECG', 'Resultado Wavelet', 'Desordem detectada', 'Anotações physionet'])
    
    
    y_list = [i * 2 for i in y_list]
    
    VP, FP, VN, FN = result.compara_arrit(y_list, real_arrhyt, NN)
    
    if (VP + FN) != 0:
        sensitivity[idx] = (VP/(VP + FN))*100
    if (VP + FP) != 0:
        positive_predictivity[idx] = (VP/(VP + FP))*100
    if (VP + FN + FP) != 0:
        accuracy[idx] = (VP/(VP + FN + FP))*100

print(' ')
print('sensibilidade: ', statistics.mean(sensitivity), '%') # PORCENTAGEM DE ACERTOS PELO TOTAL
print('preditivo positivo: ', statistics.mean(positive_predictivity), '%') #probabilidade de um pico avaliado e com resultado positivo ser realmente um pico
print('precisão: ', statistics.mean(accuracy), '%')
print(' ')
