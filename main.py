from machine import Pin
import utime

from roaster import Roaster, ROASTER_STATUS


CYCLE_DELAY = 100 #milliseconds
PIN_BUTTON = Pin(34, Pin.IN)
BUTTON_PRESS_DELAY = 8 #seconds
button_press_time = 0

roaster = Roaster(CYCLE_DELAY)
# Activate and assign services and interrupt request methods
while not roaster.ble.ble.active():
    # Activate ESP32's Bluetooth module
    roaster.ble.ble.active(True)

roaster.ble.register()
roaster.ble.advertise()

print("SETUP COMPLETE")

# The run cycle needs to be external to the Roaster
# instance to allow Roaster reset and other controls
while True:
    # Update variables
    current_time = utime.time()
    print("current_time: ", current_time)
    roaster.time_current = current_time
    roaster.temp_update()

    # Check which cycle, if any, needs to run
    if roaster.status == ROASTER_STATUS.ROAST:
        roaster.roast_cycle()
    elif roaster.status == ROASTER_STATUS.COOL:
        roaster.cool_cycle()
    
    # Notify the roast data
    roaster.roast_notify()

    # Handle the button
    print("ROASTER BUTTON: ", PIN_BUTTON.value())
    if PIN_BUTTON.value() == 1:
        print("ROASTER BUTTON PRESSED: ", button_press_time)
        if button_press_time == 0:
            # This is the first time the button was pressed, start the delay counter
            button_press_time = current_time
        elif (current_time - button_press_time) > BUTTON_PRESS_DELAY:
            print("RESET ROASTER")
    else:
        # Reset the button press start time
        button_press_time = 0
    
    # utime.sleep_ms(self.CYCLE_DELAY)
    utime.sleep_ms(1000)

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