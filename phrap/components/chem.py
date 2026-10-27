"""
SLAVE COMPONENT: Chemistry --> Nozzle --> Motor
"""

import math

import rocketcea.units
from rocketcea.cea_obj import CEA_Obj, add_new_fuel, add_new_oxidizer, add_new_propellant

from dataclasses import dataclass

from ..modules.units import *

# PROPERTIES

@dataclass
class ChemProps:
    card_str: str
    combustion_efficiency: float
    ervme_step: float
    # TODO-LOW Add more items


# SNAPSHOTS

@dataclass
class ChemState:
    gamma_exit: float
    mach_exit: float
    gas_constant_exit: float
    temperature_chamber: float
    characteristic_velocity: float
    dynamic_viscosity: float
    molar_mass: float
    density_chamber: float
    # TODO-MEDIUM Add more items


# MAIN CLASS

class Chem:
    def __init__(self, chem_props, nozzle_props):
        add_new_fuel('ABS', chem_props.card_str)
        rocketcea.units.add_default_unit(name = "temperature_units", akaL = "K")
        self._C = CEA_Obj(oxName="N2O", fuelName="ABS")
        self._combustion_efficiency = chem_props.combustion_efficiency
        self._expansion_ratio = nozzle_props.expansion_ratio
        self._ervme_step = chem_props.ervme_step
        self._mach_exit = 1

    def pressurize(self, chamber_state):
        # TODO-HIGH make functionable
        self._characteristic_velocity = self._combustion_efficiency * self._C.get_Cstar(Pc=chamber_state.pressure / psi, MR=chamber_state.of_ratio) * ft
        self._gas_constant_exit = 8314 / self._C.get_exit_MolWt_gamma(Pc = chamber_state.pressure / 6985, MR = chamber_state.of_ratio, eps = self._expansion_ratio)[0]
        self._gas_constant_chamber = 8314 / self._C.get_Chamber_MolWt_gamma(Pc = chamber_state.pressure / 6985, MR = chamber_state.of_ratio, eps = self._expansion_ratio)[0]
        self._gamma_exit = self._C.get_exit_MolWt_gamma(Pc = chamber_state.pressure / 6985, MR = chamber_state.of_ratio, eps = self._expansion_ratio)[1]
        self._chamber_temperature = self._C.get_Temperatures(Pc=chamber_state.pressure / 6985, MR=chamber_state.of_ratio, eps=self._expansion_ratio)[0] * (5/9)
        self._density_chamber = self._C.get_Chamber_Density(Pc=chamber_state.pressure / 6985, MR=chamber_state.of_ratio, eps=self._expansion_ratio) * 16.0185

        self._viscosity = self._C.get_Chamber_Transport(Pc=chamber_state.pressure / 6985, MR=chamber_state.of_ratio, eps=self._expansion_ratio)[1] * 0.001 # poise
        self._conductivity = self._C.get_Chamber_Transport(Pc=chamber_state.pressure / 6985, MR=chamber_state.of_ratio, eps=self._expansion_ratio)[2] * 4184000 # W/cm-K
        self._cp = self._C.get_Chamber_Cp(Pc=chamber_state.pressure / 6985, MR=chamber_state.of_ratio, eps=self._expansion_ratio) * 4.1868 # J/kg-K
        self._gamma = self._C.get_Chamber_MolWt_gamma(Pc=chamber_state.pressure / 6985, MR=chamber_state.of_ratio, eps=self._expansion_ratio)

        self._dynamic_viscosity = self._C.get_Chamber_Transport(Pc=chamber_state.pressure / 6985, MR=chamber_state.of_ratio, eps=self._expansion_ratio)[1] * 0.0001 # poise --> Pa-s
        self._molar_mass = self._C.get_Chamber_MolWt_gamma(Pc=chamber_state.pressure / 6985, MR=chamber_state.of_ratio, eps=self._expansion_ratio)[0]

        temp_expansion_ratio = (((self._gamma_exit + 1)/2)**(-(self._gamma_exit + 1)/(2*(self._gamma_exit - 1)))) * (((1 + ((self._gamma_exit - 1)/2) * (self._mach_exit**2))**((self._gamma_exit + 1)/(2 * (self._gamma_exit - 1)))) / self._mach_exit)
        
        if temp_expansion_ratio < self._expansion_ratio:
            while temp_expansion_ratio < self._expansion_ratio:
                self._mach_exit += self._ervme_step
                temp_expansion_ratio = (((self._gamma_exit + 1)/2)**(-(self._gamma_exit + 1)/(2*(self._gamma_exit - 1)))) * (((1 + ((self._gamma_exit - 1)/2) * (self._mach_exit**2))**((self._gamma_exit + 1)/(2 * (self._gamma_exit - 1)))) / self._mach_exit)
        else:
            while temp_expansion_ratio > self._expansion_ratio:
                self._mach_exit -= self._ervme_step
                temp_expansion_ratio = (((self._gamma_exit + 1)/2)**(-(self._gamma_exit + 1)/(2*(self._gamma_exit - 1)))) * (((1 + ((self._gamma_exit - 1)/2) * (self._mach_exit**2))**((self._gamma_exit + 1)/(2 * (self._gamma_exit - 1)))) / self._mach_exit)

        return self._state

    @property
    def telemetry(self):
        # TODO-HIGH make functionable
        return {"Characteristic Velocity (m/s)": self._characteristic_velocity,
                "Mach Exit": self._mach_exit}

    @property
    def _state(self):
        return ChemState(gamma_exit = self._gamma_exit,
                         mach_exit = self._mach_exit,
                         gas_constant_exit = self._gas_constant_exit,
                         temperature_chamber = self._chamber_temperature,
                         characteristic_velocity = self._characteristic_velocity,
                         dynamic_viscosity = self._dynamic_viscosity,
                         molar_mass = self._molar_mass,
                         density_chamber = self._density_chamber)