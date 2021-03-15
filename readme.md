# Leonhard and Euler Guide

- [Leonhard and Euler Guide](#leonhard-and-euler-guide)
  - [Preliminary](#preliminary)
    - [Resources](#resources)
    - [Connecting to the cluster](#connecting-to-the-cluster)
  - [Modules](#modules)
  - [Python](#python)
    - [Using the pre-compiled binaries](#using-the-pre-compiled-binaries)
    - [Setup Miniconda](#setup-miniconda)
    - [Creating Conda Environment](#creating-conda-environment)
    - [Test your Python Installation](#test-your-python-installation)
  - [Using Jupyter Notebook for Visualizing Results](#using-jupyter-notebook-for-visualizing-results)
  - [Storing Data](#storing-data)
    - [General Procedure](#general-procedure)
    - [Implementation Commands](#implementation-commands)
      - [**Taring** a folder without compression](#taring-a-folder-without-compression)
      - [**Copying** a **folder from local computer** to the cluster](#copying-a-folder-from-local-computer-to-the-cluster)
      - [**Copying** a **folder** **from cluster** to yor local computer](#copying-a-folder-from-cluster-to-yor-local-computer)
      - [**Untaring** the tar file to the local storage of a node](#untaring-the-tar-file-to-the-local-storage-of-a-node)
      - [Accessing locale scratch directory in python](#accessing-locale-scratch-directory-in-python)
    - [Performance](#performance)
  - [Scheduling Jobs](#scheduling-jobs)
    - [Interactive jobs](#interactive-jobs)
    - [Monitoring Jobs](#monitoring-jobs)
    - [Scheduling Python-Job Manual](#scheduling-python-job-manual)
    - [Python Debugging Tipps](#python-debugging-tipps)
    - [Template Environment](#template-environment)
  - [Template Project Overview](#template-project-overview)
  - [Setting up Environment Variables on the cluster](#setting-up-environment-variables-on-the-cluster)
  - [Using Ansible](#using-ansible)
    - [Installation](#installation)
    - [Configure](#configure)
    - [Testing the settings](#testing-the-settings)
    - [Scheduling Jobs Using Playbooks](#scheduling-jobs-using-playbooks)

## Preliminary

### Resources
Read the Leohard/Euler cluster guides:
[Getting_started_with_clusters](https://scicomp.ethz.ch/wiki/Getting_started_with_clusters)


### Connecting to the cluster
For this you can follow the guide on the official cluster web-side which shows you how to generate and copy your local ssh key to the cluster.

Steps in short:
1. Connect to the ETH network via VPN CiscoAnyConnect is highly recommended. (most stable)
2. Generate your local ssh key. 
3. Copy your local ssh key to the cluster by running:
```
cat ~/.ssh/id_rsa.pub | ssh username@login.leonhard.ethz.ch "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >>  ~/.ssh/authorized_keys"
```
Here we assume your created your ssh key at '~/.ssh/id_rsa.pub' on your locale machine. 

4. Try to connect.
'ssh username@login.leonhard.ethz.ch'


## Modules
When you connect to the cluster you connect to a login node.
There exists a variety of modules pre-installed. 

(https://scicomp.ethz.ch/wiki/Leonhard_applications_and_libraries)


You can list the currently loaded modules with:
```
module list
```

When you want to develop something in Python you can either use precompiled binaries by loading the correct python module
```
module load gcc/6.3.0 python_gpu/3.7.4 cuda/10.1.243
module load gcc/6.3.0 python_gpu/3.8.5 cuda/11.0.3
```
or create your own Python installation.

The job execution nodes are not directly connected to the internet, but you can access the internet by loading the proxy module.
```
module load eth_proxy
```


## Python
### Using the pre-compiled binaries
You can take a look into the provided pre-compiled python bianaries here:
https://scicomp.ethz.ch/wiki/Python_on_Euler


As a preliminary the scicomp wesite is often not up-to-date!

In general we recommend setting up miniconda to mange your python environment.
This allows to fully match the cluster and your locale setup.

### Setup Miniconda
Using anaconda to setup a custom python environments.
(https://docs.conda.io/en/latest/miniconda.html)

To install miniconda:
1. Connect to the cluster
2. Navigate to $HOME 
3. Run the following:
```
cd ~ && wget https://repo.anaconda.com/miniconda/
chmod +x ./Miniconda3-latest-Linux-x86_64.sh
./Miniconda3-latest-Linux-x86_64.sh 
```

In gerneral:

It is important to install the conda environment (which will contain a lot of small files), to your $HOME folder (/cluster/home/username/miniconda3). This directory will always before running a job be copied to the compute node. Your home folder is quite small < 15GB but perfect for storing your code and the python environments.

4. Source the .bashrc file or open a new shell.
```
source ~/.bashrc
```
5. Verfy your installation:
You should now see the currently loaded conda environments in brackets before your username. `(base) [username@login-noden ~]$`


### Creating Conda Environment
Follow this guide on how to setup a new environment.
When using GPUs make sure to match the CUDA Version.
You can load different CUDA-Versions with module load. 
Also be aware of the GCC Version.
We recommended to use GCC version 6.3.0 and CUDA 11.0.


[Guide how to ,manage conda environments](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)

Exectute the following command to create your Python environment named myenv (you can change the name):
```
conda create -n myenv python=3.8.5
conda activate myenv
```

Install some packages:  
Example PyTorch Installation (Here its important to match the cudatoolkit version!):
```bash
conda install pytorch==1.7.1  \ 
    torchvision==0.8.2 \
    torchaudio==0.7.2 \
    cudatoolkit=11.0 -c pytorch
```

### Test your Python Installation
1. At first check your python path:
Command:
```bash
which python 
```
Result:
```bash 
/cluster/home/username/miniconda3/envs/myenv/bin/python
```

If an other path is given try to execute `conda deactivate`.
Reactivate your environment: `conda activate myenv`

1. Open an interactive python shell:
```bash
python
```

```python
import torch
torch.__version__
```
To check that you have installed the correct pytorch version.
Exit the shell with `exit()`



## Using Jupyter Notebook for Visualizing Results
[Jupyter_on_Euler_and_Leonhard_Open](https://scicomp.ethz.ch/wiki/Jupyter_on_Euler_and_Leonhard_Open)


## Storing Data
### General Procedure
Its important to manage your data storage correctly on the cluster.
All large datasets should be stored under the `/cluster/work/riner` folder.  
Also if your experiment results are large store them under the `/cluster/work/riner` aswell.

Its important to not store small files. When you need to train your model on a large dataset the workflow is the following.
1. Tar the dataset folder without compression!
2. Schedule the job and request SCRATCH storage (will be discussed in the job-section)
3. Untar the dataset to the SCRATCH pariton of the compute node ($TMPDIR). The SCRATCH partiton is mounted under $TMPDIR
4. Now you can access the small files individually very fast given that they are on the SSD directly on the compute node and no network transfer is needed.

If you dont follow this procedure and try to access a lot of small files on a network storage (/cluster/work/riner) you will slow down the network and your bandwidth will be massively reduced when you hit a certain file number limit.


### Implementation Commands

#### **Taring** a folder without compression
```
cd directory/containing/datasets
tar -cvf dataset.tar dataset_folder
```

#### **Copying** a **folder from local computer** to the cluster
Open a shell on your local computer
```
scp -r ./path/to/local_folder username@login.leonhard.ethz.ch:/cluster/work/riner/some_folder
```
#### **Copying** a **folder** **from cluster** to yor local computer
Oopen a shell on your local computer
```
scp -r username@login.leonhard.ethz.ch:/cluster/work/riner/results ./path/to/local_results 
```
#### **Untaring** the tar file to the local storage of a node
```
tar -xvf /cluster/work/riner/datasets.tar -C $TMPDIR
```

#### Accessing locale scratch directory in python

Given that the TMPDIR variable is automatically set you can access the location of the dataset as follows:

```python
import os
tmpdir = os.getenv('TMPDIR)
os.system(f'tar \cluster\work\riner\yourtarfile -C {tmpdir}')
```

### Performance
Dont use a compression if you already have compressed files such as images stored as jpgs or pngs.  
HDF5 files are also handy to use.  
If your dataset is small you can consider to load all files into the RAM given that you can request huge amount of RAM.  


## Scheduling Jobs
Read the **Using the batch system** section. [Getting_started_with_clusters](https://scicomp.ethz.ch/wiki/Getting_started_with_clusters)

### Interactive jobs
At first let's start an interactive job running a shell.
```
bsub -n 16 -W 1:00 -R "rusage[mem=5000,ngpus_excl_p=2]" -R "select[gpu_mtotal0>=10000]" -R "rusage[scratch=10000]" -Is bash
```
This command will return an interactive bash session *(-Is)* with 16 cores *(-n 16)* that runs for 1 hour *(-W 1:00)* with 2 GPUS with more then 10GB of memory.
A total RAM of 16x5000MB and a total SSD Scratch of 10000x16MB.

We can run the following two commands to see the GPU utilization `nvidia-smi` and CPU usage `htop`.

You can now simply activate the correct conda environment and run your python code as on your local computer.
This is especially useful for debugging. If your code crashes it might happen that the terminal freezes and you have to submit a new interactive session.

If you know a workaround for this freezing problem I please share it!


### Monitoring Jobs
Jo can see the runing Jobs with `bjobs` or `bbjobs` for more details.

Jo can use the JOB-IDS to stop or peek the job.
```bash 
bkill JOB-ID           # Sends stop signal to the selected job
bkill 0                # Sends stop signal to ALL-jobs.
bpeek JOB-ID           # Prints STD OUT of the selected job to the terminal.
```

When you want the evaluate or debug certain problems its helpful to connect to the job-execution directly.
```
bjob_connect JOB-ID
```
You will see in brackets how the node changes from a login node to the execution node.

### Scheduling Python-Job Manual

To schedule a python job we will create shell-script `submit.sh`
Dont forget to set the correct permissions for exectution:
`chmod +x submit.sh`

```sh
# Always reload all-modules before execution for consitency.
module list &> /dev/null || source /cluster/apps/modules/init/bash
module purge
module load legacy new gcc/6.3.0 hdf5 eth_proxy

# Navigate to the folder containing your python project.
$HOME/my_project/
# Specify the conda version.
# $@ allows you to pass arguments to the python file
$HOME/miniconda3/envs/myenv/bin/python main.py $@   
```

Scheduling the Job:
```bash
bsub -I -n 4 -W 1:00 -R "rusage[mem=5000]" $HOME/run.sh --env=hello --exp=world
```

`main.py`
```python
import argparse
if __name__ == "__main__":
  parser = argparse.ArgumentParser()    
  parser.add_argument('--exp', help='Some flag.')
  parser.add_argument('--env', help='Other flag')
  args = parser.parse_args()
  print( args.exp, args.env )
```


### Python Debugging Tipps
When using interactive bash sessions and you would like to break the program using Ctrl-C without freezing the terminal it helps to explicitly catch the signal.  
By adding the following to the main script:
```
import signal

def signal_handler(signal, frame):
	print('exiting on CRTL-C')
	logger.experiment.stop()
	sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
```

### Template Environment
Tested on Leonhard and Euler.  
Machine learning and vision tasks.  
Python 3.8.5 & GCC/6.3.0  

Install:
```
conda env create -f .conda/py38.yml
```

FRAMEWORKS:
```yaml
- torch=1.7.1+cu110
- scikit-learn=0.24
- scipy=1.6.1
- numpy=1.19.2
- pandas=1.2.3
- pytorch-lightning=1.2.3
- opencv=4.5.1
```
UTILS:
```yaml
- imageio=2.9.0
- pillow=8.1.2
- torchvision=0.8.2+cu110
- h5py=h5py
- matplotlib=3.3.4
```

MONITORING:
```yaml
- neptune-client=0.5.1
- tensorboard=2.4.1
```


## Template Project Overview

## Setting up Environment Variables on the cluster
Append the following lins to the end of your ~/.bashrc file.
vi ~/.bashrc

```
export NEPTUNE_API_TOKEN="""torken"""
export ENV_WORKSTATION_NAME="""leonhard"""
```
Specify your neptune.ai key for debugging. (only necesarray if you want to use neptune)  
Specify the name of the cluster. This allows later to access this variable from your python script. Therfore your able to keep track on which cluster your on. Also this variable will be used to load the correct environment yaml file with the same name `/home/jonfrey/ASL_leonhard_euler/cfg/env/euler.yml` where you are able to specify cluster specific paths and settings.
This allows to easly move between your workstation and cluster.

## Using Ansible

### Installation
Follow the installing ansible on Ubuntu guide. 

(https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)

### Configure

Configure ansible settings by modifiying the following files.
1. ```sudo vi /etc/ansible/ansible.cfg```
```
[defaults]
remote_user=username
host_key_checking = False
sudo_flags=-H -S
private_key_file = /home/jonfrey/.ssh/id_rsa

[ssh_connection]
pipelining = True
```

2. ``` sudo vi /etc/ansible/hosts```
```
[leonhard]
login.leonhard.ethz.ch ansible_ssh_user=username

[euler]
euler.ethz.ch ansible_ssh_user=username
```

Replace the username with your ETH email abbreviation.

### Testing the settings

You should now be able to ping the configured hosts:
Command: 
```bash
sudo ansible all -m ping
```

Result:
```bash
euler.ethz.ch | SUCCESS => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python"
    }, 
    "changed": false, 
    "ping": "pong"
}
login.leonhard.ethz.ch | SUCCESS => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python"
    }, 
    "changed": false, 
    "ping": "pong"
}
```



###  Scheduling Jobs Using Playbooks

At first habe a look into the offical documentation
(https://docs.ansible.com/ansible/latest/user_guide/playbooks_intro.html)

Example Playbook `(ansible/queue_jobs.yml)`:
```yaml
---
- name: Schedule Experiments
  hosts: euler
  vars:
    - project_dir: "{{ ansible_env.HOME }}/"
  tasks:
    - name: Sync
      synchronize: 
        src: /home/jonfrey/ASL_leonhard_euler 
        dest: "{{ project_dir }}"

    - name: Load variables
      include_vars:
        file: /home/jonfrey/ASL_leonhard_euler/ansible/experiments.yml
        name: experiments
    
    - name: Schdule all experiments
      shell: >
          bsub -n 1 -W 0:10 -R "rusage[mem=5000,ngpus_excl_p=2]" -R "select[gpu_mtotal0>=10000]" -R "rusage[scratch=1000]" $HOME/ASL_leonhard_euler/scripts/submit.sh --exp={{ item.exp }}
      loop: "{{ experiments.jobs }}"

```
Playbook Explanation:
1. Specify the execution host:   
`hosts: euler`  
The available hosts can be found in the perviously setup `/etc/ansible/hosts` file
2. Synchronize your local code with the cluster:  
`synchronize`   
You can modify the `dest` and `src` path as needed.  
Also it's possible to use `rsync` instead here.  
1. Load variables:    
Loads the `ansible/experiments.yml` where paths to experiment files are listed.  
Each of the entries in the `jobs` list will be handled seperate.
We will loop over the jobs list in the next command.
4. Scheduling:  
Schedule the job with the bash command. Sets the correct exp-file-path for each experiment.
The `scripts/submit.sh` file loads the correct module. And starts the `main.py` with the template conda environment.
the arguments that are passed to the script (`--exp=`) will be passed to the main.py file.
With the loop command ansible knows it is supposed to loop over the list.  
`loop: "{{ experiments.jobs }}"`



Command:
```bash
sudo ansible-playbook ansible/queue_jobs.yml 
```

Result:

```bash
PLAY [Schedule Experiments] *********************************************************************************

TASK [Gathering Facts] **************************************************************************************
ok: [euler.ethz.ch]

TASK [Sync] *************************************************************************************************
changed: [euler.ethz.ch]

TASK [Load experiments] *************************************************************************************
ok: [euler.ethz.ch]

TASK [Schdule all experiments] ******************************************************************************
changed: [euler.ethz.ch] => (item={u'exp': u'/home/jonfrey/ASL_leonhard_euler/cfg/exp/exp.yml'})
changed: [euler.ethz.ch] => (item={u'exp': u'/home/jonfrey/ASL_leonhard_euler/cfg/exp/exp.yml'})

PLAY RECAP **************************************************************************************************
euler.ethz.ch              : ok=4    changed=2    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
```

```
(base) [jonfrey@eu-login-11 ~]$ bjobs
JOBID      USER    STAT  QUEUE      FROM_HOST   EXEC_HOST   JOB_NAME   SUBMIT_TIME
165381072  jonfrey PEND  gpu.4h     eu-login-21             *p/exp.yml Mar 15 07:00
165381081  jonfrey PEND  gpu.4h     eu-login-21             *p/exp.yml Mar 15 07:00
```


```
TODO:
- Workflow diagram
- Add my paramiko script
- Extend ansible to use -o correctly
```