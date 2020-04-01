import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv('network_obs.csv')

df = df.drop(['segmentSize','minRTT'],axis=1)

plt.figure(figsize=(10,10))
# plt.figure()
sns.heatmap(df.corr(), annot=True, cmap='Spectral')
plt.show()