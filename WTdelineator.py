
from pywt import wavedec 
 
def waveletDecomp(sig):
    
#    widths = np.array([2**1, 2**2, 2**3, 2**4, 2**5])
    coeffs = wavedec(sig, 'coif9', level = 3)
    
#        
    cA, cD1, cD2, cD3 = coeffs
            
    return cA, cD1, cD2, cD3
