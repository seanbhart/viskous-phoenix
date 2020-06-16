import network
import urequests


def log_custom(string):
    # Print for serial output
    print(string)

    # # Append string to log file
    # log_file = open("log.txt", "a")  # append mode 
    # log_file.write(string) 
    # log_file.close()

def reset_log_custom():
    print("RESET LOG")
    # log_file = open("log.txt", "w")  # append mode 
    # log_file.write('----- BEGIN LOG -----') 
    # log_file.close()

def wifi_connect(ssid_, wp2_pass):
    sta_if = network.WLAN(network.STA_IF)

    sta_if.active(True)
    sta_if.connect(ssid_, wp2_pass)
    print(sta_if.isconnected())

def log_firebase(key, value):
    data = '{"%s":"%s"}' % (key,value)
    # print('Firebase logging: ', data)
    response = urequests.post('https://viskousroast.firebaseio.com/log/tests.json', data = data)
    # print(response.text)
    # print(response.json())