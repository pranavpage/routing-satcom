# Simulator for testing algorithms
# Discrete Event Simulator

event_queue = []
transmit_delay = 1
class packet:
    def __init__(self, p1, s1, p2, s2, t):
        self.p1 = p1 
        self.s1 = s1 
        self.p2 = p2 
        self.s2 = s2
        self.hops = 0
        self.next_hop_p = -1
        self.next_hop_s = -1
        self.t_origin = t
    def __repr__(self):
        return f"({self.p1} , {self.s1}) -> ({self.p2}, {self.s2}), hops = {self.hops}"
    
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
    
    def execute(self):
        '''Executed when it's the earliest event in the queue'''
        # Check event type
        if(self.event_type=='arrival'):
            # Routes the packet onto next hop 
            packet.route() # TBD
            # Schedules the packet for transmission, according to queue
            t_transmit = t_exec + packet.queue_length()*transmit_delay # TBD : gives the queue length at the node 
            # Creates event
            event_queue.append(event(t_transmit, packet, 'departure'))
            # popping must be taken care of outside
            # TBD : extract traffic info from header and store in node
        elif(self.event_type=='departure'):
            # Sends the packet onto next hop
            # Generates an arrival event for the next hop node 
            # Need to find propagation delay between two nodes
            prop_delay = packet.propagation_delay() # TBD
            t_arrival = t_exec + 1*transmit_delay + prop_delay
            event_queue.append(event(t_arrival, packet, 'departure'))
        else: 
            return -1
               
