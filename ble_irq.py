from micropython import const

# Define constants for BLE IRQ
_IRQ_ALL = const(0xffff)
_IRQ_CENTRAL_CONNECT                 = const(1 << 0)
_IRQ_CENTRAL_DISCONNECT              = const(1 << 1)
_IRQ_GATTS_WRITE                     = const(1 << 2)
_IRQ_GATTS_READ_REQUEST              = const(1 << 3)
_IRQ_SCAN_RESULT                     = const(1 << 4)
_IRQ_SCAN_COMPLETE                   = const(1 << 5)
_IRQ_PERIPHERAL_CONNECT              = const(1 << 6)
_IRQ_PERIPHERAL_DISCONNECT           = const(1 << 7)
_IRQ_GATTC_SERVICE_RESULT            = const(1 << 8)
_IRQ_GATTC_CHARACTERISTIC_RESULT     = const(1 << 9)
_IRQ_GATTC_DESCRIPTOR_RESULT         = const(1 << 10)
_IRQ_GATTC_READ_RESULT               = const(1 << 11)
_IRQ_GATTC_WRITE_STATUS              = const(1 << 12)
_IRQ_GATTC_NOTIFY                    = const(1 << 13)
_IRQ_GATTC_INDICATE                  = const(1 << 14)

# # Main event handler function
# def ble_irq(event, data):
#     if event == _IRQ_CENTRAL_CONNECT:
#         # A central has connected to this peripheral.
#         # NOTE: Default behavior of normal devices are acting as centrals, not peripherals.
#         conn_handle, addr_type, addr = data
#         print('bt irq', event, data)
        
#     elif event == _IRQ_CENTRAL_DISCONNECT:
#         # A central has disconnected from this peripheral.
#         conn_handle, addr_type, addr = data
#         # Start advertising again to allow a new connection.
#         adv()
    
#     elif event == _IRQ_SCAN_RESULT:
#         # A single scan result.
#         addr_type, addr, connectable, rssi, adv_data = data
#         # For addr_type, 0 is public device address, while 1 is random device address.
#         # No Resolvable Private Addresses are advertised (since Bluetooth v4.0) due to privacy reasons.
#         # Even though some older devices might still emit their RPAs, this still remains a stubborn issue.
#         # print(addr_type, bytes(addr), adv_decode_name(adv_data))
#         print(addr_type, bytes(addr), adv_data)

#     elif event == _IRQ_SCAN_COMPLETE:
#         # Scan duration finished or manually stopped.
#         print('Scan complete!')

#     elif event == _IRQ_PERIPHERAL_CONNECT:
#         # Connect successful.
#         conn_handle, addr_type, addr = data
#         peripheralVk.gattc_discover_services(conn_handle)
    
#     elif event == _IRQ_PERIPHERAL_DISCONNECT:
#         # Disconnect (either initiated by us or the remote end).
#         conn_handle, addr_type, addr = data

#     elif event == _IRQ_GATTC_SERVICE_RESULT:
#         # Connected device returned a service.
#         conn_handle, start_handle, end_handle, uuid = data
#         peripheralVk.gattc_discover_characteristics(conn_handle, start_handle, end_handle)
    
#     elif event == _IRQ_GATTC_CHARACTERISTIC_RESULT:
#         # Connected device returned a characteristic.
#         conn_handle, def_handle, value_handle, properties, uuid = data
#         print(data)
        
#     elif event == _IRQ_GATTC_READ_RESULT:
#         # A read completed successfully.
#         conn_handle, value_handle, char_data = data
#         print(data)
        
#     elif event == _IRQ_GATTC_NOTIFY:
#         # The script periodically notifies its value.
#         conn_handle, value_handle, notify_data = data
#         print(data)