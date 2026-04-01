from eos_setup import *

path = '/home/abkatai/scratch/eos'

Nb = Elemental_Bulk('Nb', 3.3006, 'bcc')
Mo = Elemental_Bulk('Mo', 2.90, 'bcc')
Ta = Elemental_Bulk('Ta', 3.15, 'bcc')
W = Elemental_Bulk('W', 2.95, 'bcc')
V = Elemental_Bulk('V', 2.75, 'bcc')

elemental_bulk_list = [Nb, Ta, Mo, W, V]

for e in elemental_bulk_list:
    e.plot_eos(f'{path}/lammps', sim_package='lammps')
    e.plot_eos(f'{path}/vasp', sim_package='vasp')
