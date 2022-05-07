from cmath import polar
from selectors import EpollSelector
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
polar_region_boundary = 75
def sat_in_polar_region(s, polar_region_boundary = polar_region_boundary):
    polar_angle = s*360/num_sats
    theta = 90 - polar_region_boundary
    # 0 to 360
    # (0, theta), (180 - theta, 180 + theta), (360 - theta, 360)
    if(polar_angle>=0 and polar_angle<=theta):
        return 1
    elif(polar_angle >= 180 - theta and polar_angle <= 180 + theta):
        return 1
    elif(polar_angle >= 360 - theta and polar_angle <= 360):
        return 1
    else:
        return 0
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
    def __init__(self, h, plane_idx, sat_idx, polar_angle):
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
    def __repr__(self):
        return f"({self.p1} , {self.s1}) -> ({self.p2}, {self.s2}), hops = {self.hops}"
#def condition_6(p1, s1, p2, s2, )
def s_to_lat(s):
    polar_angle = s*num_sats/360
    lat = abs(180 - polar_angle) - 90
    return lat
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
    fig = plt.figure(0)
    ax = fig.gca(projection = '3d')
    ax.set_xlim3d(-R, R)
    ax.set_ylim3d(-R, R)
    ax.set_zlim3d(-R, R)
    ax.scatter(coordinates[:,0],coordinates[:,1],coordinates[:,2], c = dir_sats, alpha = 0.2)
    return coordinates
planes, sats, dir_sats = initialize_constellation(alt, P, num_sats, inclination)
def plot_path(nodes_list, coords):
    for node in nodes_list:
        [p1, s1] = node 
        node_coords = coords[num_sats*p1 + s1, :]
        fig = plt.figure(0)
        ax = fig.gca(projection = '3d') 
        ax.scatter(node_coords[0], node_coords[1], node_coords[2], c = 'red')
    return 0
print(inclination)
coords = plot_constellation(sats, dir_sats)
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
        self.primary = [0, 0]
        self.secondary = [0, 0]
    def __repr__(self):
        return f"dv={self.dv}, dh={self.dh}, nv={self.nv}, nh={self.nh}, hops={self.hops}, primary={self.primary}, secondary = {self.secondary} \n"
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
            pv.dv = (-1)*(2*(s2-s1) < num_sats) + (+1)*(2*(s2-s1) >= num_sats)
        elif(s1 >= num_sats/2 and s2 < num_sats/2):
            #1 West, 2 East
            pv.dh = (+1)*(p1 < p2) + (-1)*(p1 > p2)
            pv.dv = (+1)*(2*(s1-s2) < num_sats) + (-1)*(2*(s1-s2) >= num_sats)
            print("1w2e")
        pv.nh = abs(p1 - p2)
        pv.nv = min(abs(s1-s2), num_sats - abs(s1-s2))
        pv.hops = pv.nv + pv.nh
        print(pv)
    if(pv.hops == min(pv.hops, ph.hops)):
        return pv
    else:
        return ph
def direction_enhancement(p1, s1, p2, s2):
    path_de = direction_estimation(p1, s1, p2, s2)
    if(sat_in_polar_region(s1)):
        #hop in same plane
        print("polar")
        if(path_de.dv):
            path_de.primary=[0, path_de.dv]
            path_de.dh = 0
        else:
            if(s1 < num_sats/4 or s1 > 3*num_sats/4):
                path_de.primary = [0, -1]
            else:
                path_de.primary = [0, 1]
            path_de.dh = 0
    elif(sat_in_polar_region(s1+1) or sat_in_polar_region(s1-1)):
        if(path_de.dh):
            path_de.primary = [path_de.dh, 0]
            if(path_de.dv):
                path_de.secondary = [0, path_de.dv]
        else:
            path_de.primary = [0, path_de.dv]
    else:
        #condition on nh (6)
        if(s_to_lat(s1) > s_to_lat(s2)):
            if(path_de.dh):
                path_de.primary = [path_de.dh, 0]
            else:
                path_de.primary = [0, path_de.dv]
        elif(s_to_lat(s1) < s_to_lat(s2)):
            path_de.primary = [0, path_de.dv]
        else:
            path_de.primary = [path_de.dh, 0]
            
            
        
    return path_de 

# integrate with constellation 
# add 4 buffers to satellites

#testing routing
np.random.seed(5)
p1, p2 = np.random.randint(0, P, 2)
s1, s2 = np.random.randint(0, num_sats, 2) 
print(direction_estimation(11,20, 11, 8))
print(s_to_lat(19), s_to_lat(8))
print(f"testing ({p1} , {s1}) -> ({p2}, {s2})")
pkt = packet(p1, s1, p2, s2, 0)
i=0
nodes_list = []
while(pkt.p1 != p2 or pkt.s1 != s2):
    path_enhanced = direction_enhancement(pkt.p1, pkt.s1, pkt.p2, pkt.s2)
    print(path_enhanced)
    if(path_enhanced.primary[0]):
        pkt.p1 += path_enhanced.primary[0]
        pkt.p1 = (pkt.p1 + P)%P
        pkt.hops +=1
    else:
        if(pkt.s1 >= num_sats/2 or pkt.s1 ==0):
            pkt.s1 -= path_enhanced.primary[1]
            pkt.s1 = (pkt.s1 + num_sats)%num_sats
            pkt.hops +=1
        else :
            pkt.s1 -= path_enhanced.primary[1]
            pkt.s1 = (pkt.s1 + num_sats)%num_sats
            pkt.hops +=1
    print(pkt)
    node = [pkt.p1, pkt.s1]
    nodes_list.append(node)
plot_path(nodes_list, coords=coords)
plt.savefig("path_routed.png")
plt.show()
## Routing works!!

    