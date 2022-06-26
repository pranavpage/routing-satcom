# Simulator for testing algorithms
# Discrete Event Simulator
#from sat_network import orbital_plane, satellite
import numpy as np
alt = 600e3
P = 12
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
class node:
    def __init__(self, p, s):
        self.p = p
        self.s = s
        self.queue = []
        self.longitude = 180*p/P
        self.polar_angle = 360*s/num_sats
    def __repr__(self):
        return f"({self.p}, {self.s}, {len(self.queue)} packets)\n"
    
    def route(self, packet, algo_type='test'):
        # Calculate next hop for the packet
        # Load traffic info into packet header
        if(algo_type=='test'):
            packet.next_hop_p = self.p+1
            packet.next_hop_s = self.s+1
        elif(algo_type=='dra'):
            pass        
        return packet
class packet:
    def __init__(self, p1, s1, p2, s2, t):
        self.p1 = p1 
        self.s1 = s1 
        self.p2 = p2 
        self.s2 = s2
        self.hops = 0
        self.next_hop_p = p1
        self.next_hop_s = s1
        self.t_origin = t
    def __repr__(self):
        return f"({self.p1} , {self.s1}) -> ({self.p2}, {self.s2}), hops = {self.hops}\n"
    
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
        return f"Event {self.event_type} at time {self.t_exec}, node ({self.packet.p1}, {self.packet.s1})->({self.packet.p2}, {self.packet.s2}), next hop ({self.packet.next_hop_p}, {self.packet.next_hop_s})\n"
    def execute(self):
        '''Executed when it's the earliest event in the queue'''
        # Check event type
        global t
        t = self.t_exec
        if(self.event_type=='arrival'):
            # Routes the packet onto next hop 
            self.packet.p1 = self.packet.next_hop_p
            self.packet.s1 = self.packet.next_hop_s
            source_node = nodes[self.packet.p1*num_sats+self.packet.s1]
            if(not (self.packet.s1 == self.packet.s2 and self.packet.p1 == self.packet.p2)):
                self.packet = source_node.route(self.packet)
                # Schedules the packet for transmission, according to queue
                t_transmit = self.t_exec + len(source_node.queue)*transmit_delay # TBD : gives the queue length at the node 
                # Creates event
                event_queue.append(event(t_transmit, self.packet, 'departure'))
                source_node.queue.append(self.packet)
            else:
                pass
                # popping must be taken care of outside
            # TBD : extract traffic info from header and store in node
        elif(self.event_type=='departure'):
            # Sends the packet onto next hop
            # Generates an arrival event for the next hop node 
            # Need to find propagation delay between two nodes
            source_node = nodes[self.packet.p1*num_sats+self.packet.s1]
            prop_delay = propagation_delay(self.packet.p1, self.packet.s1, self.packet.next_hop_p, self.packet.next_hop_p) # TBD
            t_arrival = self.t_exec + 1*transmit_delay + prop_delay
            event_queue.append(event(t_arrival, self.packet, 'arrival'))
            source_node.queue.pop(0)
        else: 
            return -1
        print(self)
        return 
    
def initialize_constellation(alt, P, num_sats, inclination = 90):
    nodes = []
    for p in range(P):
        for s in range(num_sats):
            nodes.append(node(p, s))
    return nodes
def propagation_delay(p1, s1, p2, s2):
    return 5
def event_handler():
    t_exec_array = np.array([evnt.t_exec for evnt in event_queue])
    next_idx = np.argmin(t_exec_array)
    evnt = event_queue.pop(next_idx)
    evnt.execute()
    return
# def gen_pkts():
#     rates = [1]
nodes = initialize_constellation(alt, P, num_sats)
for t_arrival in [1.2, 1.4, 1.7]:
    pkt = packet(1, 2, 3, 4, 0)
    evnt = event(t_arrival, pkt, 'arrival')
    event_queue.append(evnt)
    event_handler()

while(event_queue):
    event_handler()
