# libraries
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


# data
df=pd.DataFrame({'x': range(1,10), 'y': np.random.randn(9)*80+range(1,10) })
 
# plot
plt.plot( 'x', 'y', data=df, linestyle='-', marker='o')
plt.show()