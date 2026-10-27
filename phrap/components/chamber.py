"""
MASTER COMPONENT: Combustion Chamber --> Motor
"""

from dataclasses import dataclass

from ..components.grain import Grain
from ..components.grain import GrainProps
from ..components.gas import Gas
from ..components.gas import AmbientProps
from .. import config
from ..modules.units import *


# PROPERTIES

@dataclass
class ChamberProps:
    volume: float


# SNAPSHOTS

@dataclass
class ChamberState:
    of_ratio: float
    pressure: float
    temperature: float


# MAIN CLASS

class Chamber:
    def __init__(self, chamber_props: ChamberProps, grain_props: GrainProps, ambient_props: AmbientProps):
        self._grain = Grain(grain_props)
        self._gas = Gas(chamber_props, ambient_props)
        self._pressure = ambient_props.pressure
        self._temperature = ambient_props.temperature
        self._gas_density = 1.225
    
    def initialize_state(self):
        return ChamberState(of_ratio = 0, 
                            pressure = self._pressure,
                            temperature = self._temperature)

    def combust(self, tank_state, nozzle_state, time_step):
        grain_state = self._grain.burn(self._gas_density, tank_state, nozzle_state, time_step)
        self._of = grain_state.of
        self._pressure, self._gas_density = self._gas.pressurize(grain_state, tank_state, nozzle_state, config.pd_limit, time_step)
        self._temperature = nozzle_state.temperature
        return self._state

    @property
    def telemetry(self):
        telemetry = {"Chamber Pressure (PSI)": self._pressure * pa,
                     "O/F Ratio": self._of}
        telemetry.update(self._grain.telemetry)
        telemetry.update(self._gas.telemetry)
        return telemetry

    @property
    def _state(self):
        return ChamberState(of_ratio = self._of,
                            pressure = self._pressure,
                            temperature = self._temperature)