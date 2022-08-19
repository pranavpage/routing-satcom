#main_script_simulation.py
# Combines des_simulator.py with the routing strategy developed in sat_network.py
# Discrete Event Simulator
import numpy as np
import matplotlib.pyplot as plt
alt = 600e3
P = 12
num_sats = 24
inclination = 90
R = 6.378e6
G = 6.674e-11
M = 5.972e24
c = 2.998e8
packet_size = 2**(10+3) #in bits
tx_rate = 5e7 # in bits/s
transmit_delay = packet_size/tx_rate
print(f"Packet size = {packet_size/8:.2e} bytes")
print(f"Transmit delay = {transmit_delay:.2e}")
polar_region_boundary = 75
theta_intra_plane = 360.0/num_sats
theta_inter_plane = 180.0/P
l_intra_plane = (R+alt)*np.sqrt(2*(1-np.cos(np.radians(theta_intra_plane))))
l_alpha = (R+alt)*np.sqrt(2*(1-np.cos(np.radians(theta_inter_plane))))
print(f"Propagation delay ~= {l_alpha/c:.2e} s")
print(f"t_prop/t_queue = {l_alpha/c/transmit_delay:.2f}")
s_min = np.floor((90 - polar_region_boundary)/theta_intra_plane)+1
# max_buff_length = int((l_alpha/c/transmit_delay))
max_buff_length = 40
# print(f"Number of orbital planes = {P}, sats per plane = {num_sats}")
# print(f"Inter plane angle : {theta_inter_plane:.2f}")
# print(f"Intra plane angle : {theta_intra_plane:.2f}")
# print(f"Polar Region bdry : {polar_region_boundary}")
event_queue = []
completed_packets = []
flow_packets = []
t = 0
algo_type = 'dra'
route_seed = 0
cc_arr = ['ekici', '3-average']
cc_type = cc_arr[0]
print(f"Congestion control type : {cc_type}")
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
lat_min = s_to_lat(s_min)
# print(f"Max latitude of ring : {lat_min:.2f}")
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
        if(nh>max(th_list) and nh>0):
            # print("cross polar region (condition 6)")
            return 1
        elif(nh>0):
            # print("don't cross polar region")
            return 0
        else:
            # print("nh==0")
            return 0
def horizontal_hop(p1, s1, p2, s2, path_de):
    # decision criterion for staying in horizontal ring or moving up/down
    # condition 8 in paper
    # print("Horizontal Hop func")
    lat_1 = s_to_lat(s1)
    # lat_2 = s_to_lat(s2)
    long_1 = ps_to_long(p1, s1)
    # long_2 = ps_to_long(p2, s2)
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
    # print("Run Min calc")
    # |lat_1| > |lat_2|
    # min hops to closest polar region 
    if(lat_1>=0):
        # go north
        max_hops = int(np.floor((polar_region_boundary - lat_1)*num_sats/360.0))
        # print(f"Hops to last satellite = {max_hops}")
        hops_list = np.arange(1, max_hops+1, 1)
        th_list = hops_list*(2*l_intra_plane/l_alpha)/(np.cos(np.radians(lat_1)) - np.cos(np.radians(lat_1 + hops_list*theta_intra_plane)))
        n_h = path_de.nh
        if(n_h < min(th_list) and n_h>0):
            # print("Same ring")
            # d_h = (+1)*(long_1<long_2) + (-1)*(long_1>long_2)
            # d_v = +1
            return [[path_de.dh, 0], [0, path_de.dv]]
        elif(n_h>0):
            # print("Go towards pole")
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
            # print("Same plane")
            return [[0, path_de.dv], [path_de.dh, 0]]
    else:
        # go south
        max_hops = int(np.floor(-(-polar_region_boundary - lat_1)*num_sats/360.0))
        # print(f"Hops to last satellite = {max_hops}")
        hops_list = np.arange(1, max_hops+1, 1)
        th_list = hops_list*(2*l_intra_plane/l_alpha)/(np.cos(np.radians(lat_1)) - np.cos(np.radians(lat_1 - hops_list*theta_intra_plane)))
        n_h = path_de.nh
        if(n_h < min(th_list) and n_h > 0):
            # print("Same ring")
            # d_h = (+1)*(long_1<long_2) + (-1)*(long_1>long_2)
            # d_v = -1
            return [[path_de.dh, 0], [0, path_de.dv]]
        elif(n_h>0):
            # print("Go towards pole")
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
            # print("Same plane")
            return [[0, path_de.dv], [path_de.dh, 0]]
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
        ph.dh = (-1)*(p1 < p2) + (+1)*(p1 >= p2)
        #differs from paper
        ph.dv = (+1)*((num_sats - 1 - s1) < s2) + (-1)*((num_sats - 1 - s1) >= s2)
        ph.nv = abs(num_sats-s1 - s2-1)
        ph.nh = -abs(p1 - p2) + P
        ph.hops = ph.nv + ph.nh
        
        if(s1 < num_sats/2 and s2 >= num_sats/2):
            #1 East, 2 West
            pv.dh = (+1)*(p1 < p2) + (-1)*(p1 > p2)
            pv.dv = (-1)*(2*(s2-s1) < num_sats) + (+1)*(2*(s2-s1) >= num_sats)
        elif(s1 >= num_sats/2 and s2 < num_sats/2):
            #1 West, 2 East
            pv.dh = (+1)*(p1 < p2) + (-1)*(p1 > p2)
            pv.dv = (+1)*(2*(s1-s2) < num_sats) + (-1)*(2*(s1-s2) >= num_sats)
        pv.nh = abs(p1 - p2)
        pv.nv = min(abs(s1-s2), num_sats - abs(s1-s2))
        pv.hops = pv.nv + pv.nh
    if(pv.hops == ph.hops):
        return ph
    elif(pv.hops == min(ph.hops, pv.hops)):
        return pv
    else:
        return ph
def direction_enhancement(p1, s1, p2, s2):
    path_de = direction_estimation(p1, s1, p2, s2)
    lat_1 = s_to_lat(s1)
    lat_2 = s_to_lat(s2)
    if(sat_in_polar_region(s1)):
        #hop in same plane
        # print("(1) polar")
        if(sat_in_polar_region(s2) and ((lat_1>0 and lat_2>0) or (lat_1<0 and lat_2<0))):
            # both in same polar region
            # print("same polar region")
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
        path_de.secondary = path_de.primary
    elif(sat_in_polar_region(s1+1) or sat_in_polar_region(s1-1)):
        # print("(2) last horizontal ring")
        if(path_de.dh):
            path_de.primary = [path_de.dh, 0]
            if(path_de.dv):
                path_de.secondary = [0, path_de.dv]
        else:
            path_de.primary = [0, path_de.dv]
    else:
        #condition on nh (6)
        # print("(3) Middle of the net")
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
            path_de.secondary = ret[1]
            pass
    # print(path_de)
    return path_de
def give_neighbours(p, s):
    # give the four neighbours of (p,s) in [[right, left], [up, down]] format
    neighbours = [[], []]
    # right 
    right_p = (p+1+P)%P
    right_s = s
    if((p==P-1 and right_p==0)):
        right_s = num_sats - s
    neighbours[0].append([right_p, right_s])
    # left
    left_p = (p-1+P)%P
    left_s = s
    if((p==0 and left_p==P-1)):
        left_s = num_sats - s
    neighbours[0].append([left_p, left_s])
    # up 
    up_s  = (s-1+num_sats)%num_sats
    neighbours[1].append([p, up_s])
    # down 
    down_s  = (s+1+num_sats)%num_sats
    neighbours[1].append([p, down_s])
    return neighbours
def congestion_control(node, path_enhanced, type=cc_type):
    '''
    (p1,s1) -> (p2, s2)
    node : Source node (with updated neighbouring_queue_lengths)
    path_enhanced : Path suggested by logical routing
    type : 'ekici' refers to basic buffer length threshold based avoidance
    '''
    # print(f"Max buffer length = {max_buff_length} packets")
    if(type == 'ekici'):
        node_idx = dir_to_node(path_enhanced.primary)
        # print(f"Node idx : {node_idx}")
        buff_length = len(node.buffers[node_idx[0]][node_idx[1]])
        # print(f"Buffer length = {buff_length}")
        if(buff_length<=max_buff_length):
            return path_enhanced.primary
        else:
            node_idx = dir_to_node(path_enhanced.secondary)
            # print(f"Secondary : {node_idx}, completed packets : {len(completed_packets)}", end='\r')
            if(node_idx):
                buff_length = len(node.buffers[node_idx[0]][node_idx[1]])
                # print(f"Buffer length = {buff_length}")
                if(buff_length<=max_buff_length):
                    return path_enhanced.secondary
                else:
                    return path_enhanced.primary
            else:
                return path_enhanced.primary
    if(type == '3-average'):
        node_idx = dir_to_node(path_enhanced.primary)
        buff_length = len(node.buffers[node_idx[0]][node_idx[1]])
        ngbr_buff_length = node.neighbour_queue_lengths[node_idx[0]][node_idx[1]]
        total_buff_length = buff_length
        if(ngbr_buff_length):
            total_buff_length += ngbr_buff_length
        if(total_buff_length<=max_buff_length):
            return path_enhanced.primary
        else:
            node_idx = dir_to_node(path_enhanced.secondary)
            # print(f"Secondary : {node_idx}, completed packets : {len(completed_packets)}", end='\r')
            if(node_idx):
                buff_length = len(node.buffers[node_idx[0]][node_idx[1]])
                ngbr_buff_length = node.neighbour_queue_lengths[node_idx[0]][node_idx[1]]
                total_buff_length = buff_length
                if(ngbr_buff_length):
                    total_buff_length += ngbr_buff_length
                if(total_buff_length<=max_buff_length):
                    return path_enhanced.secondary
                else:
                    return path_enhanced.primary
            else:
                return path_enhanced.primary
def dir_to_node(dir):
    # returns index of node corresponding to dir (as in path format)
    if(dir[0]):
        # horizontal direction
        if(dir[0]>0):
            # right 
            return [0,0]
        else:
            return [0,1]
    elif(dir[1]):
        # vertical
        if(dir[1]>0):
            return [1,0]
        else:
            return [1,1]
class node:
    def __init__(self, p, s):
        self.p = p
        self.s = s
        self.queue = []
        self.buffers = [[[], []], [[], []]]
        self.longitude = 180*p/P
        self.polar_angle = 360*s/num_sats
        self.queue_time = [[0,0]]
        self.average_queue_length = 0
        self.neighbour_queue_lengths = [[-1,-1],[-1,-1]] # [[right, left], [up, down]]
        self.neighbours = give_neighbours(p,s)
    def __repr__(self):
        return f"({self.p}, {self.s}, {len(self.queue)} packets)\n"
    def which_dir(self, p, s):
        # for i in range(2):
        #     for j in range(2):
        #         if(self.neighbours[i][j] == [p,s]):
        #             return [i,j]
        ret = [[i,j] for i in range(2) for j in range(2) if self.neighbours[i][j] == [p,s]]
        return ret[0]
    def give_buffer_lengths(self):
        arr = [[len(self.buffers[i][j]) for j in range(2)] for i in range(2)]
        return arr
    def route(self, packet, algo_type=algo_type):
        # Calculate next hop for the packet
        if(algo_type=='test'):
            packet.next_hop_p = self.p+1
            packet.next_hop_s = self.s+1
            packet.hops+=1
        elif(algo_type=='dra'):
            path_routed = direction_enhancement(self.p, self.s, packet.p2, packet.s2)
            path_enhanced = congestion_control(self, path_routed)
            # include congestion control here 
            # takes path_enhanced, packet.hdr, destination as input
            if(path_enhanced[0]):
                # Horizontal
                old_p = self.p
                new_p = old_p + path_enhanced[0]
                new_p = (new_p+P)%P
                if((old_p == 0 and new_p == P-1) or (old_p == P-1 and new_p == 0)):
                    packet.next_hop_s = num_sats - self.s
                packet.next_hop_p = new_p
                packet.hops+=1
                packet.prop_delay = l_alpha*np.cos(np.radians(s_to_lat(self.s)))/c
            else:
                # Vertical
                packet.next_hop_s = self.s- path_enhanced[1]
                packet.next_hop_s = (packet.next_hop_s + num_sats)%num_sats
                packet.hops +=1
                packet.prop_delay = l_intra_plane/c
            # print(f"Propagation delay = {packet.prop_delay:e}")
        return packet
class packet:
    def __init__(self, p1, s1, p2, s2, t, pkt_type = 'bkg'):
        self.p1 = p1 
        self.s1 = s1 
        self.p2 = p2 
        self.s2 = s2
        self.hops = 0
        self.next_hop_p = p1
        self.next_hop_s = s1
        self.t_origin = t
        self.prop_delay = 0
        self.delay = 0
        self.origin_p = p1
        self.origin_s = s1
        self.hdr = []
        self.pkt_type = pkt_type # 'bkg' vs 'flow'
    def __repr__(self):
        return f"Origin = {self.t_origin:.2e}, ({self.origin_p} , {self.origin_s}) -> ({self.p2}, {self.s2}), hops = {self.hops}, next hop = ({self.next_hop_p}, {self.next_hop_s})\n"
class event:
    def __init__(self, t_exec, packet, event_type):
        '''
        t_exec : Time of execution of event
        packet : Contains source, destination, next hop, header and data
        event_type : Arrival/departure event
        '''
        self.t_exec = t_exec
        self.packet = packet
        self.event_type = event_type
    def __repr__(self):
        return f"Event {self.event_type} at time {self.t_exec:e}, {self.packet}"
    def execute(self):
        '''Executed when it's the earliest event in the queue'''
        # Check event type
        # TBD : Change it to 4 output buffers
        global t
        t = self.t_exec
        if(self.event_type=='arrival'):
            # Routes the packet onto next hop 
            # print("ARRIVAL")
            self.packet.p1 = self.packet.next_hop_p
            self.packet.s1 = self.packet.next_hop_s
            source_node = nodes[self.packet.p1*num_sats+self.packet.s1]
            if(not (self.packet.s1 == self.packet.s2 and self.packet.p1 == self.packet.p2)):
                if(self.packet.hdr):
                    [metric, dir] = self.packet.hdr
                    source_node.neighbour_queue_lengths[dir[0]][(dir[1]+1)%2]=metric
                self.packet = source_node.route(self.packet)
                # print(source_node)
                # print(self.packet)
                # Schedules the packet for transmission, according to queue
                # print(source_node.neighbours)
                (i,j) = source_node.which_dir(self.packet.next_hop_p, self.packet.next_hop_s)
                source_node.buffers[i][j].append(self.packet)
                # source_node.queue.append(self.packet)
                # print("QUEUE LENGTHS")
                # print(source_node.neighbour_queue_lengths)
                buffer_lengths = source_node.give_buffer_lengths()
                # print(source_node)
                # print(buffer_lengths)
                source_node.queue_time.append([t, sum(np.array(buffer_lengths).flatten())])
                t_transmit = self.t_exec + len(source_node.buffers[i][j])*transmit_delay # TBD : gives the queue length at the node 
                # Creates event
                event_queue.append(event(t_transmit, self.packet, 'departure'))
                # print(source_node.queue)
            else:
                self.packet.delay = t - self.packet.t_origin
                completed_packets.append(self.packet)
                if(self.packet.pkt_type == 'flow'):
                    flow_packets.append(self.packet)
                    # print(f"Flow packets completed : {len(flow_packets)}", end='\r')
                # print(f"Completed Packets : {len(completed_packets)}, t={t:e}", end='\r')
                pass
                # popping must be taken care of outside
        elif(self.event_type=='departure'):
            # Sends the packet onto next hop
            # Generates an arrival event for the next hop node 
            # Need to find propagation delay between two nodes
            source_node = nodes[self.packet.p1*num_sats+self.packet.s1]
            # print("TRAFFIC INFO")
            metric, dir = traffic_info(source_node, self.packet)
            self.packet.hdr = [metric, dir]
            # print(self.packet.hdr)
            prop_delay = self.packet.prop_delay # TBD
            t_arrival = self.t_exec + 1*transmit_delay + prop_delay
            event_queue.append(event(t_arrival, self.packet, 'arrival'))
            # source_node.queue.pop(0)
            # print(source_node.neighbours)
            [i,j] = source_node.which_dir(self.packet.next_hop_p, self.packet.next_hop_s)
            source_node.buffers[i][j].pop(0)
            buffer_lengths = source_node.give_buffer_lengths()
            source_node.queue_time.append([t, sum(np.array(buffer_lengths).flatten())])
        else: 
            return -1
        # print(self)
        return 
def initialize_constellation(alt, P, num_sats, inclination = 90):
    nodes = []
    for p in range(P):
        for s in range(num_sats):
            nodes.append(node(p, s))
    return nodes
def event_handler():
    t_exec_array = np.array([evnt.t_exec for evnt in event_queue])
    next_idx = np.argmin(t_exec_array)
    evnt = event_queue.pop(next_idx)
    evnt.execute()
    return
def traffic_info(node, packet):
    # given a particular node and its 4 neighbours, generate a metric to send along with the packet
    neighbours = give_neighbours(node.p, node.s)
    dest = [packet.next_hop_p, packet.next_hop_s]
    weights = [[0,0],[0,0]]
    dir = [0,0]
    central_weights = [[1,1], [1,1]]
    metric = 0
    for i in range(2):
        for j in range(2):
            if(neighbours[i][j] == dest):
                dir = [i,j]
                pass
            else:
                # add to metric
                ql = node.neighbour_queue_lengths[i][j]
                val1 = ql*weights[i][j]
                val2 = len(node.buffers[i][j])*central_weights[i][j]
                metric+=val2
                if(ql>0):
                    metric += (val1)
    # metric += len(node.queue)*central_weight
    metric/=(sum(np.array(central_weights).flatten()) + sum(np.array(weights).flatten()))
    # if([node.p, node.s] == [2,9]):
    #     print(f"{node.p, node.s, node.neighbour_queue_lengths}, {packet.next_hop_p, packet.next_hop_s}, {metric}")
    return metric, dir
def plot_nodes(nodes):
    '''
        nodes : list of node objects
    '''
    polar_coords = np.array([[np.radians(ps_to_long(node.p, node.s)), np.radians(s_to_lat(node.s))] for node in nodes])
    ql = np.array([node.average_queue_length for node in nodes])
    fig2 = plt.figure(0)
    ax2 = fig2.gca(projection = 'mollweide')
    ax2.grid()
    ax2.scatter(polar_coords[:,0], polar_coords[:,1], s = (ql/max(ql))*10**2)
    return 0
# def gen_pkts():
#     rates = [1]
nodes = initialize_constellation(alt, P, num_sats)
lamda = 1e5 #packets/s 
print(f"Out rate = {tx_rate/packet_size*4:.2e} packets/s")
print(f"In rate = {lamda:.2e} packets/s")
# 15.625 supports 1Mbps for each pair
np.random.seed(route_seed)
num_sessions = 1
num_packets = int(1e2)
num_sources = int(2e2)
num_flow_packets = int(20)
feed_spacing = (num_packets/lamda)/2
t_arr = np.arange(0, num_sessions)*feed_spacing
p_min = 1
p_max = 6
s_min = 3
s_max = 10
def feed_queue(num_packets, t_feed):
    '''
        num_packets : number of pkts sent from source to dest
        t_feed : arrivals at t_feed + (arrival_times)
    '''
    event_feed = []
    # for node in nodes:
    #     [p1, s1] = [node.p, node.s]
    #     p2 = np.random.randint(0,P)
    #     s2 = np.random.randint(0,num_sats)
    #     # print(f"{p1,s1}->{p2,s2}")
    #     inter_arrival_times = np.random.exponential(1/lamda, num_packets)
    #     arrival_times = t_feed+np.cumsum(inter_arrival_times)
    #     for t_arrival in arrival_times:
    #         pkt = packet(p1, s1, p2, s2, t_arrival)
    #         evnt = event(t_arrival, pkt, 'arrival')
    #         event_feed.append(evnt)
    #         pkt = packet(p2, s2, p1, s1, t_arrival)
    #         evnt = event(t_arrival, pkt, 'arrival')
    #         event_feed.append(evnt)
    for i in range(num_sources):
        [p1, p2] = np.random.randint(p_min, p_max+1, 2)
        [s1, s2] = np.random.randint(s_min, s_max+1, 2)
        inter_arrival_times = np.random.exponential(1/lamda, num_packets)
        arrival_times = t_feed+np.cumsum(inter_arrival_times)
        for t_arrival in arrival_times:
            pkt = packet(p1, s1, p2, s2, t_arrival)
            evnt = event(t_arrival, pkt, 'arrival')
            event_feed.append(evnt)
    return event_feed
# print("#"*4 + "EVENT HANDLER" + "#"*4)
# one dedicated flow
# (p1, p2) = np.random.randint(0, P, 2)
# (s1, s2) = np.random.randint(0, num_sats, 2)
[p1,s1] = [2,9]
[p2,s2] = [5,2]
print(f"Dedicated flow : {p1,s1}->{p2,s2}, {num_flow_packets} packets")
t_start_flow = (1/lamda)*(num_packets)/3
# t_start_flow = 0
# t_start_flow = 1e-3
print(f"Start time : t = {t_start_flow:.3e}")
lamda_flow = 5e3
inter_arrival_times = np.random.exponential(1/lamda, num_flow_packets)
arrival_times = np.cumsum(inter_arrival_times) + t_start_flow
# print(arrival_times)
flow_feed = []
for t_arrival in arrival_times:
    pkt = packet(p1, s1, p2, s2, t_arrival, 'flow')
    evnt = event(t_arrival, pkt, 'arrival')
    flow_feed.append(evnt)
event_queue+=flow_feed
for i in range(num_sessions):
    t_current = t
    event_queue+=feed_queue(num_packets, t)
    print(f"Fed {num_sources*num_packets} packets at t={t}")
    while(event_queue):
        print(f"TIME : {t:.3e}, Events : {len(event_queue)}  ", end='\r')
        event_handler()
# for pkt in completed_packets:
#     print(f"{pkt.t_origin*1e3:.2f} ms, {pkt.delay*1e3:.2f} ms, ({pkt.origin_p}, {pkt.origin_s}) -> ({pkt.p2}, {pkt.s2})")
i = 0
for node in nodes:
    if(node.queue_time!=[[0,0]]):
        arr = np.array(node.queue_time)
        time = arr[:,0]
        queue_lengths = arr[:,1]
        inter_arr = time[1:] - time[:-1]
        node.average_queue_length = sum(inter_arr*queue_lengths[:-1])*1.0/t
        # if(i == 0 and max(queue_lengths)>=5):
        #     plt.figure(1)
        #     plt.plot(time, queue_lengths)
        #     plt.grid()
        #     plt.axvline(t_start_flow)
        #     plt.show()
        #     i+=1
        # print(f"Lat {s_to_lat(node.s):.2f}, Long {ps_to_long(node.p, node.s):.2f}, Queue {node.average_queue_length:.2f}")
        # print(f"{node.p, node.s}, Average queue length {node.average_queue_length:.3f}, max queue lengths : {max(queue_lengths)}")
        # print(arr)
print(f"Completed packets : {len(completed_packets)}")
# plot_nodes(nodes)
# plt.savefig("images/queue_lengths.png")
# plt.show()

avg_delay = np.array([pkt.delay for pkt in flow_packets])
t_min = arrival_times[0]
t_max = np.max(np.array([pkt.t_origin+pkt.delay]))
print(f"Mean delay : {np.mean(avg_delay)*1e3:.3f} ms, stddev : {np.std(avg_delay)*1e3:.3f} ms, num packets = {len(flow_packets)}")
print(f"Average throughput : {num_flow_packets*packet_size/(t_max - t_min):.3e} bps")