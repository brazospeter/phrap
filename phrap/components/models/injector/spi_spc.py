"""
SLAVE COMPONENT: Injector --> Tank --> Motor
"""

# SPI + SPC

import math

from dataclasses import dataclass, asdict

from modules.units import *

# PROPERTIES

@dataclass
class InjectorProps:
    diameter: float
    discharge_coeff_spi: float
    discharge_coeff_gas: float
    discharge_coeff_hem: float


# SNAPSHOTS

@dataclass
class InjectorState:
    mfr: float

# MAIN CLASS

class Injector:
    def __init__(self, injector_props):
        # TODO-HIGH make functionable
        self._area = math.pi * (injector_props.diameter / 2) ** 2
        self._discharge_coefficient_spi = injector_props.discharge_coeff_spi
        self._discharge_coefficient_gas = injector_props.discharge_coeff_gas
        self._discharge_coefficient_hem = injector_props.discharge_coeff_hem


    def inject(self, oxidizer_state, chamber_state, phase):
        # TODO-HIGH make functionable
        if phase == "liquid":
            self._mfr_ox = self._discharge_coefficient_spi * self._area * math.sqrt(2 * (oxidizer_state.pressure - chamber_state.pressure) * oxidizer_state.liquid_density)
        elif phase == "vapor":
            mach = (oxidizer_state.compressibility_factor * oxidizer_state.gamma * oxidizer_state.gas_constant * oxidizer_state.temperature * \
                    ((chamber_state.pressure / oxidizer_state.pressure)**((oxidizer_state.gamma - 1) / oxidizer_state.gamma)))**0.5
            mach = ((2 / (oxidizer_state.gamma - 1)) * (((chamber_state.pressure / oxidizer_state.pressure)**(-(oxidizer_state.gamma - 1) / oxidizer_state.gamma)) - 1))**0.5
            print(mach)
            if mach > 1:
                mach = 1
            #print(asdict(oxidizer_state))
            self._mfr_ox = ((self._discharge_coefficient_gas * self._area * oxidizer_state.pressure) / ((oxidizer_state.temperature)**0.5)) * \
                            ((oxidizer_state.gamma / (oxidizer_state.compressibility_factor * oxidizer_state.gas_constant))**0.5) * mach * \
                            ((1 + ((oxidizer_state.gamma - 1) / 2) * mach**2)**(-((oxidizer_state.gamma + 1) / (2 * (oxidizer_state.gamma - 1)))))
        return self._state

    @property
    def telemetry(self):
        # TODO-HIGH include any other relevant properties
        return {"MFR Injector (kg/s)": self._mfr_ox}

    @property
    def _state(self):
        return InjectorState(mfr = self._mfr_ox)