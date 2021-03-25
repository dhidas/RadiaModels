import sys
import pickle
import matplotlib.pyplot as plt

# name from input
pickle_name = sys.argv[1]

# unpickle the data
variable, value_vs_beff = pickle.load(open(pickle_name, 'rb'))

# Grab values of interest
values = [data['value'] for data in value_vs_beff]
ByEffMag0 = [data['ByEffMag0'] for data in value_vs_beff]
ByEffMagP = [data['ByEffMagP'] for data in value_vs_beff]

# Find the max Beff
mymax = max(ByEffMag0)
myidx = ByEffMag0.index(mymax)

# Print all arguments used for max Beff
infos = value_vs_beff[myidx]['ivu18args']
for key in infos:
    print('    \'' + key + '\':', str(infos[key]) + ',')

print('\nParameter varied:', variable, '\n')
print(f'beff max is {mymax:.3f} at {values[myidx]:.3f}')

period = value_vs_beff[0]['ivu18args']['period']
print(f'Keff mas is {0.09336*mymax*period:.3f}')

plt.figure()
plt.title('$B_{eff}$ vs ' + variable)
plt.ylabel('$B_{eff}$ (T)')
plt.xlabel(variable)
plt.plot(values, ByEffMag0, label='Beff0')
plt.plot(values, ByEffMagP, label='Beff+')
plt.axvline(values[myidx], label=f'Beff Max {mymax:.3f} at {values[myidx]:.3f}')
plt.legend()
plt.show()

