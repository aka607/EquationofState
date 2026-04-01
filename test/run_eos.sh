#!/bin/bash
#SBATCH --job-name=run_eos
#SBATCH --account=def-ctetsass       # Replace with your actual allocation
#SBATCH --ntasks=32         # Or 40 for Narval
#SBATCH --mem-per-cpu=4000M
#SBATCH --time=6:00:00              # hh:mm:ss
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=abkatai@uwaterloo.ca  # Your email

# === Load LAMMPs and VASP modules ===
module load StdEnv/2023  gcc/12.3  openmpi/4.1.5
module load mpi4py/4.0.3
module load StdEnv/2023  intel/2023.2.1  intelmpi/2021.9.0 vasp/6.5.0

# === Activate the python enviornment ==
source ~/envs/vasp_tools/bin/activate

# === Set Python Enviornment Path ===
export PYTHONPATH=/home/abkatai/.local/lib/python3.11/site-packages:$PYTHONPATH
export LD_LIBRARY_PATH=/home/abkatai/.local/lib/python3.11/site-packages/lammps:$LD_LIBRARY_PATH

# === Run vasp ===
python -c "from mpi4py import MPI; print(MPI.Get_version())"
python run_eos.py


