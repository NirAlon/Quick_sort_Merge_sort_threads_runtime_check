import matplotlib.pyplot as plt
import pandas as pd


with open('quicksort') as file:
    array2d = [[float(digit) for digit in line.split()] for line in file]
with open('margesort') as file:
    array2d_marge = [[float(digit) for digit in line.split()] for line in file]

df=pd.DataFrame(array2d,columns=['x', 'y'])
df_marge = pd.DataFrame(array2d_marge,columns=['x', 'y'])

ax = df.plot(kind='line',x='x',y='y',label='Quick Sort')

df_marge.plot(ax=ax,kind='line',color='red',x='x',y='y',label='Marge Sort')

plt.show();
