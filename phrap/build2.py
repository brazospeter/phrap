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

from .modules.ccsv import load

tank_props = TankProps(volume = 72000 * cc, 
                       ullage = 0.3)
oxidizer_props = OxidizerProps(name = "N2O", 
                               temperature = k(inputs.temperature))
injector_props = InjectorProps(diameter = 0.21 * inch,
                               discharge_coeff_spi = 0.45 * 5,
                               discharge_coeff_gas = 0.7 * 5,
                               discharge_coeff_hem = True)
chamber_props = ChamberProps(volume = 0.01158)
grain_props = GrainProps(density = 910,
                         regression_coefficient = 0.022,
                         regression_exponent = 0.602,
                         length_exponent = 0,
                         inner_diameter = 2.85 * inch,
                         outer_diameter = 5 * inch,
                         length = 31 * inch,
                         file_name = "grain.stl")
ambient_props = AmbientProps(temperature = k(inputs.temperature),
                             pressure = 1.0 * atm,
                             name = "Air")
nozzle_props = NozzleProps(throat_diameter = 1.8 * inch, 
                           expansion_ratio = 4.762,
                           discharge_coefficient = 0.9, 
                           nozzle_efficiency = 0.9)
chem_props = ChemProps(card_str = """
                        fuel C3.85H4.85N0.43(S)  C 3.85   H 4.85   N 0.43     wt%=100
                        h,cal=-14.96894578     t(k)=""" + str(k(inputs.temperature)) + """  rho.g/cc=1.07
                        """,
                        combustion_efficiency = 0.8,
                        ervme_step = 0.0001)

ox_tank = Tank(tank_props, injector_props, oxidizer_props)
comb_chamber = Chamber(chamber_props, grain_props, ambient_props)
nozzle = Nozzle(nozzle_props, chem_props)

pressure_curve = load("pressure.csv", key_mapping = {"time": 0, "pressure": 1})

motor = Motor(ox_tank, comb_chamber, nozzle, pressure_curve)
motor.full_burn(config.time_step, config.min_time, config.max_time, 1 * atm)