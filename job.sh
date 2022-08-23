#!/bin/bash
rm sim_log.csv
for i in {1..10}
do
    python3 main_script_simulation.py 0
    python3 main_script_simulation.py 2    
done
python3 sim_analysis.py
