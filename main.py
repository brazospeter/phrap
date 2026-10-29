from phrap.build_nh import motor
from phrap.modules.curve import Curve

from phrap.modules.units import *

file_name = "new_horizon_v1.4.3.2"

motor.save_data(file_name)
motor.save_eng(file_name, 6 * inch, 137.8 * inch, 0.5, ["; Brazoswood New Horizon, 3 bottle w/ 300 PSI drop, 85% C* efficiency", "; from PHRAP", "; created by Peter Nguyen 10/2026"])