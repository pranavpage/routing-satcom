# script to present results of simulation that reads the sim_log.csv file
import pandas as pd
import numpy as np
df = pd.read_csv('sim_all_flows.csv', header=None)
df.columns=['cc_type', 'completed', 'dropped', 'mean_delay', 'frac_dropped']
ekici_delay = []
prob_routing_delay = []
ekici_dropped = []
prob_routing_dropped = []
for index, row in df.iterrows():
    if(row['cc_type'] == 'ekici'):
        ekici_delay.append(row['mean_delay'])
        ekici_dropped.append(row['frac_dropped'])
    elif(row['cc_type'] == 'prob-routing'):
        prob_routing_delay.append(row['mean_delay'])
        prob_routing_dropped.append(row['frac_dropped'])
print(f"Average ekici delay : {np.mean(np.array(ekici_delay))*1e3:.3f} ms, average fraction of dropped pkts : {np.mean(np.array(ekici_dropped)):.3f}")
print(f"Average prob_routing delay : {np.mean(np.array(prob_routing_delay))*1e3:.3f} ms, average fraction of dropped pkts : {np.mean(np.array(prob_routing_dropped)):.3f}")