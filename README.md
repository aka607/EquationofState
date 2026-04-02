This package uses the LAMMPS Python package (lammps) to run LAMMPs in parallel from Python by making MPI calls directly from Python. On a HPC cluster, it's better to load a prebuilt mp4py module if available (use module load).

Making LAMMPs usable within Python requires putting the LAMMPS Python package (lammps) into a location where the Python interpreter can find it and installing the LAMMPs shared library. 

To use this package, follow these instructions: 


1. Install the LAMMPs shared library. This is a dynamic version of the LAMMPs executable that can be loaded into Python: 

cd lammps/src && make mode=shared mpi

2. After compiling LAMMPs in shared mode:

make install-python


Instead of the above 2 steps, you can alternatively do:

cd lammps/src && make yes-python && make mode=shared mpi


3. Set the path to your python interpreter that has the LAMMPs Python package installed to it and the LAMMPs shared library path: 

    export PYTHONPATH=/home/abkatai/.local/lib/python3.11/site-packages:$PYTHONPATH
    export LD_LIBRARY_PATH=/home/abkatai/.local/lib/python3.11/site-packages/lammps:$LD_LIBRARY_PATH


To run a VASP calculation from ASE, you need to set the following environment variables in your .bashrc file:

    export VASP_PP_PATH=<path-to-pseudopotentials>
    export VASP_SCRIPT=<path-to-run_vasp.py>