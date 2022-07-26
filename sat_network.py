from cProfile import label
from matplotlib import projections
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
#need to build a satellite network with nodes and (lat, long)
alt = 600e3 #600 km above the earth
P = 12 #number of orbital planes
h = alt*np.ones(P) #altitude
num_sats = 25 #satellites per plane 
inclination = 90
#set up a network of virtual nodes
R = 6.378e6
G = 6.674e-11
M = 5.972e24
polar_region_boundary = 75
theta_intra_plane = 360.0/num_sats
theta_inter_plane = 180.0/P
l_intra_plane = R*np.sqrt(2*(1-np.cos(np.radians(theta_intra_plane))))
l_alpha = R*np.sqrt(2*(1-np.cos(np.radians(theta_inter_plane))))

print(f"Number of orbital planes = {P}, sats per plane = {num_sats}")
print(f"Inter plane angle : {theta_inter_plane:.2f}")
print(f"Intra plane angle : {theta_intra_plane:.2f}")
print(f"Polar Region bdry : {polar_region_boundary}")
def sat_in_polar_region(s, polar_region_boundary = polar_region_boundary):
    polar_angle = s*360.0/num_sats
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
def s_to_lat(s):
    polar_angle = s*360/num_sats
    lat = abs(180 - polar_angle) - 90
    return lat
def ps_to_long(p, s):
    polar_angle = 360.0*s/num_sats
    if(polar_angle>180):
        # diff hemisphere
        longitude = (p*180.0/P) - 180
    else:
        longitude = (p*180.0/P)
    return longitude
class satellite:
    def __init__(self, h, plane_idx, sat_idx, polar_angle):
        self.h = h
        self.plane_idx = plane_idx
        self.sat_idx = sat_idx 
        self.polar_angle = polar_angle
        self.x = 0
        self.y = 0
        self.z = 0
        self.latitude = np.radians(s_to_lat(sat_idx))
        self.longitude = np.radians(ps_to_long(plane_idx, sat_idx))
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
s_min = np.floor((90 - polar_region_boundary)/theta_intra_plane)+1
lat_min = s_to_lat(s_min)
print(f"Max latitude of ring : {lat_min:.2f}")
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
def plot_constellation(sats, dir_sats, num):
    # coordinates = np.zeros((len(sats), 3))
    # for i in range(len(sats)):
    #     coordinates[i,:] = [sats[i].x, sats[i].y, sats[i].z]
    # fig = plt.figure(num)
    # ax = fig.gca(projection = '3d')
    # ax.set_xlim3d(-R, R)
    # ax.set_ylim3d(-R, R)
    # ax.set_zlim3d(-R, R)
    # ax.scatter(coordinates[:,0],coordinates[:,1],coordinates[:,2], c = dir_sats, alpha = 0.5, s=2.5**2)
    
    fig2 = plt.figure(num)
    ax2 = fig2.gca(projection = 'mollweide')
    ax2.grid()
    polar_coords = np.zeros((len(sats), 2))
    polar_map = np.zeros((len(sats), 1))
    for i in range(len(sats)):
        polar_coords[i, :] = [sats[i].latitude, sats[i].longitude]
        polar_map[i,:] = sat_in_polar_region(sats[i].sat_idx)
    ax2.scatter(polar_coords[:,1], polar_coords[:, 0], alpha=0.5, s=polar_map*20, c='c', label='polar region')
    ax2.scatter(polar_coords[:,1], polar_coords[:, 0], alpha=0.5, s=(1-polar_map)*20, c='k')
    ax2.plot( [0, 0],[np.pi/2, -np.pi/2], '--r')
    return 0

planes, sats, dir_sats = initialize_constellation(alt, P, num_sats, inclination)
def plot_path(nodes_list, num):
    len_nodes = len(nodes_list)
    fig = plt.figure(num)
    ax = fig.gca(projection = 'mollweide')
    polar_coords = np.zeros((len_nodes, 2))
    for i in range(len_nodes):
        lat_1 = s_to_lat(nodes_list[i][1])
        long_1 = ps_to_long(nodes_list[i][0], nodes_list[i][1])
        polar_coords[i, :] = [np.radians(lat_1), np.radians(long_1)]
    ax.plot(polar_coords[:,1], polar_coords[:,0], '-ob', label='route', alpha=0.5, markersize=2**2)
    ax.scatter(polar_coords[0,1], polar_coords[0,0], color='g', label='source', s=8**2, marker='x')
    ax.scatter(polar_coords[-1,1], polar_coords[-1,0], color='r', label='destination', s=8**2,marker='x')
    # for node in nodes_list:
    #     [p1, s1] = node 
    #     node_coords = coords[num_sats*p1 + s1, :]
    #     fig = plt.figure(num)
    #     ax = fig.gca(projection = '3d') 
    #     if(i>0 and i!= len_nodes-1):
    #         ax.scatter(node_coords[0], node_coords[1], node_coords[2], c = 'red', s=5**2)
    #     elif(i!=len_nodes-1):
    #         ax.scatter(node_coords[0], node_coords[1], node_coords[2], c = 'green', s=5**2)
    #     else:
    #         ax.scatter(node_coords[0], node_coords[1], node_coords[2], c = 'blue', s=5**2)
    #     i+=1
    return 0
print(inclination)
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
def go_polar(p1, s1, p2, s2, path_de):
    # condition 6 in paper
    # decides whether going polar is shorter
    lat_1 = s_to_lat(s1)
    lat_2 = s_to_lat(s2)
    long_1 = ps_to_long(p1, s1)
    long_2 = ps_to_long(p2, s2)
    nh = path_de.nh
    if(lat_1>=0):
        #northern hemisphere
        max_hops = int(np.floor((polar_region_boundary - lat_1)*num_sats/360.0))
        hops_list = np.arange(0, max_hops+1, 1)
        k = max_hops+s_min
        th_list = (P*np.cos(np.radians(lat_min)) + (l_intra_plane/l_alpha)*(2*(k-hops_list)+1))/(np.cos(np.radians(lat_1 + hops_list*theta_intra_plane)) + np.cos(np.radians(lat_min)))
        print(th_list)
        print(nh)
        if(nh>max(th_list) and nh>0):
            print("cross polar region (condition 6)")
            return 1
        elif(nh>0):
            print("don't cross polar region")
            return 0
        else:
            print("nh==0")
            return 0
def horizontal_hop(p1, s1, p2, s2, path_de):
    # decision criterion for staying in horizontal ring or moving up/down
    # condition 8 in paper
    print("Horizontal Hop func")
    lat_1 = s_to_lat(s1)
    lat_2 = s_to_lat(s2)
    long_1 = ps_to_long(p1, s1)
    long_2 = ps_to_long(p2, s2)
    # print(f"Source lat : {lat_1:.2f}, Source long : {long_1:.2f}\n Destination lat : {lat_2:.2f}, Destination long : {long_2:.2f}")
    # if(abs(lat_1)<abs(lat_2)):
    #     print("Move to ring of destination")
    #     if(long_1>0):
    #         d_v = (+1)*(lat_1<lat_2) + (-1)*(lat_1>lat_2)
    #         d_h = (+1)*(long_1<long_2) + (-1)*(long_1>long_2)
    #         return [[0, d_v], [d_h, 0]]
    #     else:
    #         d_v = (+1)*(lat_1<lat_2) + (-1)*(lat_1>lat_2)
    #         d_h = (+1)*(long_1<long_2) + (-1)*(long_1>long_2)
    # else:
    print("Run Min calc")
    # |lat_1| > |lat_2|
    # min hops to closest polar region 
    if(lat_1>=0):
        # go north
        max_hops = int(np.floor((polar_region_boundary - lat_1)*num_sats/360.0))
        print(f"Hops to last satellite = {max_hops}")
        hops_list = np.arange(1, max_hops+1, 1)
        th_list = hops_list*(2*l_intra_plane/l_alpha)/(np.cos(np.radians(lat_1)) - np.cos(np.radians(lat_1 + hops_list*theta_intra_plane)))
        n_h = path_de.nh
        if(n_h < min(th_list) and n_h>0):
            print("Same ring")
            # d_h = (+1)*(long_1<long_2) + (-1)*(long_1>long_2)
            # d_v = +1
            return [[path_de.dh, 0], [0, path_de.dv]]
        elif(n_h>0):
            print("Go towards pole")
            # d_v = +1
            # d_h = (+1)*(long_1<long_2) + (-1)*(long_1>long_2)
            if(long_1>0):
                # Eastern
                d_v = +1
            else:
                # Western
                d_v = -1
            return [[0, d_v], [path_de.dh, 0]]
        else:
            print("Same plane")
            return [[0, path_de.dv], [path_de.dh, 0]]
    else:
        # go south
        max_hops = int(np.floor(-(-polar_region_boundary - lat_1)*num_sats/360.0))
        print(f"Hops to last satellite = {max_hops}")
        hops_list = np.arange(1, max_hops+1, 1)
        th_list = hops_list*(2*l_intra_plane/l_alpha)/(np.cos(np.radians(lat_1)) - np.cos(np.radians(lat_1 - hops_list*theta_intra_plane)))
        n_h = path_de.nh
        if(n_h < min(th_list) and n_h > 0):
            print("Same ring")
            # d_h = (+1)*(long_1<long_2) + (-1)*(long_1>long_2)
            # d_v = -1
            return [[path_de.dh, 0], [0, path_de.dv]]
        elif(n_h>0):
            print("Go towards pole")
            # d_v = -1
            # d_h = (+1)*(long_1<long_2) + (-1)*(long_1>long_2)
            if(long_1>0):
                # Eastern
                d_v = -1
            else:
                # Western
                d_v = +1
            return [[0, d_v], [path_de.dh, 0]]
        else:
            print("Same plane")
            return [[0, path_de.dv], [path_de.dh, 0]]
def direction_estimation(p1, s1, p2, s2, dmap='dra'):
    ph = min_path(0,0,0,0)
    pv = min_path(0,0,0,0)
    if(dmap=='dra'):
        if(s1 < num_sats/2 and s2 < num_sats/2):
            #Eastern Hemisphere
            print("here")
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
            ph.dh = (-1)*(p1 < p2) + (+1)*(p1 >= p2)
            #differs from paper
            ph.dv = (+1)*((num_sats - 1 - s1) < s2) + (-1)*((num_sats - 1 - s1) >= s2)
            ph.nv = abs(num_sats-s1 - s2-1)
            ph.nh = -abs(p1 - p2) + P
            ph.hops = ph.nv + ph.nh
            
            if(s1 < num_sats/2 and s2 >= num_sats/2):
                #1 East, 2 West
                print("1e2w")
                pv.dh = (+1)*(p1 < p2) + (-1)*(p1 > p2)
                pv.dv = (-1)*(2*(s2-s1) < num_sats) + (+1)*(2*(s2-s1) >= num_sats)
            elif(s1 >= num_sats/2 and s2 < num_sats/2):
                #1 West, 2 East
                pv.dh = (+1)*(p1 < p2) + (-1)*(p1 > p2)
                pv.dv = (+1)*(2*(s1-s2) < num_sats) + (-1)*(2*(s1-s2) >= num_sats)
            pv.nh = abs(p1 - p2)
            pv.nv = min(abs(s1-s2), num_sats - abs(s1-s2))
            pv.hops = pv.nv + pv.nh
        print(ph)
        print(pv)
        if(pv.hops == ph.hops):
            return ph
        elif(pv.hops == min(ph.hops, pv.hops)):
            return pv
        else:
            return ph
    elif(dmap=='improvement'):
        if((s1<num_sats/2)*(s2<num_sats/2) or (s1>=num_sats/2)*(s2>=num_sats/2)):
            # Same hemisphere
            # don't go polar
            ph.dh = (+1)*(p1 < p2) + (-1)*(p1 > p2)    
            ph.dv = (-1)*(s1 < s2) + (+1)*(s1 > s2)
            ph.nv = abs(s1 - s2)
            ph.nh = abs(p1 - p2)
            ph.hops = ph.nv + ph.nh
            print("ph")
            print(ph)
            return ph
        else:
            # Different hemispheres
            # go polar
            if(s1 < num_sats/2 and s2 >= num_sats/2 ):
                #1 East, 2 West
                pv.dv = (-1)*(2*(s2-s1) < num_sats) + (+1)*(2*(s2-s1) >= num_sats)
                pv.dh = (+1)*(p1 < p2) + (-1)*(p1 > p2)
                print("1e2w")
                print(pv.dv)
            elif(s1 >= num_sats/2 and s2 < num_sats/2):
                #1 West, 2 East
                print("1w2e")
                pv.dh = (+1)*(p1 < p2) + (-1)*(p1 > p2)
                pv.dv = (+1)*(2*(s1-s2) < num_sats) + (-1)*(2*(s1-s2) >= num_sats)
                print(pv.dv)
            pv.nh = abs(p1 - p2)
            pv.nv = min(abs(s1-s2), num_sats - abs(s1-s2))
            pv.hops = pv.nv + pv.nh
            print("pv")
            return pv
            
def direction_enhancement(p1, s1, p2, s2, dmap='dra'):
    path_de = direction_estimation(p1, s1, p2, s2, dmap)
    if(dmap=='dra'):
        lat_1 = s_to_lat(s1)
        lat_2 = s_to_lat(s2)
        print(lat_1, lat_2)
        if(sat_in_polar_region(s1)):
            #hop in same plane
            print("(1) polar")
            if(sat_in_polar_region(s2) and ((lat_1>0 and lat_2>0) or (lat_1<0 and lat_2<0))):
                # both in same polar region
                print("same polar region")
                if(path_de.dh):
                    # go out
                    if(s1 < num_sats/4 or (s1 >= num_sats/2 and s1<3*num_sats/4)):
                        path_de.primary = [0, -1]
                    else:
                        path_de.primary = [0, 1]
                    path_de.dh = 0
                else:
                    # go vertically
                    path_de.primary=[0, path_de.dv]
                    path_de.dh = 0
            elif(sat_in_polar_region(s2)):
                path_de.primary=[0, path_de.dv]
                path_de.dh = 0
            else:
                path_de.primary=[0, path_de.dv]
                path_de.dh = 0
            print(path_de)
        elif(sat_in_polar_region(s1+1) or sat_in_polar_region(s1-1)):
            print("(2) last horizontal ring")
            if(path_de.dh):
                path_de.primary = [path_de.dh, 0]
                if(path_de.dv):
                    path_de.secondary = [0, path_de.dv]
            else:
                path_de.primary = [0, path_de.dv]
        else:
            #condition on nh (6)
            print("(3) Middle of the net")
            # if(s_to_lat(s1) > s_to_lat(s2)):
            #     if(path_de.dh):
            #         path_de.primary = [path_de.dh, 0]
            #     else:
            #         path_de.primary = [0, path_de.dv]
            # elif(s_to_lat(s1) < s_to_lat(s2)):
            #     path_de.primary = [0, path_de.dv]
            # else:
            #     path_de.primary = [path_de.dh, 0]
            
            # need to decide whether to go polar
            if(go_polar(p1, s1, p2, s2, path_de)):
                pass
                # go polar
                path_de.primary = [0, path_de.dv]
                path_de.secondary = [path_de.dh, 0]
            else:
                # don't go polar
                # use horizontal hop
                ret = horizontal_hop(p1, s1, p2, s2, path_de)
                path_de.primary = ret[0]
                print(ret)
                path_de.secondary = ret[1]
                pass
        return path_de
    elif(dmap=='improvement'):
        if(sat_in_polar_region(s1)):
            # (1) polar region
            print("polar")
            if(path_de.dv):
                # not in same ring
                if(sat_in_polar_region(s2) and abs(s1-s2)<num_sats/2):
                    # both in polar, dv!=0
                    if((s1<num_sats/2)*(s2<num_sats/2) or (s1>=num_sats/2)*(s2>=num_sats/2)):
                        # both in polar, dv!=0, same hemisphere
                        # go out
                        if(s1 < num_sats/4 or s1 > 3*num_sats/4):
                            path_de.primary = [0, -1]
                        else:
                            path_de.primary = [0, 1]
                    else:
                        # both in polar, dv!=0, different hemisphere
                        # mark dv primary
                        # dh zero
                        path_de.primary=[0, path_de.dv]
                        path_de.dh = 0
                        pass
                else:
                    # s2 not in polar, dv!=0
                    # mark dv primary
                    # dh zero
                    print("here")
                    print(path_de)
                    path_de.primary=[0, path_de.dv]
                    path_de.dh = 0
                    pass
            else:
                # dv==0
                # go outside
                print(f"({p1}, {s1})")
                if(s1 < num_sats/4 or s1 > 3*num_sats/4):
                    path_de.primary = [0, -1]
                else:
                    path_de.primary = [0, 1]
                pass
        elif(sat_in_polar_region(s1+1) or sat_in_polar_region(s1-1)):
            # (2) last horizontal ring
            print("Last horizontal ring")
            if(path_de.dh):
                path_de.primary = [path_de.dh, 0]
                if(path_de.dv):
                    path_de.secondary = [0, path_de.dv]
            else:
                path_de.primary = [0, path_de.dv]
            pass
        else:
            # (3) middle of the net 
            print("Middle of the net")
            if((s1<num_sats/2)*(s2<num_sats/2) or (s1>=num_sats/2)*(s2>=num_sats/2)):
                # same hemisphere
                # implement condition 8
                ret = horizontal_hop(p1, s1, p2, s2, path_de)
                path_de.primary = ret[0]
                print(ret)
                path_de.secondary = ret[1]
                pass
            else:
                # diff hemispheres
                # go polar
                print("different hemis")
                path_de.primary = [0, path_de.dv]
                if(path_de.dh):
                    path_de.secondary = [path_de.dh, 0]
        return path_de
# integrate with constellation 
# add 4 buffers to satellites
failures = []
#testing routing
for j in range(10000):
    np.random.seed(j)
    plot_constellation(sats, dir_sats, j)
    p1, p2 = np.random.randint(0, P, 2)
    s1, s2 = np.random.randint(0, num_sats, 2)
    # p1 = 6
    # p2 = 6
    # s1 = 22
    # s2 = 16
    lat_1 = s_to_lat(s1)
    lat_2 = s_to_lat(s2)
    long_1 = ps_to_long(p1, s1)
    long_2 = ps_to_long(p2, s2)
    print(f"Start ({p1} , {s1}) -> ({p2}, {s2})")
    print(f"Source lat : {lat_1:.2f}, Source long : {long_1:.2f}\nDestination lat : {lat_2:.2f}, Destination long : {long_2:.2f}")
    #ret = direction_enhancement(p1, s1, p2, s2, 'dra')
    #print(ret) 
    print(f"testing ({p1} , {s1}) -> ({p2}, {s2})")
    pkt = packet(p1, s1, p2, s2, 0)
    i=0
    nodes_list = []
    nodes_list.append([p1, s1])
    while(pkt.p1 != p2 or pkt.s1 != s2):
        print("Packet to be forwarded")
        print(pkt)
        path_enhanced = direction_enhancement(pkt.p1, pkt.s1, pkt.p2, pkt.s2, 'dra')
        print("----")
        print(path_enhanced)
        if(path_enhanced.primary[0]):
            old_p = pkt.p1
            new_p = old_p+path_enhanced.primary[0]
            new_p = (new_p+P)%P
            if((old_p == 0 and new_p == P-1) or (old_p == P-1 and new_p == 0)):
                pkt.s1 = num_sats - pkt.s1
            pkt.p1 = new_p
            pkt.hops +=1
        else:
            pkt.s1 -= path_enhanced.primary[1]
            pkt.s1 = (pkt.s1 + num_sats)%num_sats
            pkt.hops +=1
        if(pkt.hops>50):
            print("*"*10)
            print("Alert")
            print("*"*10)
            failures.append(j)
            break
        node = [pkt.p1, pkt.s1]
        nodes_list.append(node)
    # plot_path(nodes_list, num=j)
    # plt.title(f"({p1}, {s1})->({p2}, {s2}), {pkt.hops} hops")
    # plt.legend(bbox_to_anchor=(0.75,1.25), loc="upper left")
    # plt.savefig(f"images/new_path_routed_{j}.png")
    print(nodes_list)
    print(f"Seed={j}")
print(f"Failures = {failures}")

# Routing works!!

    