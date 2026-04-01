import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt

import ase
from ase.io import read, write 
from ase import Atom

import warnings
import numpy as np
from ase.units import kJ



import numpy as np
from scipy.optimize import curve_fit

def parabola(x, a, b, c):
    """parabola polynomial function

    this function is used to fit the data to get good guesses for
    the equation of state fits

    a 4th order polynomial fit to get good guesses for
    was not a good idea because for noisy data the fit is too wiggly
    2nd order seems to be sufficient, and guarantees a single minimum"""

    return a + b * x + c * x**2


def murnaghan(V, E0, B0, BP, V0):
    'From PRB 28,5480 (1983'
    E = E0 + B0 * V / BP * (((V0 / V)**BP) / (BP - 1) + 1) - V0 * B0 / (BP - 1)
    return E


def vinet(V, E0, B0, BP, V0):
    'Vinet equation from PRB 70, 224107'

    eta = (V / V0)**(1 / 3)

    E = (E0 + 2 * B0 * V0 / (BP - 1)**2 *
         (2 - (5 + 3 * BP * (eta - 1) - 3 * eta) *
          np.exp(-3 * (BP - 1) * (eta - 1) / 2)))
    return E


class EquationOfState:
    def __init__(self, volumes, energies, eos='murnaghan'):
        self.v = np.array(volumes)
        self.e = np.array(energies)

        self.eos_string = eos
        self.v0 = None
        
        
    def fitted_energies(self, warn=True):
        self.func = globals()[self.eos_string]   # search for global function called eos_string

        # Initial guess for fitting parameters
        p0 = [min(self.e), 1, 1]
        popt, pcov = curve_fit(parabola, self.v, self.e, p0) 
             
        parabola_parameters = popt    # Here we get initial guesses for a, b and c from parabola 
        # Here I just make sure the minimum is bracketed by the volumes
        # this if for the solver
        minvol = min(self.v)
        maxvol = max(self.v)

        # the minimum of the parabola is at dE/dV = 0, or 2 * c V +b =0
        c = parabola_parameters[2]
        b = parabola_parameters[1]
        a = parabola_parameters[0]
        parabola_vmin = -b / 2 / c     # This is the guess min. volume 

        # evaluate the parabola at the minimum to estimate the groundstate
        # energy
        E0 = parabola(parabola_vmin, a, b, c)
        # estimate the bulk modulus from Vo * E''.  E'' = 2 * c
        B0 = 2 * c * parabola_vmin

        # evaluate the parabola at the minimum to estimate the groundstate
        # energy
        E0 = parabola(parabola_vmin, a, b, c)
        # estimate the bulk modulus from Vo * E''.  E'' = 2 * c
        B0 = 2 * c * parabola_vmin
        BP = 4

        initial_guess = [E0, B0, BP, parabola_vmin]

        # now fit the equation of state
        p0 = initial_guess
        popt, pcov = curve_fit(self.func, self.v, self.e, p0)
        self.eos_parameters = popt

        self.v0 = self.eos_parameters[3]
        self.e0 = self.eos_parameters[0]
        self.B = self.eos_parameters[1]
        self.BP = self.eos_parameters[2]

        if warn and not (minvol < self.v0 < maxvol):
            warnings.warn(
            'The minimum volume of your fit is not in '
            'your volumes.  You may not have a minimum in your dataset!')

        return self.v0, self.e0, self.B, self.BP

    def getplotdata(self):
        if self.v0 is None:
            self.fitted_energies()

        x = np.linspace(min(self.v), max(self.v), 100)     #Note that this INCREASES the number of points to plot compared to experimental data 
        y = self.func(x, *self.eos_parameters)

        return self.eos_string, self.e0, self.v0, self.B, x, y, self.v, self.e
    
    def plot(self, directory):
        eos_string, e0, v0, B, x, y, v, e = self.getplotdata()
        # plot
        # alter the font size 
        plt.rcParams['font.size'] = 12
        fig, ax = plt.subplots(figsize=(8, 6))
        
        ax.plot(x, y, ls='-', color='C3', label="EOS")  # By default red line
        ax.plot(v, e, ls='', marker='o', mec='C0', mfc='C0', label="Simulation Data")  # By default blue marker
        
        ax.set_xlabel('Volume [Å$^3$]')
        ax.set_ylabel('Total Energy [eV]')
        ax.set_title('%s: E0: %.1f eV, V0: %.1f Å$^3$, B: %.0f GPa' %
                     (eos_string, e0, v0,
                      B / kJ * 1.e24))
        ax.legend()
        plt.savefig(f'{directory}/EOS.png')

        a = v0 ** (1/3)
        return e0, v0, a, B / kJ * 1.e24
