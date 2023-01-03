import mesa
from typing import List, Optional
from strenum import StrEnum

from .load import Load
from .util import *


class CarrierStatus(StrEnum):
    SEARCHING = "Searching for any load"
    DEADHEADING = "Traveling to next booked load"
    IN_TRANSIT = "Carrying load"


class CarrierAgent(mesa.Agent):
    """An agent simulating a carrier."""

    def __init__(
        self, unique_id: int, model: mesa.Model, pos: mesa.space.Position
    ) -> None:
        super().__init__(unique_id, model)
        from .experiment import CONFIG

        self.config = CONFIG
        self.money = 0  # TODO make some kind of budgeting
        self.loads_moved: int = 0
        self.pos = pos
        self.load_queue: List[Load] = []
        self.current_load: Optional[Load] = None
        self.status = CarrierStatus.SEARCHING

    def __repr__(self):
        return f"C_{self.unique_id}"

    def can_pick_on_time(self, load: Load) -> bool:
        """evaluate if agent is able to reach load by activity date"""
        if self.current_load:
            t = self.current_load.get_drop_tick()
            pos = self.current_load.d
        else:
            t = self.model.current_tick
            pos = self.pos

        n_ticks_to_pick = load.planned_tick - t
        return self.config.carrier_speed_per_tick * n_ticks_to_pick >= chebychev_dist(
            pos, load.o
        )

    def does_not_conflict_with_current(self, load: Load) -> bool:
        """check that a load does not conflict with current"""
        # this isn't gonna apply when booking more than one out
        if self.current_load is None:
            return True
        return load.planned_tick > self.current_load.get_drop_tick()

    def search_pos_for_load(self, pos: mesa.space.Position):
        search_neighborhood = self.model.load_grid.get_neighborhood(
            pos=pos, moore=True, include_center=True, radius=1
        )
        load_list = self.model.load_grid.get_cell_list_contents(search_neighborhood)
        return load_list

    def add_to_load_queue(self) -> None:
        """search for available loads and book"""

        if (
            len(self.load_queue) == 0
        ):  # start with only searching for the next load when none booked
            # if no current load - search by current position
            if self.current_load is None:
                load_list = self.search_pos_for_load(self.pos)
            else:
                load_list = self.search_pos_for_load(self.current_load.d)
            # if current load - search from drop position
            if len(load_list) == 0:
                return
            # filter to ones that can handle
            load_list = [
                l
                for l in load_list
                if l is not None
                and self.can_pick_on_time(l)
                and self.does_not_conflict_with_current(l)
            ]
            if len(load_list) > 0:
                selected_load = self.random.choice(load_list)
            else:
                return

            # book load and add to queue
            selected_load.book_load()
            self.model.load_grid.remove_agent(
                selected_load
            )  # shippers put loads on load grid, carriers remove on booking
            self.load_queue.append(selected_load)

    def handle_current_load(self):
        # take one off the load queue if not currently processing
        if not self.current_load:
            if len(self.load_queue) > 0:
                self.current_load = self.load_queue.pop(0)
                self.model.carrier_grid.remove_agent(self)
            else:
                self.status = CarrierStatus.SEARCHING  # should already be set anyways
                return  # no load to handle

        # if have a current load
        if self.current_load.planned_tick > self.model.current_tick:
            self.status = CarrierStatus.DEADHEADING
        elif (self.current_load.planned_tick <= self.model.current_tick) and (
            self.current_load.get_drop_tick() > self.model.current_tick
        ):
            self.status = CarrierStatus.IN_TRANSIT
        else:
            # current load has been delivered
            self.loads_moved += 1
            self.money += self.current_load.rate

            if len(self.load_queue) == 0:
                self.model.carrier_grid.place_agent(self, self.current_load.d)
                self.current_load = None
                self.status = CarrierStatus.SEARCHING
            else:
                # set next up in load queue as current load
                self.current_load = self.load_queue.pop(0)
                self.status = CarrierStatus.DEADHEADING

    def move_while_searching(self):
        # should berandom walk
        # for now just stay put. Very boring carrier
        pass

    def step(self):
        self.add_to_load_queue()
        self.handle_current_load()
        if self.status == CarrierStatus.SEARCHING:
            self.move_while_searching()
