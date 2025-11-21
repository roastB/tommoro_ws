from conveyor import ConveyorController


ctrl = ConveyorController({'a':'/dev/ttyUSB0'})


ctrl.command('a', direction='backward', speed=30, time=100000)


