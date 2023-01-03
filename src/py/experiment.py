from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any
from tqdm import trange

import pandas as pd
import json
import os

from .model import FreightMarketModel
from .util import *


@dataclass
class ExperimentConfig:
    name: str
    version: int = 0
    # global
    carrier_speed_per_tick: int = 3
    # model params
    n_shippers: int = 50
    n_carriers: int = 400
    width: int = 40
    height: int = 10


global CONFIG
CONFIG = ExperimentConfig(name="default")


def get_config_dir() -> str:
    # CANDO expand this to search dynamically for wherever these end up living
    return "../data/configs"


def write_config(conf: ExperimentConfig):
    config_dir = get_config_dir()
    filename = conf.name + "_asof_" + datetime.now().isoformat() + ".json"

    with open(os.path.join(config_dir, filename), "w") as f:
        json.dump(asdict(conf), f)
    print(f"wrote config {filename}")


def load_config(
    run_name: str, written_on: Optional[datetime] = None, latest=True
) -> Dict[str, Any]:
    config_dir = get_config_dir()
    potential_configs = [
        f for f in os.listdir(config_dir) if run_name in f and "_asof_" in f
    ]
    dts = [
        pd.Timestamp(s[s.find("_asof_") + 6 : s.find(".json")])
        for s in potential_configs
    ]

    if written_on:
        # filter list to times matching written_on requirement
        search_time = pd.Timestamp(written_on)
        dts = [
            s
            for s in dts
            if (s.year == search_time.year)  # must match year
            & (s.month == search_time.month)  # must match month
            & (s.day == search_time.day)  # must match day
            & (
                search_time.hour == 0 or s.hour == search_time.hour
            )  # fine if no hour given
            & (
                search_time.minute == 0 or s.minute == search_time.minute
            )  # fine if no minute given
        ]

    if latest:
        idx = dts.index(max(dts))
        filename = potential_configs[idx]
    else:
        # CANDO add functionality for closest to actual timestamp
        raise NotImplemented
    with open(file=os.path.join(config_dir, filename)) as f:
        conf_dict = json.load(f)

    conf = ExperimentConfig(**conf_dict)
    global CONFIG
    CONFIG = conf
    print(f"loaded config {filename}")
    return filename


class ExperimentRunner:
    def __init__(self) -> None:
        pass

    def run_experiments(self, config_list: List[Tuple[str, Optional[str]]]) -> None:
        """Take a list of configuration params (run name, date) and run the model with these configs"""

        for run_name, date in config_list:
            try:
                conf_filename = load_config(run_name=run_name, written_on=date)
            except:
                print("Unable to load config")
                continue

            # run model
            model = FreightMarketModel(
                n_shippers=CONFIG.n_shippers,
                n_carriers=CONFIG.n_carriers,
                width=CONFIG.width,
                height=CONFIG.height,
            )
            for i in trange(50):
                model.step()

            # write out data
            df = model.datacollector.get_model_vars_dataframe()
            df = self.format_results(df)
            self.write_results(df, conf_filename)

    def format_results(self, df) -> pd.DataFrame:
        df = pd.concat(
            [
                df["carrier_states"].apply(pd.Series),
                df.drop(["carrier_states"], axis=1),
            ],
            axis=1,
        )
        return df

    def write_results(self, df: pd.DataFrame, conf_filename: str) -> None:
        filename = (
            "df_"
            + conf_filename.replace(".json", "_")
            + "run_"
            + datetime.now().isoformat()
            + ".csv"
        )
        df.to_csv(os.path.join("../data/results", filename))
        # CANDO change this to write out parquet files so that I can query across multiple runs with duckdb
