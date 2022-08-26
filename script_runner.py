# Test script to run .py files on Windows
import subprocess
import os, sys
import numpy as np
import pandas as pd
args = sys.argv
os.remove('sim_all_flows.csv')
str_array = []
parameter_name = args[1]
p_preference_range = np.array([0.5,0.7, 0.9, 0.99, 0.999, 1.0])
max_buff_length_range = np.linspace(25, 200, 10)
lamda_range = np.linspace(1e3, 4e3, 4)
tx_rate_range = np.array([10e6, 25e6, 50e6, 100e6])
p_preference_default = 0.9
max_buff_default = 150
lamda_default = 1.5e4
tx_rate_default = 25e6
if(args[1] == 'p_preference'):
  # change p_preference, keep everything else same
  parameter_vals = p_preference_range
  for p in p_preference_range:
    str = f"{p} {max_buff_default} {lamda_default} {tx_rate_default}"
    str_array.append(str)
elif(args[1] == 'max_buff_length'):
  parameter_vals = max_buff_length_range
  for max_buff in max_buff_length_range:
    str = f"{p_preference_default} {max_buff} {lamda_default} {tx_rate_default}"
    str_array.append(str)
elif(args[1] == 'lamda'):
  parameter_vals = lamda_range
  for lamda in lamda_range:
    str = f"{p_preference_default} {max_buff_default} {lamda} {tx_rate_default}"
    str_array.append(str)
elif(args[1] == 'tx_rate'):
  parameter_vals = tx_rate_range
  for tx_rate in tx_rate_range:
    str = f"{p_preference_default} {max_buff_default} {lamda_default} {tx_rate}"
    str_array.append(str)
# cc_index = int(args[1])
# route_seed = int(args[2])
# p_preference = int(args[3])
# max_buff_length = int(args[4])
j=0
for str in str_array:
  print(f"Params : {parameter_name} {str}")
  for i in range(5):
    subprocess.call(f"py main_script_simulation.py 0 {i} {str}", shell=True)
    subprocess.call(f"py main_script_simulation.py 2 {i} {str}", shell=True)
  subprocess.call(f"py sim_analysis.py {parameter_name} {parameter_vals[j]}", shell=True)
  os.remove('sim_all_flows.csv')
  j+=1