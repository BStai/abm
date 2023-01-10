from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any
from tqdm import trange
from collections import Counter
from statistics import mean

import mesa
import pandas as pd
import json



import os

# from .model import FreightMarketModel
from .util import *
from .shipper import ShipperAgent
from .carrier import CarrierAgent


@dataclass
class ExperimentConfig:
    name: str
    version: int = 0

    n_shippers: int = 50
    n_carriers: int = 400
    width: int = 40
    height: int = 10

    carrier_speed_per_tick: int = 3
    carrier_search_radius: int = 1
    carrier_search_type: str = "stay_put"  # ['stay_put','random_walk']
    carrier_rand_walk_amount: int = 1

    shipper_starting_rate: int = 3
    shipper_max_unbooked: int = 50
    shipper_lead_time: int = 3


# global CONFIG
# CONFIG = ExperimentConfig(name="default")


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
    print(f"loaded config {filename}")
    return filename, conf


class ExperimentRunner:
    def __init__(self) -> None:
        pass

    def run_experiments(
        self,
        config_list: List[Tuple[str, Optional[str]]],
        n_steps=50,
    ) -> None:
        """Take a list of configuration params (run name, date) and run the model with these configs"""

        for run_name, date in config_list:
            try:
                conf_filename, conf = load_config(run_name=run_name, written_on=date)
            except:
                print("Unable to load config")
                continue

            # run model
            model = FreightMarketModel(experiment_config=conf)

            for _ in trange(n_steps):
                model.step()

            # write out data
            df_model = model.datacollector.get_model_vars_dataframe()
            df_model = self.format_model_results(df_model)
            self.write_results(df_model, conf_filename, "mdata")

            df_agents = model.datacollector.get_agent_vars_dataframe()
            self.write_results(df_agents, conf_filename, "adata")

    def format_model_results(self, df) -> pd.DataFrame:
        df = pd.concat(
            [
                df["carrier_states"].apply(pd.Series),
                df.drop(["carrier_states"], axis=1),
            ],
            axis=1,
        )
        return df

    def write_results(
        self, df: pd.DataFrame, conf_filename: str, tag: str = ""
    ) -> None:
        filename = (
            "df_"
            + tag
            + "_"
            + conf_filename.replace(".json", "_")
            + "run_"
            + datetime.now().isoformat()
            + ".parquet"
        )
        df.to_parquet(os.path.join("../data/results", filename))
        # CANDO change this to write out parquet files so that I can query across multiple runs with duckdb


class FreightMarketModel(mesa.Model):
    """Freight market model."""

    def __init__(self, experiment_config: ExperimentConfig) -> None:
        self.config = experiment_config

        self.n_shippers = self.config.n_shippers
        self.n_carriers = self.config.n_carriers
        self.carrier_grid = mesa.space.MultiGrid(
            self.config.width, self.config.height, torus=False
        )
        self.load_grid = mesa.space.MultiGrid(
            self.config.width, self.config.height, torus=False
        )
        self.schedule = mesa.time.RandomActivationByType(self)
        self.current_tick = 0

        # Create agents
        for i in range(self.n_shippers):
            a = ShipperAgent(i, self)
            self.schedule.add(a)
            # shippers don't have single location

        for i in range(self.n_shippers, self.n_shippers + self.n_carriers):
            a = CarrierAgent(unique_id=i, model=self, pos=None)
            self.schedule.add(a)
            # Add the agent to a random grid cell
            x = self.random.randrange(self.carrier_grid.width)
            y = self.random.randrange(self.carrier_grid.height)
            self.carrier_grid.place_agent(a, (x, y))

        # set up datacollector
        self.datacollector = mesa.DataCollector(
            # model_reporters={"Gini": compute_gini}, agent_reporters={"Wealth": "wealth"}
            model_reporters={
                "n_loads": count_unbooked_loads,
                "mean_rolls_unbooked": mean_rolls_unbooked,
                "carrier_states": count_carrier_states,
            },
            agent_reporters={
                "agent_type": lambda a: type(a).__name__,
                "carrier_loads_moved": lambda a: getattr(a, "loads_moved", None),
                "carrier_status": lambda a: getattr(a, "status", None),
            },
        )

    def __repr__(self):
        return f"M@{self.current_tick}"

    def get_loads_available_to_book():
        """get full list of all avaliable loads"""
        pass

    def step(self):
        # don't shuffle types - shippers go first
        self.schedule.step(shuffle_types=False, shuffle_agents=True)
        self.datacollector.collect(self)
        self.current_tick += 1


def count_unbooked_loads(model: FreightMarketModel) -> int:
    return len([l for loads, _, _ in model.load_grid.coord_iter() for l in loads])


def count_available_carriers(model: FreightMarketModel) -> int:
    return len(
        [c for carriers, _, _ in model.carrier_grid.coord_iter() for c in carriers]
    )


def count_carrier_states(model: FreightMarketModel):
    return Counter(
        (c.status.name for c in model.schedule.agents_by_type[CarrierAgent].values())
    )


def mean_rolls_unbooked(model: FreightMarketModel):
    roll_counts = [
        l.roll_count for loads, _, _ in model.load_grid.coord_iter() for l in loads
    ]
    if len(roll_counts) < 1:
        return 0
    else:
        return mean(roll_counts)


# other metrics to track
# number of carriers in each state - deadheading, searching, in transit
# distribution of load states and rolls?
