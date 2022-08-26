import numpy as np
import matplotlib.pyplot as plt 
import pandas as pd 
df = pd.read_csv('sim_all_flows_max_buff_length.csv', header=None, usecols=[1,2,3,4,5], skiprows = 11)
df.columns = ['max_buffer_length', 'ekici_delay', 'prob_routing_delay', 'ekici_dropped', 'prob_routing_dropped']
plt.figure(0)
plt.plot(df['max_buffer_length'], df['ekici_delay'], '-ok', label = 'Ekici')
plt.plot(df['max_buffer_length'], df['prob_routing_delay'], '-ob', label= 'prob_routing')
plt.ylabel('Average delay (s)')
plt.xlabel('max_buffer_length')
plt.grid(True)
plt.legend()
plt.savefig('delay_with_max_buffer_length.png')
plt.show()
print(df.head())
