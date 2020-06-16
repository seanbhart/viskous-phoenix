from machine import Pin
import utime

from roaster import Roaster, ROASTER_STATUS
from utils import log_custom, reset_log_custom
import logger
# import utils


# # Reset the log file
# reset_log_custom()

CYCLE_DELAY = 100 #milliseconds
PIN_BUTTON = Pin(34, Pin.IN)
BUTTON_PRESS_DELAY = 8000 #milliseconds
button_press_time = 0

roaster = Roaster(CYCLE_DELAY)
# Activate and assign services and interrupt request methods
while not roaster.ble.active:
    # Activate ESP32's Bluetooth module
    roaster.ble.active = True

roaster.ble.register()
roaster.ble.advertise()

# Prepare the temp variables
# give the MAX time to settle
utime.sleep_ms(500)
roaster.temp_current = roaster.thermocouple.read()

print("SETUP COMPLETE")
# logger.info("SETUP COMPLETE-logger")
# utils.log_firebase('main','SETUP COMPLETE')

# The run cycle needs to be external to the Roaster
# instance to allow Roaster reset and other controls
while True:
    # Update variables - time always use milliseconds
    current_time = utime.time() * 1000
    # print("current_time: ", current_time)
    roaster.time_current = current_time
    roaster.temp_update()

    # Check which cycle, if any, needs to run
    if roaster.status == ROASTER_STATUS.ROAST:
        roaster.roast_cycle()
    elif roaster.status == ROASTER_STATUS.COOL:
        roaster.cool_cycle()
    
    # # Notify the roast data
    roaster.roast_notify()

    # Handle the button
    if PIN_BUTTON.value() == 1:
        # utils.log_firebase('main','button press')
        if button_press_time == 0:
            # This is the first time the button was pressed, start the delay counter
            button_press_time = current_time
        elif (current_time - button_press_time) > BUTTON_PRESS_DELAY:
            print('RESET ROASTER')
            # logger.info("RESET ROASTER")
    else:
        # Reset the button press start time
        button_press_time = 0
    
    utime.sleep_ms(CYCLE_DELAY)
    # utime.sleep_ms(3000)

    # roaster.set_ROAST()
    # utime.sleep_ms(3000)
    # roaster.set_COOL()
    # utime.sleep_ms(3000)
    # roaster.set_READY()

    # Update PID -- TODO: ADD PID UPDATE TO ROAST CYCLE
    # # compute new ouput from the PID according to the systems current value
    # control = pid(v)
    # # feed the PID output to the system and get its current value
    # v = controlled_system.update(control)