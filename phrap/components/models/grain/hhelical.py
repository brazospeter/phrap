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
    longitudinal_diameter: float
    outer_diameter: float
    length: float
    file_name: str
    centerline_radius: float
    pitch: float


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
        self._initial_longitudinal_diameter = grain_props.longitudinal_diameter
        self._longitudinal_diameter = grain_props.longitudinal_diameter
        self._outer_diameter = grain_props.outer_diameter
        self._length = grain_props.length
        self._mass = 5
        self._of = 5

        self._helix_radius = grain_props.centerline_radius * (1 + (grain_props.pitch / (2 * math.pi * grain_props.centerline_radius)))
        self._helix_radius = (grain_props.centerline_radius + (grain_props.pitch / (2 * math.pi * grain_props.centerline_radius))) / grain_props.centerline_radius
        print(self._helix_radius)
        self._num_helical_turns = grain_props.length / grain_props.pitch
        self._centerline_radius = grain_props.centerline_radius

        self._pitch = grain_props.pitch

        self._skin_friction_amplification = 1
        self._radial_blowing_amplification = 1

        self._mass_generated = 0
        self._regreg = 0
        self._mfr = 0.01

        self._fuel_generated = 0
        self._oxidizer_injected = 0
        pass

    def initialize_state(self):
        return GrainState(mfr = 0,
                          vfr = 0,
                          of = 4)
    
    def burn(self, gas_density, tank_state, nozzle_state, time_step):
        longitudinal_diameter = self._longitudinal_diameter

        port_area = math.pi * ((longitudinal_diameter / 2)**2)
        oxidizer_flux = (tank_state.mfr) / port_area
        self._oxidizer_flux = oxidizer_flux
        straight_regression = self._regression_coefficient * (oxidizer_flux**self._regression_exponent)

        reynolds_number = (oxidizer_flux * self._length) / nozzle_state.dynamic_viscosity
        straight_skin_friction_coefficient = 0.074 / ((reynolds_number)**(1 / 5))
        effective_helix_radius = self._helix_radius * math.sqrt(1 + ((math.pi / 2) * (((longitudinal_diameter - self._initial_longitudinal_diameter) / self._helix_radius)**2)))
        flow_length = (self._length / self._pitch) * math.sqrt(((math.pi * longitudinal_diameter)**2) + (self._pitch**2))

        skin_friction_amplification = 1 + (0.0075 / straight_skin_friction_coefficient) * math.sqrt(longitudinal_diameter / (2 * effective_helix_radius))
        radial_blowing_amplification = (1 + (math.pi * longitudinal_diameter * flow_length * nozzle_state.chamber_density * (self._of**2) * (2 * math.pi * self._num_helical_turns)) / (0.25 * math.pi * (longitudinal_diameter**2) * tank_state.port_density * math.sqrt(1 + ((self._pitch / (2 * math.pi * self._centerline_radius)**2)))))**0.198
        
        if skin_friction_amplification * radial_blowing_amplification > 3:
            damping_factor = math.sqrt(3 / (skin_friction_amplification * radial_blowing_amplification))
            skin_friction_amplification *= damping_factor
            radial_blowing_amplification *= damping_factor
        
        regression = skin_friction_amplification * radial_blowing_amplification * straight_regression
        self._longitudinal_diameter += regression * 0.001 * 2 * time_step

        self._skin_friction_amplification = skin_friction_amplification
        self._radial_blowing_amplification = radial_blowing_amplification

        self._vfr = (((self._longitudinal_diameter + regression * 0.001 * 2) / 2)**2) * math.pi * self._length - \
                      ((self._longitudinal_diameter / 2)**2) * math.pi * self._length
        self._mfr = self._vfr * self._density

        self._fuel_generated += self._mfr * time_step
        self._oxidizer_injected += tank_state.mfr * time_step
        self._of = self._oxidizer_injected / self._fuel_generated if self._fuel_generated > 0 else 5

        return self._state

    @property
    def telemetry(self):
        # TODO-HIGH include any other relevant properties
        return {"Longitudinal Diameter (in)": self._longitudinal_diameter / inch,
                "Longitudinal Diameter (m)": self._longitudinal_diameter,
                "Total Fuel Grain Mass (kg)": self._mass,
                "Skin Friction Amplification": self._skin_friction_amplification,
                "Radial Blowing Amplification": self._radial_blowing_amplification,
                "Helical Ratio": self._skin_friction_amplification * self._radial_blowing_amplification,
                "Oxidizer Flux (kg/sm^2)": self._oxidizer_flux}

    @property
    def _state(self):
        # TODO-HIGH make functionable
        return GrainState(mfr = self._mfr,
                          vfr = self._vfr,
                          of = self._of)