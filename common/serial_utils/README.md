# Serial Communication Utilities

Common library functions for UART, SPI, and I2C communication protocols used across F1Tenth utility modules.

## Overview

This directory contains reusable communication helper functions that standardize serial protocols across different modules in the F1Tenth utilities collection.

## Included Protocols

### UART (Universal Asynchronous Receiver-Transmitter)
- Standard baud rate configurations
- Error handling and timeout management
- Buffer management utilities

### SPI (Serial Peripheral Interface)
- Master/Slave configuration helpers
- Multi-device support functions
- Clock speed optimization

### I2C (Inter-Integrated Circuit)
- Device scanning and detection
- Multi-master support
- Address conflict resolution

## Usage

Include the appropriate header files in your project:

```cpp
#include "uart_utils.h"
#include "spi_utils.h"
#include "i2c_utils.h"
```

## Files Structure

```
serial_utils/
├── README.md          # This file
├── uart_utils.h       # UART helper functions
├── uart_utils.cpp     # UART implementations
├── spi_utils.h        # SPI helper functions
├── spi_utils.cpp      # SPI implementations
├── i2c_utils.h        # I2C helper functions
├── i2c_utils.cpp      # I2C implementations
└── examples/          # Usage examples
    ├── uart_test.cpp
    ├── spi_test.cpp
    └── i2c_test.cpp
```

## Status

🚧 **In Development** - Basic structure created, implementation in progress.

---

*Part of the F1Tenth Utilities Collection*
