"""
SLAVE COMPONENT: Tank --> Motor
"""

from dataclasses import dataclass

from .oxidizer import Oxidizer
from .oxidizer import OxidizerProps
from .injector import Injector
from .injector import InjectorProps


# PROPERTIES

@dataclass
class TankProps:
    volume: float
    ullage: float


# SNAPSHOTS

@dataclass
class TankState:
    mfr: float
    total_mass: float
    port_density: float


# MAIN CLASS

class Tank:
    def __init__(self, tank_props: TankProps, injector_props: InjectorProps, oxidizer_props: OxidizerProps):
        self._oxidizer = Oxidizer(tank_props = tank_props,
                                 oxidizer_props = oxidizer_props)
        self._injector = Injector(injector_props = injector_props)
        self._phase = "liquid"
    
    def initialize_state(self):
        oxidizer_state = self._oxidizer.initialize_state()
        return TankState(mfr = 0,
                         total_mass = oxidizer_state.total_mass,
                         port_density = oxidizer_state.vapor_density)
    
    def blow(self, chamber_state, time_step):
        oxidizer_state = self._oxidizer.initialize_state()
        injector_state = self._injector.inject(oxidizer_state, chamber_state, self._phase)
        self._oxidizer.extract(injector_state, self._phase, time_step)
        oxidizer_state = self._oxidizer.equilize(self._phase, time_step)
        self._phase = Tank._check_phase(self._phase, oxidizer_state)
        self._mfr = injector_state.mfr
        self._total_mass = oxidizer_state.total_mass
        self._port_density = injector_state.port_density

        return self._state
    
    def _check_phase(phase, oxidizer_state):
        if oxidizer_state.liquid_mass <= 0:
            return "vapor"
        else:
            return "liquid"
    
    @property
    def telemetry(self):
        telemetry = {}
        telemetry.update(self._oxidizer.telemetry)
        telemetry.update(self._injector.telemetry)
        telemetry.update({"Phase": self._phase})
        return telemetry

    @property
    def _state(self):
        return TankState(mfr = self._mfr,
                         total_mass = self._total_mass,
                         port_density = self._port_density)