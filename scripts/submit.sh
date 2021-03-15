# Loading correct modules
module list &> /dev/null || source /cluster/apps/modules/init/bash
module purge
module load legacy new gcc/6.3.0 hdf5 eth_proxy

# To export all environment variables
source ~/.bashrc
# Navigate to working directoy
cd $HOME/ASL_leonhard_euler
# Executing the script
/cluster/home/jonfrey/miniconda3/envs/py38/bin/python main.py $@
