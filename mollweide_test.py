# testing mollweide projection 
from matplotlib import pyplot as plt
import numpy as np
fig = plt.figure()
# plt.subplot(111, projection="mollweide")
# x = np.array([-np.radians(120), 0, np.radians(120)])
# y = np.array([0, np.radians(30), 0])
# plt.plot(x, y, ',')
# plt.scatter(x, y, marker=',')
# plt.grid()
# plt.show()
num_sats = 24
P = 12
plane_idx = np.arange(0, P)
sat_idx = np.zeros_like(plane_idx)
sat_idx[:] = 16
def ps_to_long(p, s):
    polar_angle = 360.0*s/num_sats
    if(polar_angle>180):
        # diff hemisphere
        longitude = (p*180.0/P) - 180
    else:
        longitude = (p*180.0/P)
    return longitude
long = [ps_to_long(plane_idx[i], sat_idx[i]) for i in range(len(sat_idx))]
plt.plot(plane_idx, long, '-o')
plt.grid()
plt.show()

