# Viskous Phoenix Roaster Firmware - Micropython

### [MicroPython Setup](https://micropython.org/download/esp32/)
[MicroPython Tutorial](https://docs.micropython.org/en/latest/esp32/tutorial/intro.html)
<br/>Erase flash:
<br/>`esptool.py --chip esp32 --port /dev/cu.SLAB_USBtoUART erase_flash`

Program firmware starting at address 0x1000:
<br/>`esptool.py --chip esp32 --port /dev/cu.SLAB_USBtoUART --baud 460800 write_flash -z 0x1000 esp32-idf4-20191220-v1.12.bin`

### Mac [Serial Monitor](https://pbxbook.com/other/mac-tty.html)
`screen -L /dev/cu.SLAB_USBtoUART 115200`
<br/>QUIT: CTRL-A + CTRL-\
<br/>SCROLL: CTRL-A + ESC

### [Upload package](https://www.cnx-software.com/2017/10/16/esp32-micropython-tutorials/)
`ampy --port /dev/cu.SLAB_USBtoUART put main.py`

### [upip install](https://lemariva.com/blog/2018/03/tutorial-installing-dependencies-on-micropython)
A wifi connector function is available in the `utils.py` file:
<br/>`import utils`
<br/>`utils.wifi_connect(<ssid>, <password>)`
Ensure the response is `true`, if not, run again.
<br/>`import upip`
<br/>`upip.install(<lib name as string>)`

## Python common commands
List directory: `os.listdir()`
<br/>Open file: `f = open(<filename>, 'r')`, `print(f.read())`
<br/>Delete file: `os.remove(<filename>)`
<br/>Delete empty directory: `os.rmdir(<dirname>)`