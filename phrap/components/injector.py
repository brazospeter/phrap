"""
SLAVE COMPONENT: Injector --> Tank --> Motor
"""

import math

from CoolProp.CoolProp import PropsSI

from dataclasses import dataclass, asdict

from ..modules.units import *

# PROPERTIES

@dataclass
class InjectorProps:
    diameter: float
    discharge_coeff_spi: float
    discharge_coeff_gas: float = None
    discharge_coeff_hem: float = None


# SNAPSHOTS

@dataclass
class InjectorState:
    mfr: float
    port_density: float

# MAIN CLASS

class Injector:
    def __init__(self, injector_props):
        # TODO-HIGH make functionable
        self._area = math.pi * (injector_props.diameter / 2) ** 2
        self._discharge_coefficient_spi = injector_props.discharge_coeff_spi
        if injector_props.discharge_coeff_gas:
            self._discharge_coefficient_gas = injector_props.discharge_coeff_gas
        else:
            self._discharge_coefficient_gas = injector_props.discharge_coeff_spi
        self._discharge_coefficient_hem = injector_props.discharge_coeff_hem
        self._temp = 0
        self._critical_pressure = 0
        self._quality = 0


    def inject(self, oxidizer_state, chamber_state, phase):
        # TODO-HIGH make functionable
        if phase == "liquid":
            self._pressure_drop = oxidizer_state.pressure - chamber_state.pressure
            if self._discharge_coefficient_hem:
                upstream_enthalpy = PropsSI('H','P',oxidizer_state.pressure,'Q',0,oxidizer_state.name)
                entropy = PropsSI('S','P',oxidizer_state.pressure,'Q',0,oxidizer_state.name)
                try:
                    quality = PropsSI('Q','P',chamber_state.pressure,'S',entropy,oxidizer_state.name)
                except:
                    quality = 0
                if quality < 0:
                    quality = 0
                elif quality > 1:
                    quality = 1
                if (oxidizer_state.liquid_mass) / oxidizer_state.total_mass >= 0:
                    quality_suppression = ((oxidizer_state.liquid_mass) / oxidizer_state.total_mass)
                else:
                    quality_suppression = 0
                if quality_suppression**0.2 < 0.5:
                    quality_suppression = quality_suppression**0.5
                    try:
                        isenthalpic_quality = PropsSI('Q','P',chamber_state.pressure,'H',upstream_enthalpy,oxidizer_state.name)
                    except:
                        isenthalpic_quality = 0
                    if isenthalpic_quality < 0:
                        isenthalpic_quality = 0
                    elif isenthalpic_quality > 1:
                        isenthalpic_quality = 1
                    quality = quality * quality_suppression + (1 - quality_suppression) * isenthalpic_quality

                downstream_density = (oxidizer_state.liquid_density * oxidizer_state.vapor_density) / (oxidizer_state.liquid_density * quality + oxidizer_state.vapor_density * (1 - quality))
                downstream_enthalpy = PropsSI('H','P',chamber_state.pressure,'Q',quality,oxidizer_state.name)
                self._quality = quality
                if type(self._discharge_coefficient_hem) == bool:
                    self._model = "SPI"
                    self._mfr_ox = self._discharge_coefficient_spi * self._area * math.sqrt(2 * (oxidizer_state.pressure - chamber_state.pressure) * oxidizer_state.liquid_density)
                    if (chamber_state.pressure < self._temp):
                        self._discharge_coefficient_hem = self._mfr_ox / (self._area * downstream_density * math.sqrt(2 * (upstream_enthalpy - downstream_enthalpy)))
                        print(self._discharge_coefficient_hem)
                    else:
                        self._temp = chamber_state.pressure
                else:
                    self._critical_pressure = ((self._discharge_coefficient_hem * downstream_density * ((2 * (upstream_enthalpy - downstream_enthalpy))**0.5)) / (self._discharge_coefficient_spi * ((2 * oxidizer_state.liquid_density)**0.5)))**2
                    try:
                        if (self._pressure_drop > self._critical_pressure) or (quality_suppression < 1):
                            try:
                                self._mfr_ox = self._discharge_coefficient_hem * self._area * downstream_density * math.sqrt(2 * (upstream_enthalpy - downstream_enthalpy))
                                self._model = "HEM"
                            except:
                                self._mfr_ox = 0
                                self._model = "HEM"
                        else:
                            self._mfr_ox = self._discharge_coefficient_spi * self._area * math.sqrt(2 * (oxidizer_state.pressure - chamber_state.pressure) * oxidizer_state.liquid_density)
                            self._model = "SPI"
                    except:
                        self._mfr_ox = 0
                        self._model = "HEM"
            else:
                self._mfr_ox = self._discharge_coefficient_spi * self._area * math.sqrt(2 * (oxidizer_state.pressure - chamber_state.pressure) * oxidizer_state.liquid_density)
                self._model = "SPI"
                self._critical_pressure = self._pressure_drop
            
        elif phase == "vapor":
            mach = (oxidizer_state.compressibility_factor * oxidizer_state.gamma * oxidizer_state.gas_constant * oxidizer_state.temperature * \
                    ((chamber_state.pressure / oxidizer_state.pressure)**((oxidizer_state.gamma - 1) / oxidizer_state.gamma)))**0.5
            mach = ((2 / (oxidizer_state.gamma - 1)) * (((chamber_state.pressure / oxidizer_state.pressure)**(-(oxidizer_state.gamma - 1) / oxidizer_state.gamma)) - 1))**0.5
            self._model = "SPC"
            if mach > 1:
                mach = 1
            #print(asdict(oxidizer_state))
            self._mfr_ox = ((self._discharge_coefficient_gas * self._area * oxidizer_state.pressure) / ((oxidizer_state.temperature)**0.5)) * \
                           ((oxidizer_state.gamma / (oxidizer_state.compressibility_factor * oxidizer_state.gas_constant))**0.5) * mach * \
                           ((1 + ((oxidizer_state.gamma - 1) / 2) * mach**2)**(-((oxidizer_state.gamma + 1) / (2 * (oxidizer_state.gamma - 1)))))

        self._port_density = PropsSI("D", "P", chamber_state.pressure, "Q", 0, oxidizer_state.name)
        
        return self._state

    @property
    def telemetry(self):
        # TODO-HIGH include any other relevant properties
        return {"MFR Injector (kg/s)": self._mfr_ox,
                "Pressure Drop (PSI)": self._pressure_drop * pa,
                "Critical Pressure (PSI)": self._critical_pressure * pa,
                "Oxidizer MFR Model": self._model,
                "Quality": self._quality}

    @property
    def _state(self):
        return InjectorState(mfr = self._mfr_ox,
                             port_density = self._port_density)