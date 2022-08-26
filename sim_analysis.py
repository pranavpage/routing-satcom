# script to present results of simulation that reads the sim_log.csv file
import pandas as pd
import numpy as np
import sys 
args = sys.argv
parameter_name = args[1]
parameter_val = args[2]
df = pd.read_csv('sim_single_flow.csv', header=None)
df.columns=['cc_type', 'flow_completed', 'dropped_flow','frac_dropped','avg_flow_drop_time', 'mean_delay', 'stddev', 'avg_throughput']
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
avg_ekici_delay = np.mean(np.array(ekici_delay))
avg_prob_routing_delay = np.mean(np.array(prob_routing_delay))
avg_fraction_ekici_drop = np.mean(np.array(ekici_dropped))
avg_fraction_prob_routing_drop = np.mean(np.array(prob_routing_dropped))
print(f"Average ekici delay : {avg_ekici_delay*1e3:.3f} ms, average fraction of dropped pkts : {avg_fraction_ekici_drop:.3f}")
print(f"Average prob_routing delay : {avg_prob_routing_delay*1e3:.3f} ms, average fraction of dropped pkts : {avg_fraction_prob_routing_drop:.3f}")
df2 = pd.DataFrame(columns=['parameter_name','parameter_val','ekici_delay', 'prob_routing_delay', 'ekici_dropped', 'prob_routing_dropped'])
df2.loc[len(df2.index)] = [parameter_name, parameter_val, avg_ekici_delay, avg_prob_routing_delay, avg_fraction_ekici_drop, avg_fraction_prob_routing_drop]
df2.to_csv(f"sim_single_flow_{parameter_name}.csv", index=False, header=False, mode='a')