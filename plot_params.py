import numpy as np
import matplotlib.pyplot as plt 
import pandas as pd 
from matplotlib.ticker import FormatStrFormatter
plt.rcParams['text.usetex'] = True
tag = 'single_flow'
var = 'lamda'
df = pd.read_csv(f'sim_{tag}_{var}.csv', header=None, usecols=[1,2,3,4,5], skiprows = 0)
df.columns = [var, 'ekici_delay', 'prob_routing_delay', 'ekici_dropped', 'prob_routing_dropped']
fig, ax1 = plt.subplots()
# ax1.axhline(df['ekici_delay'][0], linestyle='--', color='k', label = 'Ekici delay')
ax1.plot(df[var], df['ekici_delay'], '-xk', label = 'Ekici delay')
ax1.plot(df[var], df['prob_routing_delay'], '-ok', label= 'prob\_routing delay')
# plt.ylim(0.092, 0.1020)
ax1.set_ylabel('Average delay (s)')
ax1.legend(loc='upper left')
plt.xlabel('$\lambda_{in}$ packets/s')
ax1.xaxis.set_major_formatter(FormatStrFormatter('%.1e'))
plt.grid(True)
# ax2 = ax1.twinx()
# ax2.set_ylabel('Fraction of packets dropped')
# ax2.plot(df[var], df['ekici_dropped'], '-xb', label = 'Ekici dropped')
# # ax2.axhline(df['ekici_dropped'][0], linestyle='--', color='b', label = 'Ekici dropped')
# ax2.plot(df[var], df['prob_routing_dropped'], '-ob', label = 'prob_routing dropped')
# ax2.legend(loc = 'lower right')
# ax2.yaxis.label.set_color('b')
# ax2.tick_params(axis='y', colors='b')
# ax2.spines['right'].set_color('b')
plt.savefig(f'Paper/images/{tag}_delay_with_{var}.png')
plt.show()
print(df.head())
