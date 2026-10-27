from .components.chamber import Chamber
from .components.chamber import ChamberProps

from .components.grain import GrainProps
from .components.gas import AmbientProps


from .components.tank import Tank
from .components.tank import TankProps

from .components.oxidizer import OxidizerProps
from .components.injector import InjectorProps


from .components.nozzle import Nozzle
from .components.nozzle import NozzleProps

from .components.chem import ChemProps

from .motor import Motor

from .modules.units import *
from . import config
from . import inputs

def build_motor(temperature):
    tank_props = TankProps(volume = 27659 * cc, 
                        ullage = 0.2)
    oxidizer_props = OxidizerProps(name = "N2O", 
                                temperature = k(temperature))
    injector_props = InjectorProps(diameter = 0.125 * inch,
                                discharge_coeff_spi = 0.7 * 3,
                                discharge_coeff_gas = 0.95 * 3,
                                discharge_coeff_hem = 0.9 * 3)
    chamber_props = ChamberProps(volume = 10*0.0002338434)
    grain_props = GrainProps(density = 1070,
                            regression_coefficient = 0.198,
                            regression_exponent = 0.325,
                            length_exponent = 0,
                            inner_diameter = 3.25 * inch,
                            outer_diameter = 5 * inch,
                            length = 17 * inch,
                            file_name = "grain.stl")
    ambient_props = AmbientProps(temperature = k(temperature),
                                pressure = 0.99 * atm,
                                name = "Air")
    nozzle_props = NozzleProps(throat_diameter = 1.0 * inch, 
                            expansion_ratio = 4.8,
                            discharge_coefficient = 1, 
                            nozzle_efficiency = 1)
    chem_props = ChemProps(card_str = """
                            fuel C3.85H4.85N0.43(S)  C 3.85   H 4.85   N 0.43     wt%=100
                            h,cal=-14.96894578     t(k)=""" + str(k(temperature)) + """  rho.g/cc=1.07
                            """,
                            combustion_efficiency = 0.8,
                            ervme_step = 0.0001)

    ox_tank = Tank(tank_props, injector_props, oxidizer_props)
    comb_chamber = Chamber(chamber_props, grain_props, ambient_props)
    nozzle = Nozzle(nozzle_props, chem_props)

    motor = Motor(ox_tank, comb_chamber, nozzle)
    motor.full_burn(config.time_step, config.min_time, config.max_time, 1 * atm)

    return motor