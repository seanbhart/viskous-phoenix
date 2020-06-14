from micropython import const
import machine
import ubluetooth
import utime

import ble_advertising


# class BLE_CHARACTERISTIC():
#     STATUS = 1
#     SETTINGS = 2
#     ROAST = 3


class Ble:
    # Define constants for BLE IRQ
    IRQ_ALL = const(0xffff)
    IRQ_CENTRAL_CONNECT                 = const(1 << 0)
    IRQ_CENTRAL_DISCONNECT              = const(1 << 1)
    IRQ_GATTS_WRITE                     = const(1 << 2)
    IRQ_GATTS_READ_REQUEST              = const(1 << 3)
    IRQ_SCAN_RESULT                     = const(1 << 4)
    IRQ_SCAN_COMPLETE                   = const(1 << 5)
    IRQ_PERIPHERAL_CONNECT              = const(1 << 6)
    IRQ_PERIPHERAL_DISCONNECT           = const(1 << 7)
    IRQ_GATTC_SERVICE_RESULT            = const(1 << 8)
    IRQ_GATTC_CHARACTERISTIC_RESULT     = const(1 << 9)
    IRQ_GATTC_DESCRIPTOR_RESULT         = const(1 << 10)
    IRQ_GATTC_READ_RESULT               = const(1 << 11)
    IRQ_GATTC_WRITE_STATUS              = const(1 << 12)
    IRQ_GATTC_NOTIFY                    = const(1 << 13)
    IRQ_GATTC_INDICATE                  = const(1 << 14)

    ### Initialize UUIDs and tuples
    # UUID_VALUE_SERVICE_GEN = int(0x1801)
    # UUID_VALUE_CHAR_STATUS_CHANGE = int(0x2A05)
    # UUID_SERVICE_GEN = ubluetooth.UUID(UUID_VALUE_SERVICE_GEN)
    # CHAR_STATUS_CHANGE = (ubluetooth.UUID(UUID_VALUE_CHAR_STATUS_CHANGE), ubluetooth.FLAG_READ,)
    # SERVICE_GEN = (UUID_SERVICE_GEN, (CHAR_STATUS_CHANGE,),)

    UUID_VALUE_SERVICE = "87916f94-2485-4e33-b6b8-9d4bd3f7a148"
    UUID_VALUE_CHAR_STATUS = "f7ef1eb9-c7ce-42a3-b781-7426420837ab"
    UUID_VALUE_CHAR_SETTINGS = "96797478-bd6c-4b0a-a3e9-018b56eacdf7"
    UUID_VALUE_CHAR_ROAST = "d5491592-0d80-4cfb-8f92-279b54f68814"
    BLE_UUID_SERVICE = ubluetooth.UUID(UUID_VALUE_SERVICE)
    BLE_CHAR_STATUS = (ubluetooth.UUID(UUID_VALUE_CHAR_STATUS), ubluetooth.FLAG_NOTIFY | ubluetooth.FLAG_READ | ubluetooth.FLAG_WRITE,)
    BLE_CHAR_SETTINGS = (ubluetooth.UUID(UUID_VALUE_CHAR_SETTINGS), ubluetooth.FLAG_READ | ubluetooth.FLAG_WRITE,)
    BLE_CHAR_ROAST = (ubluetooth.UUID(UUID_VALUE_CHAR_ROAST), ubluetooth.FLAG_NOTIFY,)
    BLE_SERVICE = (BLE_UUID_SERVICE, (BLE_CHAR_STATUS, BLE_CHAR_SETTINGS, BLE_CHAR_ROAST,),)
    BLE_SERVICES = (BLE_SERVICE,)

    ### Initialize variables
    ble = ubluetooth.BLE() # BLE singleton
    connected = False
    connections = set()
    handle_status = 0
    handle_settings = 0
    handle_roast = 0
    
    # command should have a callback
    @property
    def command(self):
        return self._command
    @command.setter
    def command(self, command):
        self._command = command
        self._notify_command_observers(command)
    _command_callbacks = []
    def _notify_command_observers(self, command):
        for callback in self._command_callbacks:
            callback(command)
    def register_command_callback(self, callback):
        self._command_callbacks.append(callback)

    ### BLE methods
    def register(self):
        ((self.handle_status, self.handle_settings, self.handle_roast),) = self.ble.gatts_register_services(self.BLE_SERVICES)
        self.ble.irq(self.irq, self.IRQ_ALL)
        print('BLE current mac address: ', self.ble.config('mac'))
        print("handle_status: ", self.handle_status)
        print("handle_settings: ", self.handle_settings)
        print("handle_roast: ", self.handle_roast)

    def advertise(self):
        # Indicate GATT service name in reverse byte order in second argument of adv_encode(0x03, b'')
        # List of services: https://www.bluetooth.com/specifications/gatt/services/
        # ble.gap_advertise(100, adv_encode(0x01, b'\x06') + adv_encode(0x03, b'\x15\x18') + adv_encode(0x19, b'\xc1\x03') + adv_encode_name('deLIGHTer'))
        # ble.gap_advertise(100, bytearray("\x02\x01\x02") + adv_encode(0x03, b'\x34\x39\x66\x36\x31\x39\x37\x38') + adv_encode_name("Vk"))
        payload = ble_advertising.advertising_payload(
            name="Vk",
            services=[self.BLE_UUID_SERVICE],
        )
        self.ble.gap_advertise(100, payload)
    
    def notify(self, handle, data):
        print('Ble - notify')
        for conn_handle in self.connections:
            print('Ble - notifying conn_handle: ', conn_handle)
            print('Ble - notifying handle: ', handle)
            print('Ble - notifying data: ', data)
            # Notify all connected centrals
            self.ble.gatts_notify(conn_handle, handle, data)

    # Main event handler function
    def irq(self, event, data):
        print('bt irq', event, data)
        if event == self.IRQ_CENTRAL_CONNECT:
            # A central has connected to this peripheral.
            conn_handle, addr_type, addr = data
            # Add the connection to the list
            self.connections.add(conn_handle)
            self.connected = True
            print('_IRQ_CENTRAL_CONNECT: ', conn_handle, addr_type, addr)
        
        elif event == self.IRQ_CENTRAL_DISCONNECT:
            # A central has disconnected from this peripheral.
            conn_handle, addr_type, addr = data
            # Remove the connection
            self.connections.remove(conn_handle)
            self.connected = False
            print('_IRQ_CENTRAL_DISCONNECT: ', conn_handle, addr_type, addr)
            # Start advertising again to allow a new connection.
            self.advertise()
        
        elif event == self.IRQ_GATTS_WRITE:
            # A central has written to this characteristic or descriptor.
            conn_handle, attr_handle = data
            print('_IRQ_GATTS_WRITE: ', conn_handle, attr_handle)
            received_data = self.ble.gatts_read(attr_handle)
            print(received_data)
            if attr_handle == self.handle_status:
                self.command = received_data
