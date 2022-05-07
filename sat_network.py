from cmath import polar
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
#need to build a satellite network with nodes and (lat, long)
alt = 600e3 #600 km above the earth
P = 12 #number of orbital planes
h = alt*np.ones(P) #altitude
num_sats = 24 #satellites per plane 
inclination = 90
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
    def __repr__(self):
        return ' altitude= {}, longitude= {}, inclination= {}, number of satellites= {}, period= {} hours \n'.format(
	self.h,
	'%.2f'%(self.longitude),
	'%.2f'%self.inclination,
	'%.2f'%self.num_sats,
	'%.2f'%(self.period/3600))
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
class packet:
    def __init__(self, p1, s1, p2, s2, t):
        self.p1 = p1 
        self.s1 = s1 
        self.p2 = p2 
        self.s2 = s2
        self.hops = 0
        self.t_origin = t
def initialize_constellation(alt, P, num_sats, inclination):
    planes = [] 
    sats = []
    i=0
    dir_sats = np.zeros(P*num_sats)
    for plane_idx in range(P):
        longitude = 180*plane_idx/P
        planes.append(orbital_plane(alt, longitude, inclination, num_sats))
        for sat_idx in range(num_sats):
            polar_angle = 2*np.pi*sat_idx/(num_sats)
            if(polar_angle > np.pi):
                dir_sats[i] = 1
            sats.append(satellite(alt, plane_idx, sat_idx, polar_angle))
            #calculate x,y,z
            delta = np.pi/2 - 2*np.pi*inclination/360
            theta = 2*np.pi*planes[plane_idx].longitude/360
            phi = sats[i].polar_angle
            sats[i].x = (alt + R)*(np.sin(phi)*np.cos(theta) + np.cos(phi)*np.sin(delta)*np.sin(theta))
            sats[i].y = (alt + R)*(np.sin(phi)*np.sin(theta) - np.cos(phi)*np.sin(delta)*np.cos(theta))
            sats[i].z = (alt + R)*(np.cos(phi)*np.cos(delta))
            i+=1
    return planes, sats, dir_sats
def plot_constellation(sats, dir_sats):
    coordinates = np.zeros((len(sats), 3))
    for i in range(len(sats)):
        coordinates[i,:] = [sats[i].x, sats[i].y, sats[i].z]
    fig = plt.figure()
    ax = fig.gca(projection = '3d')
    ax.set_xlim3d(-R, R)
    ax.set_ylim3d(-R, R)
    ax.set_zlim3d(-R, R)
    ax.scatter(coordinates[:,0],coordinates[:,1],coordinates[:,2], c = dir_sats)
    return coordinates
planes, sats, dir_sats = initialize_constellation(alt, P, num_sats, inclination)
print(inclination)
#coords = plot_constellation(sats, dir_sats)
#plt.savefig("sat_constellation_vp.png")
#plt.show()

# each vp has a buffer queue
# pkt generated knows source and destination (p,s)
# ph does not cross polar region 
# pv does
class min_path:
    def __init__(self, dv, dh, nv, nh):
        self.dv = dv 
        self.dh = dh
        self.nv = nv 
        self.nh = nh 
        self.hops = 0
    def __repr__(self):
        return f"dv={self.dv}, dh={self.dh}, nv={self.nv}, nh={self.nh}, hops={self.hops} \n"
def direction_estimation(p1, s1, p2, s2):
    ph = min_path(0,0,0,0)
    pv = min_path(0,0,0,0)
    if(s1 < num_sats/2 and s2 < num_sats/2):
        #Eastern Hemisphere
        ph.dh = (+1)*(p1 < p2) + (-1)*(p1 > p2)
        ph.dv = (-1)*(s1 < s2) + (+1)*(s1 > s2)
        ph.nv = abs(s1 - s2)
        ph.nh = abs(p1 - p2)
        ph.hops = ph.nv + ph.nh
        
        pv.dh = (-1)*(p1 < p2) + (+1)*(p1 >= p2)
        pv.dv = (+1)*(2*(s1+s2+1) < num_sats) + (-1)*(2*(s1+s2+1) > num_sats) + (+1)*(2*(s1+s2+1) == num_sats)
        pv.nh = (P - abs(p1-p2))
        pv.nv = min((s1 + s2 + 1), num_sats - (s1 + s2 + 1))
        pv.hops = pv.nv + pv.nh
        pass
    elif(s1 >= num_sats/2 and s2 >= num_sats/2):
        #Western Hemisphere
        ph.dh = (+1)*(p1 < p2) + (-1)*(p1 > p2)
        ph.dv = (-1)*(s1 < s2) + (+1)*(s1 > s2)
        ph.nv = abs(s1 - s2)
        ph.nh = abs(p1 - p2)
        ph.hops = ph.nv + ph.nh
        
        pv.dh = (-1)*(p1 < p2) + (+1)*(p1 >= p2)
        pv.dv = (+1)*(2*(s1+s2+1) < 3*num_sats) + (-1)*(2*(s1+s2+1) >= 3*num_sats)
        pv.nh = (P - abs(p1-p2))
        pv.nv = min((s1 + s2 + 1) - num_sats,2*num_sats - (s1 + s2 + 1))
        pv.hops = pv.nv + pv.nh
        pass
    else:
        #Different sides of the seam
        ph.dh = (-1)*(p1 < p2) + (+1)*(p1 > p2)
        ph.dv = (+1)*((num_sats - 1 - s1) < s2) + (-1)*((num_sats - 1 - s1) > s2)
        ph.nv = abs(num_sats-s1 - s2-1)
        ph.nh = abs(p1 - p2) + num_sats
        ph.hops = ph.nv + ph.nh
        
        if(s1 < num_sats/2 and s2 >= num_sats/2):
            #1 East, 2 West
            pv.dh = (+1)*(p1 < p2) + (-1)*(p1 > p2)
            pv.dv = (-1)*(2*(s1-s2) < num_sats) + (+1)*(2*(s1-s2) >= num_sats)
        elif(s1 >= num_sats/2 and s2 < num_sats/2):
            #1 West, 2 East
            pv.dh = (+1)*(p1 < p2) + (-1)*(p1 > p2)
            pv.dv = (+1)*(2*(s1-s2) < num_sats) + (-1)*(2*(s1-s2) >= num_sats)
        
        pv.nh = abs(p1 - p2)
        pv.nv = min(abs(s1-s2), num_sats - abs(s1-s2))
        pv.hops = pv.nv + pv.nh        
    return ph, pv
ph, pv = direction_estimation(2, 8, 5, 6)
print(ph, pv)
