#!/bin/bash
rm sim_log.csv
for i in {1..5}
do
    python3 main_script_simulation.py 0    
done
