from typing import Optional
import mesa
from .util import *


class Load:
    """Class for simulated loads."""

    def __init__(
        self,
        experiment_config,
        load_id: str,
        o: mesa.space.Position,
        d: mesa.space.Position,
        planned_tick: int,  # scheduled "activity date"
        rate: Optional[int] = None,
    ) -> None:

        self.config = experiment_config
        self.load_id = load_id
        self.o = o
        self.d = d
        self.rate = rate
        self.planned_tick = planned_tick
        self.roll_count = 0
        self.is_booked = False
        self.is_picked = False
        self.is_dropped = False

    def __repr__(self):
        return f"""{self.load_id} OD[{self.o}{self.d}] @{self.planned_tick}-{self.get_drop_tick()}(+{self.roll_count}) ${self.rate} bpd[{int(self.is_booked)}{int(self.is_picked)}{int(self.is_dropped)}]"""

    def get_distance(self) -> int:
        """Get Chebyshev distance"""
        return chebychev_dist(self.o, self.d)

    def get_transit_time(self) -> int:
        """Get number of ticks expected to move"""
        dist = self.get_distance()
        required_ticks = ceildiv(dist, self.config.carrier_speed_per_tick)
        return required_ticks

    def get_drop_tick(self) -> int:
        """Get the tick the load will be dropped"""
        return self.planned_tick + self.get_transit_time()

    def get_rate_per(self) -> float:
        """get rate divided by distance"""
        return self.rate / self.get_distance()

    def book_load(self) -> None:
        """mark load as booked"""
        self.is_booked = True

    def update_load_state(self, current_tick: int) -> None:
        """auto update load, assuming no same-day booking"""
        if not self.is_booked and current_tick >= self.planned_tick:
            # need to roll forward another day
            self.planned_tick += 1
            self.roll_count += 1
            return

        if self.is_booked and current_tick < self.planned_tick:
            # state is waiting on pick, don't need to do anything
            return

        if self.is_booked and current_tick == self.planned_tick:
            # reached pick tick
            self.is_picked = True
            return

        if self.is_picked and current_tick >= self.get_drop_tick():
            # reached drop tick
            self.is_dropped = True
            return
