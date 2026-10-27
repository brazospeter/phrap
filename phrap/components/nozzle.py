"""
MASTER COMPONENT: Nozzle --> Motor
"""


"""
TODO: dynamic viscosity, molar_mass
"""

import math

from dataclasses import dataclass

from .chem import Chem

from ..modules.units import *

# PROPERTIES

@dataclass
class NozzleProps:
    throat_diameter: float
    expansion_ratio: float
    discharge_coefficient: float
    nozzle_efficiency: float


# SNAPSHOTS

@dataclass
class NozzleState:
    mfr: float
    thrust: float
    dynamic_viscosity: float
    molar_mass: float
    temperature: float
    chamber_density: float


# MAIN CLASS

class Nozzle:
    def __init__(self, nozzle_props, chem_props):
        # TODO-HIGH make functionable
        self._chem = Chem(chem_props, nozzle_props)
        self._throat_diameter = nozzle_props.throat_diameter
        self._expansion_ratio = nozzle_props.expansion_ratio
        self._discharge_coefficient = nozzle_props.discharge_coefficient
        self._nozzle_efficiency = nozzle_props.nozzle_efficiency
        self._characteristic_velocity = 0
        self._temp = 0
        self._prop_mass = 0
        pass

    def initialize_state(self):
        return NozzleState(mfr = 0,
                           thrust = 1,
                           dynamic_viscosity = 1,
                           molar_mass = 1,
                           temperature = 1,
                           chamber_density = 1)

    def choke(self, chamber_state, ambient_state, time_step):
        # TODO-HIGH make functionable
        chem_state = self._chem.pressurize(chamber_state)
        self._dynamic_viscosity = chem_state.dynamic_viscosity
        self._molar_mass = chem_state.molar_mass

        self._characteristic_velocity = chem_state.characteristic_velocity
        self._mfr = self._discharge_coefficient * ((chamber_state.pressure) * (math.pi * ((self._throat_diameter / 2)**2)) / (chem_state.characteristic_velocity))
        self._prop_mass += self._mfr * time_step
        self._exit_pressure = chamber_state.pressure / ((1 + (((chem_state.gamma_exit - 1) / 2) * (chem_state.mach_exit**2)))**(chem_state.gamma_exit / (chem_state.gamma_exit - 1)))
        self._thrust_coefficient = ((((2 * chem_state.gamma_exit**2) / (chem_state.gamma_exit - 1))*(2 / (chem_state.gamma_exit + 1))**((chem_state.gamma_exit + 1)/ \
        (chem_state.gamma_exit - 1))*(1 - (self._exit_pressure/chamber_state.pressure)**((chem_state.gamma_exit-1)/chem_state.gamma_exit)))**0.5)+ \
        ((self._exit_pressure - ambient_state.pressure)*((math.pi * ((self._throat_diameter / 2)**2)) * self._expansion_ratio))/ \
        (chamber_state.pressure * (math.pi * ((self._throat_diameter / 2)**2)))

        self._temperature = chem_state.temperature_chamber
        self._chamber_density = chem_state.density_chamber
        self._exit_temperature = chem_state.temperature_chamber / (1 + (((chem_state.gamma_exit - 1) / 2) * (chem_state.mach_exit**2)))
        self._velocity_exit = chem_state.mach_exit * ((chem_state.gamma_exit * chem_state.gas_constant_exit * self._exit_temperature)**0.5)
        self._thrust = self._nozzle_efficiency * (self._mfr * self._velocity_exit + (self._exit_pressure - ambient_state.pressure) * (math.pi * ((self._throat_diameter / 2)**2) * self._expansion_ratio))
        self._thrust = self._discharge_coefficient * self._thrust_coefficient * (math.pi * ((self._throat_diameter / 2)**2)) * chamber_state.pressure * self._nozzle_efficiency
        if self._thrust < 0:
            self._thrust = 0

        self._velocity_exit = self._thrust / self._mfr if self._mfr != 0 else 2100
        return self._state

    @property
    def telemetry(self):
        # TODO-HIGH include any other relevant properties
        telemetry = {"MFR Nozzle (kg/s)": self._mfr,
                     "Thrust (N)": self._thrust,
                     "Nozzle Temp": self._temp,
                     "Exit Pressure (atm)": self._exit_pressure / atm,
                     "Total Propellant Mass Expelled (kg)": self._prop_mass,
                     "Exit Velocity (m/s)": self._velocity_exit}
        telemetry.update(self._chem.telemetry)
        return telemetry

    @property
    def _state(self):
        # TODO-HIGH make functionable
        return NozzleState(mfr = self._mfr,
                           thrust = self._thrust,
                           dynamic_viscosity = self._dynamic_viscosity,
                           molar_mass = self._molar_mass,
                           temperature = self._temperature,
                           chamber_density = self._chamber_density)