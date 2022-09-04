import numpy as np
import matplotlib.pyplot as plt 
import pandas as pd 
from matplotlib.ticker import FormatStrFormatter
plt.rcParams.update({'font.size': 13})
plt.rcParams['text.usetex'] = True
tag = 'all_flows'
var = 'threshold_fraction'
param = 'dropped'
df = pd.read_csv(f'sim_{tag}_{var}.csv', header=None, usecols=[1,2,3,4,5], skiprows = [0,1,2])
df.columns = [var, 'ekici_delay', 'prob_routing_delay', 'ekici_dropped', 'prob_routing_dropped']
fig, ax1 = plt.subplots()
# ax1.axhline(df['ekici_delay'][0], linestyle='--', color='k', label = 'Ekici delay')
ax1.plot(df[var]*200, df[f'ekici_{param}'], '-xk', label = f'Ekici {param}')
ax1.plot(df[var]*200, df[f'prob_routing_{param}'], '-ok', label= f'prob\_routing {param}')
if(param == 'delay'):
    ax1.set_ylabel('Average delay (s)')
    ax1.legend(loc='upper left')
else:
    ax1.set_ylabel('Average fraction of dropped packets')
    ax1.legend(loc='upper left')
# ax1.set_xscale('log')
plt.xticks(df[var]*200, rotation=90)
plt.xlabel('$N_{threshold}$ packets')
plt.minorticks_off()
plt.tight_layout()
ax1.xaxis.set_major_formatter(FormatStrFormatter('%.0f'))
# ax1.xaxis.set_minor_formatter(FormatStrFormatter('%.0f'))
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
plt.savefig(f'Paper/images/{tag}_{param}_with_{var}.png')
plt.show()
print(df.head())
