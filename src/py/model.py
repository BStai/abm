import mesa
from .shipper import ShipperAgent
from .carrier import CarrierAgent

from collections import Counter

class FreightMarketModel(mesa.Model):
    """Freight market model."""

    def __init__(
        self, n_shippers: int, n_carriers: int, width: int, height: int
    ) -> None:
        self.n_shippers = n_shippers
        self.n_carriers = n_carriers
        self.carrier_grid = mesa.space.MultiGrid(width, height, torus=False)
        self.load_grid = mesa.space.MultiGrid(width, height, torus=False)
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
                "N_Loads": count_unbooked_loads,
                "N_Carriers": count_available_carriers,
                "unbooked_roll_total": total_rolls_unbooked,
                "Carrier_States": count_carrier_states,
            }
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


def total_rolls_unbooked(model: FreightMarketModel):
    return sum(
        (l.roll_count for loads, _, _ in model.load_grid.coord_iter() for l in loads)
    )


# other metrics to track
# number of carriers in each state - deadheading, searching, in transit
# distribution of load states and rolls?