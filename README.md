# Viskous Phoenix Roaster Firmware - Micropython

## [MicroPython Setup](https://micropython.org/download/esp32/)
[MicroPython Tutorial](https://docs.micropython.org/en/latest/esp32/tutorial/intro.html)
<br/>Erase flash:
<br/>`esptool.py --chip esp32 --port /dev/cu.SLAB_USBtoUART erase_flash`

Program firmware starting at address 0x1000:
<br/>`esptool.py --chip esp32 --port /dev/cu.SLAB_USBtoUART --baud 460800 write_flash -z 0x1000 esp32-idf4-20191220-v1.12.bin`

## Mac [Serial Monitor](https://pbxbook.com/other/mac-tty.html)
`screen /dev/cu.SLAB_USBtoUART 115200`
<br/>QUIT: CTRL-A, CTRL-\

## [Upload package](https://www.cnx-software.com/2017/10/16/esp32-micropython-tutorials/)
ampy --port /dev/cu.SLAB_USBtoUART put main.py

