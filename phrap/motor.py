from dataclasses import dataclass

from .modules.units import *

from .modules.curve import Curve
from .modules.ccsv import save
import copy
import traceback

@dataclass
class AmbientState:
    pressure: float

class Motor:
    def __init__(self, tank, chamber, nozzle, pressure_curve: Curve = None):
        self.tank = tank
        self._tank_state = None
        self.chamber = chamber
        self._chamber_state = None
        self.nozzle = nozzle
        self._nozzle_state = None
        self.pressure_curve = pressure_curve
        self.data = Curve()
        self.time = 0

        self._time_step = 0.01

    def full_burn(self, time_step, min_time, max_time, ambient_pressure):
        try:
            self._time_step = time_step
            tank = copy.deepcopy(self.tank)
            chamber = copy.deepcopy(self.chamber)
            nozzle = copy.deepcopy(self.nozzle)

            tank_state = tank.initialize_state()
            chamber_state = chamber.initialize_state()
            nozzle_state = nozzle.initialize_state()
            ambient_state = AmbientState(pressure=ambient_pressure)

            t = 0
            max_thrust = 0

            thrust_curve_stop = 0.05
            while ((t <= max_time) and (tank_state.total_mass > 0) and (nozzle_state.thrust > thrust_curve_stop * max_thrust or nozzle_state.thrust == max_thrust)) or (t < min_time):
                print("Time:", round(t,2), "s")
                ambient_state = AmbientState(pressure=ambient_pressure)
                if self.pressure_curve is not None:
                    ambient_state.pressure = self.pressure_curve.lookup({"time": t}, "pressure")
                tank_state = tank.blow(chamber_state, time_step)
                chamber_state = chamber.combust(tank_state, nozzle_state, time_step)
                nozzle_state = nozzle.choke(chamber_state, ambient_state, time_step)

                telemetry = {"Ambient Pressure (atm)": ambient_state.pressure / atm}
                telemetry.update({"Time (s)": t})
                telemetry.update(tank.telemetry)
                telemetry.update(chamber.telemetry)
                telemetry.update(nozzle.telemetry)
                self.data.append(telemetry)

                max_thrust = max([nozzle_state.thrust, max_thrust])

                t += time_step
        except:
            print(traceback.format_exc())
    
    def part_burn(self, time_step, ambient_pressure):
        try:
            tank = self.tank
            chamber = self.chamber
            nozzle = self.nozzle

            if self._tank_state is None:
                tank_state = tank.initialize_state()
            else:
                tank_state = self._tank_state

            if self._chamber_state is None:
                chamber_state = chamber.initialize_state()
            else:
                chamber_state = self._chamber_state

            if self._nozzle_state is None:
                nozzle_state = nozzle.initialize_state()
            else:
                nozzle_state = self._nozzle_state

            ambient_state = AmbientState(pressure=ambient_pressure)
            self._tank_state = tank.blow(chamber_state, time_step)
            self._chamber_state = chamber.combust(tank_state, nozzle_state, time_step)
            self._nozzle_state = nozzle.choke(chamber_state, ambient_state, time_step)
            self.time += time_step

            telemetry = {}
            telemetry.update({"Time (s)": self.time})
            telemetry.update(tank.telemetry)
            telemetry.update(chamber.telemetry)
            telemetry.update(nozzle.telemetry)
            self.data.append(telemetry)

            return telemetry
        except:
            print(traceback.format_exc())

    def save_data(self, file_name):
        save(file_name, self.data.values)

    @property
    def total_impulse(self):
        return sum(self.data.values["Thrust (N)"]) * self._time_step

    @property
    def average_thrust(self):
        return sum(self.data.values["Thrust (N)"]) / len(self.data.values["Thrust (N)"])

    @property
    def average_of_ratio(self):
        return sum(self.data.values["O/F Ratio"]) / len(self.data.values["O/F Ratio"])