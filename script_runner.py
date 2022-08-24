# Test script to run .py files on Windows
import subprocess
import os
os.remove('sim_all_flows.csv')
for i in range(5):
  subprocess.call(f"python3 main_script_simulation.py 0 {i}", shell=True)
  subprocess.call(f"python3 main_script_simulation.py 2 {i}", shell=True)
subprocess.call("python3 sim_analysis.py", shell=True)