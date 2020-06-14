from machine import SPI, Pin
import json

from ble import Ble
from simple_pid import PID
import max31855


class ROASTER_STATUS():
    NA = 1
    READY = 2
    ROAST = 3
    COOL = 4

    @classmethod
    def string_to_status(self, string):
        if string == "READY":
            return ROASTER_STATUS.READY
        elif string == "ROAST":
            return ROASTER_STATUS.ROAST
        elif string == "COOL":
            return ROASTER_STATUS.COOL
        else:
            return ROASTER_STATUS.NA

    @classmethod
    def status_to_string(self, s):
        if s == ROASTER_STATUS.READY:
            return "READY"
        elif s == ROASTER_STATUS.ROAST:
            return "ROAST"
        elif s == ROASTER_STATUS.COOL:
            return "COOL"
        else:
            return "NA"


class COIL():
    OFF = 1
    ON = 2


class Max31855:
    thermocouple = max31855.MAX31855

    def __init__(self):
        _PIN_DO = 35
        _PIN_CS = 32
        _PIN_CLK = 33
        _miso = Pin(_PIN_DO, Pin.IN)
        _sck = Pin(_PIN_CLK, Pin.OUT)
        _cs = Pin(_PIN_CS, Pin.OUT)
        _spi = SPI(1, baudrate=1000000, sck=_sck, miso=_miso)
        self.thermocouple = max31855.MAX31855(_spi, _cs)


class ColorLed:
    PIN_LED_RED     = Pin(5, Pin.OUT)
    PIN_LED_GREEN   = Pin(16, Pin.OUT)
    PIN_LED_BLUE    = Pin(17, Pin.OUT)

    def off(self):
        self.PIN_LED_RED.value(1)
        self.PIN_LED_GREEN.value(1)
        self.PIN_LED_BLUE.value(1)
    def white(self):
        self.PIN_LED_RED.value(0)
        self.PIN_LED_GREEN.value(0)
        self.PIN_LED_BLUE.value(0)
    def red(self):
        self.PIN_LED_RED.value(0)
        self.PIN_LED_GREEN.value(1)
        self.PIN_LED_BLUE.value(1)
    def green(self):
        self.PIN_LED_RED.value(1)
        self.PIN_LED_GREEN.value(0)
        self.PIN_LED_BLUE.value(1)
    def blue(self):
        self.PIN_LED_RED.value(1)
        self.PIN_LED_GREEN.value(1)
        self.PIN_LED_BLUE.value(0)
    def yellow(self):
        self.PIN_LED_RED.value(0)
        self.PIN_LED_GREEN.value(0)
        self.PIN_LED_BLUE.value(1)
    def magenta(self):
        self.PIN_LED_RED.value(0)
        self.PIN_LED_GREEN.value(1)
        self.PIN_LED_BLUE.value(0)
    def cyan(self):
        self.PIN_LED_RED.value(1)
        self.PIN_LED_GREEN.value(0)
        self.PIN_LED_BLUE.value(0)


class Roaster:
    def __init__(self, CYCLE_DELAY):
        self.CYCLE_DELAY = CYCLE_DELAY
        # Initialize the Ble instance and pass the callback method
        self.ble = Ble()
        self.ble.register_command_callback(self.ble_status_listener)
        # Set the roaster to the READY state
        self.set_READY()

    ########## SETTINGS ##########
    PIN_SYSTEM      = Pin(18, Pin.OUT) 
    PIN_COIL        = Pin(19, Pin.OUT)
    color_led = ColorLed()
    color_led.magenta()

    CYCLE_DELAY = 100 #milliseconds

    ########## STATUS & BLE ##########
    status = ROASTER_STATUS.NA
    # Set the passed status, convert to an int and notify via BLE
    def set_status_and_notify(self, status):
        self.status = status
        string = ROASTER_STATUS.status_to_string(self.status)
        
        # BLE notify the status update
        self.ble.notify(self.ble.handle_status, string)
    
    # Set a listener method for the `command` variable in Ble
    def ble_status_listener(self, new_status_bytes):
        new_status_string = new_status_bytes.decode("utf-8")
        print("new_status_string: ", new_status_string)
        new_status = ROASTER_STATUS.string_to_status(new_status_string)
        # Do not set the status directly - call the appropriate method
        # and the status will be updated when device changes are complete
        if new_status == ROASTER_STATUS.READY:
            self.set_READY()
        elif new_status == ROASTER_STATUS.ROAST:
            self.set_ROAST()
        elif new_status == ROASTER_STATUS.COOL:
            self.set_COOL()
        else:
            print("ERROR: new_status invalid")

    ########## THERMOCOUPLE ##########
    thermocouple = Max31855().thermocouple
    # Read the thermocouple but check that the temp is not an outlier
    # If the new reading is 10C or more different than the last
    # stored temp, do not use the new reading, just pass the last stored temp
    def temp_update(self):
        temp_new = self.thermocouple.read()
        print("temp_new: ", temp_new)
        # Be sure to use the absolute value difference
        # to skip outlier thermocouple readings
        temp_diff = abs(temp_new - self.temp_current)
        if temp_diff < 10:
            self.temp_current = temp_new
        print("temp_current: ", self.temp_current)

    ########## PID & ROAST CURVE ##########
    # Set the duration (s) to heat the chamber before PID activated
    ROAST_PRIMETIME = 8
    # Start the curve at 25C or 75F
    ROAST_CURVE_TEMP_ROOM = 25
    ROAST_CURVE_TEMP_MAX = 250
    ROAST_CURVE = 100
    # Default Other Roast settings
    ROAST_TIME_MAX = 420 #seconds

    PID_OUTPUT = 0
    PID_COIL_TIME_MAX = 600 #seconds
    PID_COIL_TIME_EST = 0 #seconds
    PID_P = 2
    PID_I = 1
    PID_D = 10
    #PID(double* Input, double* Output, double* Setpoint,double Kp, double Ki, double Kd, int ControllerDirection)
    #PID PID1(&tempCurrent, &output, &tempCurve, kP, kI, kD, DIRECT);
    pid = PID(PID_P, PID_I, PID_D, setpoint=1)
    pid.sample_time = CYCLE_DELAY / 1000 #seconds
    pid.output_limits = (0, PID_COIL_TIME_MAX)
    
    # Bundle the PID settings into JSON format to be sent to the app
    def pid_settings_create_json(self):
        j = {
            "kP": self.PID_P,
            "kI": self.PID_I,
            "kD": self.PID_D,
            "primeTime": self.ROAST_PRIMETIME,
            "roomTemp": self.ROAST_CURVE_TEMP_ROOM,
            "maxTemp": self.ROAST_CURVE_TEMP_MAX,
            "curve": self.ROAST_CURVE,
            "timeMax": self.ROAST_TIME_MAX,
        }
        return json.dumps(j)

    ########## ROAST DATA ##########
    coil = COIL.OFF
    time_current = 0         # Time since last reset
    time_start = 0           # Time of roast start
    time_roast = 0           # Roast duration
    time_last = 0            # Time of last measurement
    time_last_notify = 0     # Time of last notification
    time_coil_on = 0         # Time coil turned on

    temp_curve = 0.0
    temp_initial = 0.0
    temp_last = 0.0
    temp_current = 0.0

    def roast_notify(self):
        print("Roaster - roast_notify")
        if self.ble.connected:
            print("Roaster - roast_notify - connected")
            # Bluetooth stack will go into congestion if too many packets are sent (>=100ms)
            # Notify every: .5 second (needs to be faster than app data so that timing issues don't cause <1 sec app data)
            if self.temp_current - self.time_last_notify < 500:
                print("Roaster - roast_notify - temp check")
                # Convert the RoastReading components to json and notify
                d = {
                    "time": self.time_roast,
                    "temp": self.temp_current,
                }
                self.ble.notify(self.ble.handle_roast, json.dumps(d))
                # Update the notification time to the data gathered time
                self.time_last_notify = self.time_current
    
    # Run continuously when on ROAST
    def roast_cycle(self):
        print("ROAST CYCLE")

        # Calculate the amount of time the beans have been roasting
        self.time_roast = self.time_current - self.time_start

        # # Update the temp reading
        # updateTemp()

        # If the maximum allowed time has been reached, start the cool cycle
        if self.time_roast >= self.ROAST_TIME_MAX:
            self.set_COOL()
        elif self.time_roast < (self.ROAST_PRIMETIME * 1000):
            # Chamber Priming: First run a standard program to stabilize the temp at expected (half fill) level
            # then engage PID to maintain the curve

            # # Handle BLE roast data notification
            # notifyRoastData()

            self.PIN_COIL.value(1)
            self.coil = COIL.ON
            
        else:
            # If it has been at least _ ms since the last temp check, run it again
            # DO NOT set at less than 500ms if a machanical relay is used (not SSR)
            if self.time_current - self.time_last >= 500:

                # # Handle BLE roast data notification
                # notifyRoastData();
            
                # Calculate the ideal roast curve temp based on the passed roast time
                # tempCurve = tempInitial + ((250 * (timeRoast / 1000)) / (100 + (timeRoast / 1000)))
                self.temp_curve = self.ROAST_CURVE_TEMP_ROOM + ((self.ROAST_CURVE_TEMP_MAX * (self.time_roast / 1000)) / (self.ROAST_CURVE + (self.time_roast / 1000)))
            
                # The PID equation will estimate how many additional seconds the coil needs to be on
                # to match the roast curve target temp. The PID equation will max out at 60 seconds
                # so if the output is equal to 60, just keep the coil on.
            
                # IMPORTANT: Multiply the output by 1000 to convert from seconds to microseconds
                self.PID_COIL_TIME_EST = self.PID_OUTPUT * 1000
            
                # Determine if the coil should be on or not
                # If the estimated coil time is 60, that is the max, so just keep the coil on
                if self.PID_COIL_TIME_EST >= 60:
                    self.PIN_COIL.value(1)
                    print("COIL ON")
                elif self.PID_COIL_TIME_EST > self.time_current - self.time_coil_on:
                    # If the estimated coil time on is greater than the time passed since it was last turned on, it should be on
                    # Check whether the coil is already on, if not, turn it on and reset the coil time on indicator
                    if self.coil == COIL.OFF:
                        self.PIN_COIL.value(1)
                        self.time_coil_on = self.time_current
                        self.coil = COIL.ON
                    
                    print("COIL ON")
                
                else:
                    # If the estimated coil time on is less than or equal to the time passed since it was last turned on, it should be off
                    # Set the signal to LOW again just to be sure
                    self.PIN_COIL.value(0)
                    self.coil = COIL.OFF
                    print("COIL OFF")
                
                self.time_last = self.time_current

    # Run ONCE when the device is set to NA (default/unknown status)
    def set_NA(self):
        # In case of bug, ensure the coils are off as indicated
        self.PIN_COIL.value(0)
        self.PIN_SYSTEM.value(0)

        # Set status and notify
        self.set_status_and_notify(ROASTER_STATUS.NA)
        print("SYSTEM STATUS NA")
    
    # Run ONCE when the device is set to READY
    def set_READY(self):
        # Turn off the system (all coils & fan) - ensure the coil relay is also off
        self.PIN_COIL.value(0)
        self.PIN_SYSTEM.value(0)
        # Set the LED to indicate the roast is off
        self.color_led.blue()

        # Set status and notify
        self.set_status_and_notify(ROASTER_STATUS.READY)
        print("SYSTEM STATUS READY")
    
    # Run ONCE when the device is set to ROAST
    def set_ROAST(self):
        # Set the roast start time and initially set the last reading time
        # (last reading time is needed to limit the relay toggle time)
        self.time_start = self.time_current
        self.time_last = self.time_current
        self.time_last_notify = self.time_current
        # Update the temp reading
        self.temp_update()
        # Set the roast initial temp to the current temp
        self.temp_initial = self.temp_current
        print("Initial Temp = ", self.temp_initial)

        # Turn on the coils and switch the LED
        self.PIN_SYSTEM.value(1)
        self.color_led.red()

        # Set status and notify
        self.set_status_and_notify(ROASTER_STATUS.ROAST)
        print("SYSTEM STATUS ROAST")

        # Run the roast cycle the first time (loop will continue directly)
        self.roast_cycle()
    
    # Run continuously when on COOL
    def cool_cycle(self):
        # Continue to calculate roast time & chamber temp for data reporting
        self.time_roast = self.time_current - self.time_start
        # self.temp_update()
        # # Handle BLE roast data notification
        # notifyRoastData();
        # If the temp is lower than 55C (if using RTD, use higher temp since probe will lag)
        if self.temp_current <= 55:
            self.set_READY()
    
    # Run ONCE when the device is set to COOL
    def set_COOL(self):
        # Turn off the coil
        self.PIN_COIL.value(0)
        self.color_led.yellow()
        # set the stage to cooling
        self.set_status_and_notify(ROASTER_STATUS.COOL)
        print("SYSTEM STATUS COOLING")

        # Start the first cool cycle (loop will continue)
        self.cool_cycle()
