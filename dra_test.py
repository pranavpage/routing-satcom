# script to test dra as implemented in sat_network.py
alt = 600e3
P = 24
num_sats = 24
inclination = 90
R = 6.378e6
G = 6.674e-11
M = 5.972e24
polar_region_boundary = 75
event_queue = []
transmit_delay = 1
t = 0
algo_type = 'dra'
from sat_network import direction_estimation, direction_enhancement

