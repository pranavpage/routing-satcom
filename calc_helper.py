# Script to do calculations
import numpy as np
tx_rate = 25e6 # bits/s
pkt_size = 2**(13) # bits/pkt
lamda_min = 4*tx_rate/pkt_size # pkts/s
lamda = 1.1*lamda_min
t_step = 1e-2
num_packets_per_step = lamda*t_step
t_stop = 30e-3
print(f"TX Rate : {tx_rate/1e6:.2f} Mbps")
print(f"Packet size : {pkt_size/(2**13) : .2f} kB")
print(f"Min lamda : {lamda_min:.2e} pkts/s")
print(f"t_step = {t_step*1e3:.2f} ms")
print(f"Lamda : {lamda:.2e} pkts/s = {lamda*pkt_size/(1e6):.2f} Mbps")
print(f"Num packets/step = {num_packets_per_step:.2e}")
print(f"t_stop = {t_stop*1e3:.2f} ms")
print(f"Num steps = {int(t_stop/t_step)}")
print(f"Queue length at end of sim = {(lamda-lamda_min)*t_stop:.2e}")