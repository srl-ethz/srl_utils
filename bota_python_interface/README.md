# Python interface

Python scripts for running Bota Systems sensors.

## PySOEM

PySOEM is a Cython wrapper for the Simple Open EtherCAT Master Library (https://github.com/OpenEtherCATsociety/SOEM).

### Introduction

PySOEM enables basic system testing of EtherCAT slave devices with Python.

Features

* input process data read and output process data write
* SDO read and write
* EEPROM read and write
* FoE read and write

### Dependencies

#### Linux

* Python 3
* GCC (installed on your machine)
* Python scripts that use PySOEM must be executed under administrator privileges

#### Windows

* [Python 3 / 64 Bit](https://www.python.org/downloads/) or through Microsoft Store
* [Npcap](https://nmap.org/npcap/)* or [WinPcap](https://www.winpcap.org/)

[*] Make sure you check "Install Npcap in WinPcap API-compatible Mode" during the install

### Installation

#### Linux
Install pysoem with `sudo` rights because scripts that use PySOEM must be executed under administrator privileges.
```
  sudo pip install pysoem
```

#### Windows
```
  pip install pysoem
```

### Usage

#### Linux
Find the network adapter, the following script lists the available adapters
```
  python3 examples/find_ethernet_adapters.py
```

**The following scripts need to be run as root**

Read input data (PDO) and unpack it for printing
```
  python3 examples/bota_ethercat_minimal_example.py <adapter>
```

Read input data (PDO) in a separate thread, monitor ethercat communication
```
  python3 examples/bota_ethercat_basic_example.py <adapter>
```

#### Windows
Find the network adapter, the following script lists the available adapters
```
  python examples\find_ethernet_adapters.py
```
Choose the right adapter. The format of the adapter name is like \Device\NPF_{XXXX-XXXX-XXXX-XXXX-XXXX}

Read input data (PDO) and unpack it for printing
```
  python examples\bota_ethercat_minimal_example.py <adapter>
```

Read input data (PDO) in a separate thread, monitor ethercat communication
```
  python examples\bota_ethercat_basic_example.py <adapter>
```

## PySerial

### Dependencies

[pySerial](https://pyserial.readthedocs.io/en/latest/)

### Installation

```
  pip install pyserial
  pip install crc
```

### Usage

Find the port the device is connected to (e.g. COM1 on Windows or /dev/ttyUSB0 on Linux)

#### Linux
```
  python3 examples/bota_serial_example.py <port>
```

#### Windows
```
  python examples/bota_serial_example.py <port>
```