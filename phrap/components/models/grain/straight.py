"""
MASTER SLAVE COMPONENT: Grain --> Chamber --> Motor
"""

from dataclasses import dataclass
import math

from ..modules.units import *

# PROPERTIES

@dataclass
class GrainProps:
    density: float
    regression_coefficient: float
    regression_exponent: float
    length_exponent: float
    inner_diameter: float
    outer_diameter: float
    length: float
    file_name: str


# SNAPSHOTS

@dataclass
class GrainState:
    mfr: float
    vfr: float
    of: float


# MAIN CLASS

class Grain:
    def __init__(self, grain_props):
        # TODO-HIGH make functionable
        self._density = grain_props.density
        self._regression_coefficient = grain_props.regression_coefficient
        self._regression_exponent = grain_props.regression_exponent
        self._length_exponent = grain_props.length_exponent
        self._hydraulic_diameter = grain_props.inner_diameter
        self._outer_diameter = grain_props.outer_diameter
        self._length = grain_props.length
        self._mass = self._density * math.pi * ((self._outer_diameter / 2)**2 - (self._hydraulic_diameter / 2)**2) * self._length
        self._regression = 0
        self._vfr = 0
        self._mfr = 0
        self._of = 4
        pass

    def initialize_state(self):
        return GrainState(mfr = 0,
                          vfr = 0,
                          of = 4)
    
    def burn(self, gas_density, tank_state, nozzle_state, time_step):
        # TODO-HIGH make functionable
        port_area = math.pi * ((self._hydraulic_diameter / 2)**2)
        oxidizer_flux = tank_state.mfr / port_area
        regression = self._regression_coefficient * (oxidizer_flux**self._regression_exponent)
        self._regression = regression
        self._vfr = (((self._hydraulic_diameter + regression * 0.001 * 2) / 2)**2) * math.pi * self._length - \
              ((self._hydraulic_diameter / 2)**2) * math.pi * self._length
        self._mfr = self._vfr * self._density
        self._mass -= self._mfr * time_step
        if self._mfr > 0:
            self._of = tank_state.mfr / self._mfr
        else:
            self._of = 5
        self._hydraulic_diameter += regression * 0.001 * 2 * time_step

        return self._state

    @property
    def telemetry(self):
        # TODO-HIGH include any other relevant properties
        return {"Hydraulic Diameter (in)": self._hydraulic_diameter / inch,
                "Hydraulic Diameter (m)": self._hydraulic_diameter,
                "Total Fuel Grain Mass (kg)": self._mass,
                "Regression Rate (mm/s)": self._regression if hasattr(self, "_regression") else 0}

    @property
    def _state(self):
        # TODO-HIGH make functionable
        return GrainState(mfr = self._mfr,
                          vfr = self._vfr,
                          of = self._of)