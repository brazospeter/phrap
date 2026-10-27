"""
MASTER SLAVE COMPONENT: Oxidizer --> Tank --> Motor
"""

# Equilibrium tank modeling, two volume nodes: liquid, gas

from dataclasses import dataclass

from CoolProp.CoolProp import PropsSI

from modules.units import pa

import traceback
import sys

# PROPERTIES

@dataclass
class OxidizerProps:
    name: str
    temperature: float


# SNAPSHOTS

@dataclass
class OxidizerState:
    total_mass: float
    liquid_mass: float
    liquid_density: float
    vapor_density: float
    compressibility_factor: float
    gamma: float
    gas_constant: float
    pressure: float
    temperature: float
    # TODO-LOW include oxidizer slices for 2d model


# MAIN CLASS

class Oxidizer:
    def __init__(self, tank_props, oxidizer_props):
        self._temperature = oxidizer_props.temperature
        self._name = oxidizer_props.name
        self._tank_model = "isenthalpic"
        
        self._liquid_density = PropsSI("D", "T", self._temperature, "Q", 0, self._name)
        self._vapor_density = PropsSI("D", "T", self._temperature, "Q", 1, self._name)
        self._liquid_mass = tank_props.volume * (1 - tank_props.ullage) * self._liquid_density
        self._vapor_mass = tank_props.volume * tank_props.ullage * self._vapor_density
        self._total_mass = self._liquid_mass + self._vapor_mass
        self._volume = tank_props.volume
        self._compressibility_factor = 0.55
        self._pressure = PropsSI("P", "T", self._temperature, "Q", 0, self._name)
        self._gamma = 1.4
        self._gas_constant = 287
        self._thermal_losses = []
        self._temp = None
        self._previous_state = None
        # TODO-LOW include oxidizer slices for 2d model
        

    def initialize_state(self):
        return OxidizerState(total_mass = self._total_mass,
                             liquid_mass = self._liquid_mass,
                             liquid_density = self._liquid_density,
                             vapor_density = self._vapor_density,
                             compressibility_factor = self._compressibility_factor,
                             gamma = self._gamma,
                             gas_constant = self._gas_constant,
                             pressure = self._pressure,
                             temperature = self._temperature)

    def equilize(self, phase, time_step):
        self._total_mass = self._liquid_mass + self._vapor_mass
        if phase == "liquid":
            self._pressure = PropsSI("P", "T", self._temperature, "Q", 0, self._name)
            self._liquid_density = PropsSI("D", "T", self._temperature, "Q", 0, self._name)
            self._vapor_density = PropsSI("D", "T", self._temperature, "Q", 1, self._name)

            vaporized_mass = ((self._volume * self._liquid_density * self._vapor_density - self._vapor_density * self._total_mass) / (self._liquid_density - self._vapor_density)) - self._vapor_mass
            self._vapor_mass = (self._volume * self._liquid_density * self._vapor_density - self._vapor_density * self._total_mass) / (self._liquid_density - self._vapor_density)
            self._liquid_mass = self._total_mass - self._vapor_mass

            if vaporized_mass >= 0 and self._tank_model != "average":
                heat_vaporization = PropsSI('H', 'T', self._temperature, 'Q', 1, self._name) - PropsSI('H', 'T', self._temperature, 'Q', 0, self._name)
                heat_capacity = PropsSI('C', 'T', self._temperature, 'Q', 0, self._name)
                heat_energy = vaporized_mass * heat_vaporization
                thermal_loss = heat_energy / (self._liquid_mass * heat_capacity)
                self._thermal_losses.append(thermal_loss)
            else:
                self._tank_model = "average"
                thermal_loss = sum(self._thermal_losses) / len(self._thermal_losses)
            self._temperature -= thermal_loss
            self._temp = thermal_loss
        elif phase == "vapor":
            self._tank_model = "isentropic"
            self._compressibility_factor = PropsSI("Z", "T|gas", self._temperature, "P", self._pressure, self._name)
            self._gamma = PropsSI("CPMOLAR", "T", self._temperature, "P|gas", self._pressure, self._name) / PropsSI("CVMOLAR", "T", self._temperature, "P|gas", self._pressure, self._name)
            self._gas_constant = PropsSI("GAS_CONSTANT", "T|gas", self._temperature, "P", self._pressure, self._name) / \
                PropsSI("MOLAR_MASS", "T|gas", self._temperature, "P", self._pressure, self._name) 
            self._vapor_density = self._vapor_mass / self._volume
            if self._previous_state is not None:
                entropy = PropsSI("S", "T|gas", self._previous_state.temperature, "P", self._previous_state.pressure, self._name)
                self._temperature = PropsSI("T", "D|gas", self._vapor_density, "S", entropy, self._name)
                self._pressure = PropsSI("P", "D|gas", self._vapor_density, "S", entropy, self._name)
        return self._state
    
    def extract(self, injector_state, phase, time_step):
        # TODO-HIGH make functionable
        extracted_mass = injector_state.mfr * time_step
        if phase == "liquid":
            self._liquid_mass -= extracted_mass
        if phase == "vapor":
            self._previous_state = self._state
            self._vapor_mass -= extracted_mass
        if self._total_mass <= 0:
            self._liquid_mass = 0
            self._vapor_mass = 0
        if self._liquid_mass < 0:
            self._vapor_mass += self._liquid_mass
            self._liquid_mass = 0

    @property
    def telemetry(self):
        # TODO-LOW include any other relevant properties
        return {"Total Mass (kg)": self._total_mass,
                "Liquid Mass (kg)": self._liquid_mass,
                "Vapor Mass (kg)": self._vapor_mass,
                "Tank Pressure (PSI)": self._pressure * pa,
                "Temperature (K)": self._temperature,
                "Oxidizer Temp": self._temp}

    @property
    def _state(self):
        # TODO-MEDIUM make functionable
        return OxidizerState(total_mass = self._total_mass,
                             liquid_mass = self._liquid_mass,
                             liquid_density = self._liquid_density,
                             vapor_density = self._vapor_density,
                             compressibility_factor = self._compressibility_factor,
                             gamma = self._gamma,
                             gas_constant = self._gas_constant,
                             pressure = self._pressure,
                             temperature = self._temperature)