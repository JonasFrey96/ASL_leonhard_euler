import os
import sys 
sys.path.insert(0, os.getcwd())
sys.path.append(os.path.join(os.getcwd() + '/modules/'))

import argparse
import torch
import yaml
import datetime
from pytorch_lightning import Trainer
import shutil
from pathlib import Path

from datasets import RandomDataset
from lightning import BoringModel
from utils import load_yaml


if __name__ == '__main__':
  parser = argparse.ArgumentParser()    
  parser.add_argument('--exp', default='cfg/exp/exp.yml',
            help='The main experiment yaml file.')
  args = parser.parse_args()

  local_rank = int(os.environ.get('LOCAL_RANK', 0))

  # Load Experiment Setting and Environment File
  exp_cfg_path = args.exp
  if local_rank != 0:
    # if not main task load the modfied exp config file.
    # this allows to performe timestamps of the model folder
    rm = exp_cfg_path.find('cfg/exp/') + len('cfg/exp/')
    exp_cfg_path = os.path.join( exp_cfg_path[:rm],'tmp/',exp_cfg_path[rm:])
  exp = load_yaml(exp_cfg_path)

  env_cfg_path = os.path.join('cfg/env', os.environ['ENV_WORKSTATION_NAME']+ '.yml')
  env = load_yaml(env_cfg_path)

  # Create model folder (only for rank 0 ddp task) !
  if local_rank == 0 :
    # Set in name the correct model path
    if exp.get('timestamp',True):
      timestamp = datetime.datetime.now().replace(microsecond=0).isoformat()
      model_path = os.path.join(env['base'], exp['name'])
      p = model_path.split('/')
      model_path = os.path.join('/',*p[:-1] ,str(timestamp)+'_'+ p[-1] )
    else:
      model_path = os.path.join(env['base'], exp['name'])
    
    shutil.rmtree(model_path,ignore_errors=True)
    Path(model_path).mkdir(parents=True, exist_ok=True)

    exp_cfg_fn = os.path.split(exp_cfg_path)[-1]
    env_cfg_fn = os.path.split(env_cfg_path)[-1]
    print(f'Copy {env_cfg_path} to {model_path}/{exp_cfg_fn}')
    shutil.copy(exp_cfg_path, f'{model_path}/{exp_cfg_fn}')
    shutil.copy(env_cfg_path, f'{model_path}/{env_cfg_fn}')
    exp['name'] = model_path
  else:
    # the correct model path has already been written to the yaml file.
    model_path = os.path.join( exp['name'], f'rank_{local_rank}')
    # Create the directory
    Path(model_path).mkdir(parents=True, exist_ok=True)

  # Write back modified exp file
  if local_rank == 0:
    rm = exp_cfg_path.find('cfg/exp/') + len('cfg/exp/')
    exp_cfg_path = os.path.join( exp_cfg_path[:rm],'tmp/',exp_cfg_path[rm:])
    Path(exp_cfg_path).parent.mkdir(parents=True, exist_ok=True) 
    with open(exp_cfg_path, 'w+') as f:
      yaml.dump(exp, f, default_flow_style=False, sort_keys=False)
  

  # Fake Data
  train_data = torch.utils.data.DataLoader(RandomDataset(32, 64))
  val_data = torch.utils.data.DataLoader(RandomDataset(32, 64))
  test_data = torch.utils.data.DataLoader(RandomDataset(32, 64))

  # Model
  model = BoringModel()
      
  # Train and Test
  if ( exp['trainer'] ).get('gpus', -1):
    nr = torch.cuda.device_count()
    exp['trainer']['gpus'] = nr
    print( f'Set GPU Count for Trainer to {nr}!' )

  trainer = Trainer(
    **exp['trainer'],
    default_root_dir = model_path
  )
  trainer.fit(model, train_data, val_data)
  trainer.test(test_dataloaders=test_data)
