import numpy as np
import matplotlib.pyplot as plt
#need to build a satellite network with nodes and (lat, long)

alt = 600e3 #600 km above the earth
P = 72 #number of orbital planes
h = alt*np.ones(P) #altitude
num_sats = 22 #satellites per plane 

#set up a network of virtual nodes
