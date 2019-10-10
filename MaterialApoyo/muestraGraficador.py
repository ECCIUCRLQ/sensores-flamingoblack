# library
import matplotlib.pyplot as plt
import numpy as np
import sys

#aqui se busca cual es el grupo


# create data
x=range(1,41)
values=np.random.uniform(size=40)
 
# stem function: first way
plt.stem(x, values)
plt.ylim(0, 1.2)
plt.show()
 
# stem function: If no X provided, a sequence of numbers is created by python:
plt.stem(values)
#plt.show()
 
# stem function: second way
(markerline, stemlines, baseline) = plt.stem(x, values)
plt.setp(baseline, visible=False)
#plt.show()