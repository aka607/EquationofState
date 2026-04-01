from ase import build
from ase.io import read, write
from ase.visualize import view
import numpy as np
import os

from ase.calculators.lammpslib import LAMMPSlib

from mpi4py import MPI
from lammps import lammps

from ase.calculators.vasp import Vasp

from EOS_add_legend import *

# magmom database. Stores the magnetic moment for a given element. 
magmom = {'Mo': 5, 'V': 5, 'Nb': 0.6, 'Ta': 0.6, 'W': 5}


class Elemental_Bulk:
    '''
    Fields:
        symbol (Str),
        lattice_constant (Float)
        phase (Str)
    '''
    def __init__(self, symbol, phase, lattice_constant):
       '''
       Constructor: Create an Elemental_Bulk object by calling Elemental_Bulk(symbol, phase, lattice_constant). 

        Effect: mutates self 

        __init__: Elemental_Bulk(Str, Float, Str) -> None 
        Requires:
              - symbol must be a valid element from the periodic table 
              - phase can only be one of the cubic crystal structures - 'sc', 'bcc' or 'fcc' - where 'sc' represents 'simple cubic'
              - lattice_constant > 0 

        Elemental_Bulk('Nb', 'bcc', 3.3006) -> None 
        '''
       self.symbol = symbol
       self.phase = phase
       self.lattice_constant = lattice_constant


    def __repr__(self):
        '''
        Returns a string representation of self.

        __rep__: Elemental_Bulk -> Str 
        '''
        s = "Symbol: {0.symbol}; Lattice Constant (Å); {0.lattice_constant}; Crystal structure: {0.phase}"
        return s.format(self)
    
    def plot_eos(self, main_path, lower_bounds=0.80, upper_bounds=1.20, num_cells=40, sim_package='vasp'):
       '''
       Generates a plot for the Equation of State (EOS) for the conventional unit cell of Elemental_Bulk. The EOS model is fitted to static energy calculations performed on a series of unit cells (num_cells)
       with fixed volumes ranging from V0 * lower_bounds to V0 * upper_bounds. V0 represents the "estimated" equilibrium volume determined from self.lattice_constant. The calculated properties from the EOS, 
       including lattice constant and bulk modulus, are written to a file called eos_data.csv located in main_path. 

       prepare_eos(Elemental_Bulk, Str, Float, Float, Nat, Str) -> None

       Requires:
              - symbol must be a valid element from the periodic table 
              - lattice_constant > 0 
              - phase can only be one of the cubic crystal structures - 'sc', 'bcc' or 'fcc' - where 'sc' represents 'simple cubic'
       '''
       eos_data = open(f'{main_path}/eos_data.csv', 'w')

       bulk = build.bulk(self.symbol, self.phase, self.lattice_constant, cubic=True)
       
       if sim_package == 'vasp':
              for atom in bulk:
                     atom.magmom = magmom[self.symbol]



       directory = f'{main_path}/{self.symbol}'
       # Checks if the directory exists. If it does, does not create new folder. If it doesn't, new folder is created. 
       if not os.path.exists(directory):
              os.makedirs(directory)
              print(f"Directory '{directory}' created.")
       else:
              print(f"Directory '{directory}' already exists.")


       # Write the ElementalBulk structure with the estimated equilibrium volume. 
       bulk.write(filename=f'{directory}/bulk.vasp', format='vasp')
            
       cell = bulk.get_cell()
       arr1 = np.empty((num_cells, 2))

       for n, x in enumerate(np.linspace(lower_bounds, upper_bounds, num_cells)):
              # Create the sub-directory for the given volume number in increasing order. 
              subdirectory = f'{directory}/{n+1}'

              # Checks if a directory exists. If it does, does not create new folder. If it doesn't, new folder is created. 
              if not os.path.exists(subdirectory):
                     os.makedirs(subdirectory)
                     print(f"Directory '{subdirectory}' created.")
              else:
                     print(f"Directory '{subdirectory}' already exists.")

              # Now write the lammps data file for the given volume. 
              bulk.set_cell(cell * x, scale_atoms=True)
              arr1[n][0] = bulk.get_volume()

              # might have to set lreal to False 
              if sim_package == 'vasp':
                     calc = Vasp(restart=False, directory=f'{subdirectory}', label=f'{self.symbol}_{n+1}_eos', txt='vasp.out', xc='pbe', kpts=(10, 10, 10), gamma=True, \
                            encut=400, prec='Accurate', ivdw=11, ediff=1E-6, ispin=2, lnoncollinear=False, ismear=1, sigma=0.2, nelm=200)
                     print(calc)
              else:
                     # default dimension 3, peridic in x-, y- and z- and atomic_style
                     cmds = ['pair_style tabgap', f'pair_coeff * * Mo-Nb-Ta-V-W.tabgap {self.symbol} yes yes']
                     calc = LAMMPSlib(lmpcmds=cmds, keep_alive=True, log_file=f'{subdirectory}/log.lammps')
              
              bulk.calc = calc

              arr1[n][1] = bulk.get_potential_energy()
              print(f'Potential energy of {self.symbol} at volume {arr1[n][0]} is {arr1[n][1]}')  # Run the calculation

       V, E = arr1[:, 0], arr1[:, 1]

       eos = EquationOfState(V, E)
       e0, v0, calc_a, B = eos.plot(directory)
       eos_data.write(f'{self.symbol},{e0:.3f},{v0:.3f},{calc_a:3f},{B:2f}\n')

       


              
 
