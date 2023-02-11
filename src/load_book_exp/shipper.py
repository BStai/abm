import mesa
from typing import List

from .load import Load


class ShipperAgent(mesa.Agent):
    """An agent simulating a shipper."""

    def __init__(self, unique_id: int, model: mesa.Model) -> None:
        super().__init__(unique_id, model)
        self.loads: List[Load] = []

    def get_rate(self, load: Load):
        """pick a rate to put on a load"""
        dist = load.get_distance()
        rate = (
            self.model.config.shipper_starting_rate * dist
        )  # fixed rate per distance to start
        return rate

    def get_load_locations(self) -> mesa.space.Position:
        w = self.model.load_grid.width
        h = self.model.load_grid.height
        o = self.random.randrange(w), self.random.randrange(h)
        d = self.random.randrange(w), self.random.randrange(h)
        return o, d

    def spawn_loads(self, current_tick: int) -> None:
        """Spawn new loads."""
        # spawn on load to start
        # cap number of unbooked loads
        if len(self.get_unbooked_loads()) >= self.model.config.shipper_max_unbooked:
            return

        # id is "shipper id_tick spawned_n"
        load_id = (
            str(self.unique_id) + "_" + str(self.model.current_tick) + "_0"
        )  # eventually implement batch loads
        o, d = self.get_load_locations()
        planned_tick = current_tick + self.model.config.shipper_lead_time
        load = Load(
            experiment_config=self.model.config,
            load_id=load_id,
            o=o,
            d=d,
            planned_tick=planned_tick,
        )
        load.rate = self.get_rate(load)

        self.loads.append(load)
        self.model.load_grid.place_agent(
            load, load.o
        )  # shippers put loads on load grid, carriers remove on booking

    def manage_loads(self, current_tick: int) -> None:
        """Update loads"""
        for load in self.loads:
            load.update_load_state(current_tick)
        # eventually do some sort of rate adjustments here

    def step(self):
        self.spawn_loads(self.model.current_tick)
        self.manage_loads(self.model.current_tick)

    def get_unbooked_loads(self) -> List[Load]:
        return [x for x in self.loads if not x.is_booked]
