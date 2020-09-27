#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 11:01:21 2020

@author: maria
"""

import scipy.signal as sg

def filtro_pre_processamento(ecg_raw, fs):
    # High-pass filter design parameters
    Fpass = 5 #1.28    # Desired cutoff frequency, Hz
    Fstop = 0.001 #0.00128
    numtaps = 250 #251      # Size of the FIR filter.
    a = [1]
    
    b = sg.remez(numtaps, [0, Fstop, Fpass, fs/2], [0,1],  [48,0.2],type='hilbert', Hz=fs) #2.096
    w, h = sg.freqz(b, [1], worN=2000)
    
    
    ecg_high = sg.filtfilt(b, a, ecg_raw)

    
    # Low-pass filter design parameters
    Fpass_low = 50    # Desired cutoff frequency, Hz
    Fstop_low = 65 #45
    numtaps_low = 137      # Size of the FIR filter.
        
    b_2 = sg.remez(numtaps_low, [0, Fpass_low, Fstop_low, fs/2], [1, 0], [1, 48.25],Hz=fs) #1.925
    
    
    ecg_filt = sg.filtfilt(b_2, a,  ecg_high)
    return ecg_filt;