# Test script to run .py files on Windows
import subprocess
import os
# os.remove('sim_log.csv', shell=True)
for i in range(1):
  subprocess.call("python3 main_script_simulation.py 0", shell=True)
  subprocess.call("python3 main_script_simulation.py 2", shell=True)
subprocess.call("python3 sim_analysis.py", shell=True)