"""
SLAVE COMPONENT: Gas Dynamics --> Chamber --> Motor
"""

from CoolProp.CoolProp import PropsSI

from dataclasses import dataclass

from ..modules.units import *

# PROPERTIES

@dataclass
class AmbientProps:
    temperature: float
    pressure: float
    name: str


# MAIN CLASS

class Gas:
    def __init__(self, chamber_props, ambient_props):
        air_density = PropsSI('D', 'T', ambient_props.temperature, 'P', ambient_props.pressure, 'Air')
        self._gas_mass = air_density * chamber_props.volume
        self._pressure = ambient_props.pressure
        self._volume = chamber_props.volume

    def pressurize(self, grain_state, tank_state, nozzle_state, pd_limit, time_step):
        if (self._pressure * (((tank_state.mfr + grain_state.mfr - nozzle_state.mfr) / self._gas_mass) - \
                              (grain_state.vfr / (self._volume)))) > pd_limit:
            self._pressure += pd_limit * time_step
        else:
            self._pressure += (self._pressure * (((tank_state.mfr + grain_state.mfr - nozzle_state.mfr) / self._gas_mass) - \
                              (grain_state.vfr / (self._volume)))) * time_step
        self._volume += grain_state.vfr * time_step
        self._gas_mass += (tank_state.mfr + grain_state.mfr - nozzle_state.mfr) * time_step
        return self._pressure, self._gas_mass / self._volume
        
        

    @property
    def telemetry(self):
        # TODO
        return {"Chamber Pressure (PSI)": self._pressure * pa,
                "Gas Mass (kg)": self._gas_mass}