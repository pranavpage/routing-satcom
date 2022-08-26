import numpy as np
import matplotlib.pyplot as plt 
import pandas as pd 
from matplotlib.ticker import FormatStrFormatter
df = pd.read_csv('sim_all_flows_drop_buff_length.csv', header=None, usecols=[1,2,3,4,5], skiprows = 1)
df.columns = ['drop_buff_length', 'ekici_delay', 'prob_routing_delay', 'ekici_dropped', 'prob_routing_dropped']
fig, ax1 = plt.subplots()
ax1.plot(df['drop_buff_length'], df['ekici_delay'], '-xk', label = 'Ekici delay')
ax1.plot(df['drop_buff_length'], df['prob_routing_delay'], '-ok', label= 'prob_routing delay')
ax1.set_ylabel('Average delay (s)')
ax1.legend(loc='upper left')
plt.xlabel('drop_buff_length (packets)')
# ax1.xaxis.set_major_formatter(FormatStrFormatter('%.1e'))
plt.grid(True)
# ax2 = ax1.twinx()
# ax2.set_ylabel('Fraction of packets dropped')
# ax2.plot(df['drop_buff_length'], df['ekici_dropped'], '-xb', label = 'Ekici dropped')
# ax2.plot(df['drop_buff_length'], df['prob_routing_dropped'], '-ob', label = 'prob_routing dropped')
# ax2.legend(loc = 'lower right')
# ax2.yaxis.label.set_color('b')
# ax2.tick_params(axis='y', colors='b')
# ax2.spines['right'].set_color('b')
plt.savefig('delay_with_drop_buff_length_only.png')
plt.show()
print(df.head())
