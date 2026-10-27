from phrap.build import motor
from phrap.modules.units import *

time_step = 0.01
min_time = 1
thrust = 0

while motor.time < min_time or thrust > 0:
    telemetry = motor.part_burn(time_step, 1 * atm) # motor.part_burn() returns a dictionary of telemetry data for the current time step
    # parameters are time_step (in seconds) and ambient_pressure (in pascals)
    # you can see what parameters are available in the telemetry dictionary in the saved data
    thrust = telemetry["Thrust (N)"]
    print("Time:", round(telemetry["Time (s)"], 2), "s", "Thrust:", round(thrust, 2), "N")

motor.save_data("test_rocket") # saves all data from telemetry collected, optional