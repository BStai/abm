from typing import Dict, Any, Optional
import json
import os
from datetime import datetime
import pandas as pd

global CONFIG

def ceildiv(a, b):
  return -(a // -b)

def floordiv(a,b):
  return a // b

def chebychev_dist(start,end):
  return max(abs(a-b) for a, b in zip(start,end))

def get_config_dir()-> str:
    # CANDO expand this to search dynamically for wherever these end up living
    return "../data/configs"

def write_config(conf):
    config_dir = get_config_dir()
    filename = conf['name'] + "_asof_" + datetime.now().isoformat() + ".json"
    with open(os.path.join(config_dir,filename),"w") as f:
        json.dump(conf,f)
    print(f"wrote config {filename}")

def load_config(run_name: str, written_on: Optional[datetime] = None, latest = True) -> Dict[str, Any]:
    config_dir = get_config_dir()
    potential_configs = [f for f in os.listdir(config_dir) if run_name in f and "_asof_" in f]
    dts = [pd.Timestamp(s[s.find("_asof_")+6:s.find(".json")]) for s in potential_configs]

    search_time = pd.Timestamp(written_on)
    matching_times = [s for s in dts if 
        (s.year == search_time.year) & # must match year
        (s.month == search_time.month) & # must match month
        (s.day == search_time.day) & # must match day
        (search_time.hour == 0 or s.hour == search_time.hour) & # fine if no hour given 
        (search_time.minute == 0 or s.minute == search_time.minute) # fine if no minute given
     ]

    if latest:
        idx = dts.index(max(matching_times))
        filename = potential_configs[idx]
    else:
        # CANDO add functionality for closest to actual timestamp
        raise NotImplemented


    with open(file=os.path.join(config_dir,filename)) as f:
        conf = json.load(f)
    
    global CONFIG 
    CONFIG = conf

    print(f"loaded config {filename}")
    return conf

