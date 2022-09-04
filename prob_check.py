# Script to check behaviour of functions governing whether to go along primary/secondary directions
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 12})
def f_prob(a,b,p):
    return p*b/(a + (b-a)*p)
num_points = 25
a = np.arange(1,num_points+1)
b = np.arange(1,num_points+1)
p = 0.8
arr = np.zeros((num_points,num_points))
av, bv = np.meshgrid(a, b, indexing='ij')
arr = f_prob(av, bv, p)
plt.pcolormesh(arr, cmap='gray')
plt.colorbar()
plt.xlabel("$c_p$", fontsize=16)
plt.ylabel("$c_s$", fontsize=16)
plt.savefig("Paper/images/heatmap.png")
# for i in range(num_points):
#     for j in range(num_points):
#         print(f"a={av[i,j]}, b={bv[i,j]}, P(primary) = {f_prob(av[i,j], bv[i,j], p):.3f}, arr[i,j]={arr[i,j]:0.3f}")