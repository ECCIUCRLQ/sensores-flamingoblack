# libraries
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import sys

#aqui se compara cual argumento se recibió y compara para llamar al metodo de la intefaz que permita 
#traer todos los datos que tenga de ese grupo y sensor en ese momento para graficarlo
if sys.argv[1] == "FlamingoBlack":
    if sys.argv[2] == "1":
        print("FlamingoBlack sensor 1")
    elif sys.argv[2] == "2":
        print("FlamingoBlack sensor 2")
        
elif sys.argv[1] == "FlamingoBlack":
    if sys.argv[2] == "1":
        print("FlamingoBlack sensor 1")
    elif sys.argv[2] == "2":
        print("FlamingoBlack sensor 2")

 
# data
#df=pd.DataFrame({'x': range(1,10), 'y': np.random.randn(9)*80+range(1,10) })
 
# plot
#plt.plot( 'x', 'y', data=df, linestyle='-', marker='o')
#plt.show()