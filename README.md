# F1Tenth Utilities & Pit Lane Modules

A collection of utility modules and hardware projects designed for F1Tenth autonomous racing cars. This repository contains various microcontroller-based modules for timing, data display, and communication that enhance the racing experience and provide valuable telemetry.

## 🏎️ Project Overview

This repository serves as a centralized collection of utility modules for F1Tenth racing projects, including:
- Lap timing systems
- Data display modules
- Serial communication utilities
- PCB designs and firmware for race-oriented hardware

## 📁 Repository Structure

```
f1tenth-utils/
│
├── README.md               # This file
├── LICENSE                 # Project license
├── docs/                   # Global documentation and guides
├── common/                 # Shared utility code
│   └── serial_utils/       # UART/SPI/I2C communication helpers
│
├── lap_timer/              # Lap timing measurement and display system
│   ├── firmware/           # Microcontroller code (Arduino/PlatformIO)
│   ├── pcb_design/         # KiCAD PCB design files
│   ├── docs/               # Lap timer specific documentation
│   └── README.md          # Lap timer module documentation
│
└── display_module/         # Future: OLED/LCD data display module
```

## 🚀 Getting Started

### Prerequisites
- Arduino IDE or PlatformIO for firmware development
- KiCAD for PCB design viewing/editing
- Basic knowledge of microcontrollers (Arduino, ESP32, etc.)

### Quick Start
1. Clone this repository:
   ```bash
   git clone https://github.com/GIU-F1Tenth/racebrain-modules.git
   cd racebrain-modules
   ```

2. Choose the module you want to work with:
   - For lap timing: `cd lap_timer/`
   - For common utilities: `cd common/`

3. Follow the specific README instructions in each module directory

## 📦 Modules

### 🏁 Lap Timer Module
A complete lap timing system designed to measure and display lap times for F1Tenth cars.

**Features:**
- Microcontroller-based timing system
- Real-time lap time display
- Configurable timing gates/sensors
- Data logging capabilities

**Status:** 🚧 In Development

### 📊 Display Module
Future module for displaying telemetry data on OLED/LCD screens.

**Planned Features:**
- Speed, acceleration, and sensor data display
- Real-time race statistics
- Configurable display layouts

**Status:** 📋 Planned

### 🔧 Common Utilities
Shared code libraries for serial communication and hardware interfacing.

**Includes:**
- UART communication helpers
- SPI/I2C utility functions
- Common sensor interfaces

**Status:** 🚧 In Development

## 🛠️ Development Guidelines

### Code Style
- Follow Arduino/C++ coding standards
- Use meaningful variable and function names
- Include comprehensive comments
- Document all public APIs

### Hardware Design
- Use standard F1Tenth car dimensions and mounting points
- Design for easy installation and maintenance
- Include proper ESD protection and power management
- Document all electrical specifications

### Documentation
- Each module must have its own README
- Include wiring diagrams and assembly instructions
- Provide example code and usage scenarios
- Document all configuration options

## 🤝 Contributing

We welcome contributions from the F1Tenth community! Please see our [Contributing Guidelines](docs/CONTRIBUTING.md) for details on how to get involved.

### How to Contribute
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📋 Roadmap

- [x] Repository structure setup
- [ ] Complete lap timer firmware
- [ ] Lap timer PCB design
- [ ] Common serial utilities library
- [ ] Display module development
- [ ] Integration testing with F1Tenth cars
- [ ] Community testing and feedback

## 🐛 Issues and Support

If you encounter any issues or have questions:
1. Check the [Issues](https://github.com/GIU-F1Tenth/racebrain-modules/issues) page
2. Search existing issues before creating new ones
3. Provide detailed information including hardware specifications
4. Include relevant code snippets and error messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎯 Related Projects

- [F1Tenth Official Repository](https://github.com/f1tenth)
- [F1Tenth Documentation](https://f1tenth.org/)
- [GIU F1Tenth Team](https://github.com/GIU-F1Tenth)

## 👥 Maintainers

- @Mohammed-Azab(m.3zab@outlook.com)

---
