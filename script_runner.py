# Test script to run .py files on Windows
import subprocess
import os, sys
import numpy as np
import pandas as pd
args = sys.argv
# os.remove('sim_all_flows.csv')
str_array = []
parameter_name = args[1]
p_preference_range = np.linspace(0.1, 0.9, 10)
max_buff_length_range = np.linspace(25, 200, 10)
p_preference_default = 0.9
max_buff_default = 50
if(args[1] == 'p_preference'):
  # change p_preference, keep everything else same
  parameter_vals = p_preference_range
  for p in p_preference_range:
    str = f"{p} {max_buff_default}"
    str_array.append(str)
elif(args[1] == 'max_buff_length'):
  parameter_vals = max_buff_length_range
  for max_buff in max_buff_length_range:
    str = f"{p_preference_default} {max_buff}"
    str_array.append(str)
# cc_index = int(args[1])
# route_seed = int(args[2])
# p_preference = int(args[3])
# max_buff_length = int(args[4])
j=0
for str in str_array:
  print(f"Params : {parameter_name} {str}")
  for i in range(2):
    subprocess.call(f"python3 main_script_simulation.py 0 {i} {str}", shell=True)
    subprocess.call(f"python3 main_script_simulation.py 2 {i} {str}", shell=True)
  subprocess.call(f"python3 sim_analysis.py {parameter_name} {parameter_vals[j]}", shell=True)
  os.remove('sim_all_flows.csv')
  j+=1