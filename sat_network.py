import numpy as np
import matplotlib.pyplot as plt
#need to build a satellite network with nodes and (lat, long)

alt = 600e3 #600 km above the earth
P = 72 #number of orbital planes
h = alt*np.ones(P) #altitude
num_sats = 22 #satellites per plane 
#set up a network of virtual nodes
R = 6.378e6
G = 6.674e-11
M = 5.972e24
class orbital_plane:
    def __init__(self, h, longitude, inclination, num_sats):
        self.h = h
        self.longitude = longitude 
        self.inclination = inclination 
        self.num_sats = num_sats
        self.period = 2 * np.pi * np.sqrt((self.h+R)**3/(G*M))
        
class satellite:
    def __init__(self, h, plane_idx, sat_idx, polar_angle) -> None:
        self.h = h
        self.plane_idx = plane_idx
        self.sat_idx = sat_idx 
        self.polar_angle = polar_angle
        self.x = 0
        self.y = 0
        self.z = 0
        self.latitude = (np.pi/2 - self.polar_angle + 2*np.pi)%(2*np.pi)
