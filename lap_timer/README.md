# Lap Timer Module

A comprehensive lap timing system designed specifically for F1Tenth autonomous racing cars. This module provides accurate lap time measurement and real-time display capabilities using microcontroller-based hardware.

## 🎯 Overview

The Lap Timer Module is designed to measure and display lap times for F1Tenth cars during practice sessions, competitions, and development testing. It uses infrared sensors or magnetic sensors to detect when a car crosses the start/finish line and provides immediate feedback on lap performance.

## ✨ Features

- **Accurate Timing**: Microsecond precision lap time measurement
- **Real-time Display**: Immediate lap time feedback on LCD/OLED screen
- **Data Logging**: Store lap times for later analysis
- **Multiple Detection Methods**: Support for IR sensors, magnetic sensors, or beam-break detection
- **Configurable**: Adjustable sensor sensitivity and display options
- **Compact Design**: Fits standard F1Tenth track infrastructure
- **Battery Powered**: Portable operation with rechargeable battery

## 📁 Directory Structure

```
lap_timer/
├── README.md               # This file
├── firmware/               # Microcontroller code
│   ├── src/               # Source code files
│   ├── lib/               # Libraries and dependencies
│   ├── platformio.ini     # PlatformIO configuration
│   └── examples/          # Example sketches
├── pcb_design/            # Hardware design files
│   ├── schematic/         # Circuit schematics
│   ├── pcb/              # PCB layout files
│   ├── gerbers/          # Manufacturing files
│   └── bom/              # Bill of Materials
└── docs/                  # Documentation
    ├── assembly.md        # Assembly instructions
    ├── wiring.md         # Wiring diagrams
    ├── calibration.md    # Sensor calibration guide
    └── images/           # Photos and diagrams
```

## 🛠️ Hardware Requirements

### Microcontroller
- **Primary**: ESP32 DevKit (recommended for WiFi connectivity)
- **Alternative**: Arduino Nano/Uno for basic functionality

### Sensors
- **Option 1**: IR Break-beam sensor pair (Transmitter + Receiver)
- **Option 2**: Magnetic hall effect sensor with magnets
- **Option 3**: Ultrasonic distance sensor

### Display
- **Primary**: 128x64 OLED Display (SSD1306)
- **Alternative**: 16x2 LCD Display

### Additional Components
- Pushbutton switches (2x) for control
- Buzzer for audio feedback
- LED indicators (3x) - Red, Yellow, Green
- Power management circuit
- Enclosure (3D printed or off-the-shelf)

## 🔧 Installation & Setup

### 1. Hardware Assembly
1. Follow the [assembly instructions](docs/assembly.md)
2. Wire components according to [wiring diagram](docs/wiring.md)
3. Mount the sensor at the start/finish line location

### 2. Firmware Upload
```bash
# Using PlatformIO
cd firmware/
pio run --target upload

# Using Arduino IDE
# Open firmware/src/main.cpp in Arduino IDE
# Select appropriate board and port
# Click Upload
```

### 3. Calibration
1. Power on the device
2. Follow the [calibration guide](docs/calibration.md)
3. Test with a car to ensure proper detection

## 🚀 Usage

### Basic Operation
1. **Power On**: Press and hold the power button
2. **Ready Mode**: Green LED indicates system is ready
3. **Detection**: Yellow LED flashes when car is detected
4. **Lap Complete**: Display shows lap time, buzzer sounds
5. **Reset**: Press reset button to clear times

### Display Information
- **Line 1**: Current lap time
- **Line 2**: Best lap time
- **Line 3**: Last lap time
- **Line 4**: Total laps completed

### Button Controls
- **Button 1**: Reset/Clear times
- **Button 2**: Mode select (Practice/Race/Setup)

## ⚙️ Configuration

### Sensor Settings
```cpp
// In firmware/src/config.h
#define SENSOR_TYPE IR_BEAM        // IR_BEAM, MAGNETIC, ULTRASONIC
#define SENSOR_PIN 2               // Digital pin for sensor
#define DETECTION_THRESHOLD 100    // Sensor sensitivity
#define DEBOUNCE_TIME 50          // Milliseconds
```

### Display Options
```cpp
#define DISPLAY_TYPE OLED_128x64   // OLED_128x64, LCD_16x2
#define REFRESH_RATE 100          // Milliseconds
#define BACKLIGHT_TIMEOUT 30000   // Auto-off timer
```

## 📊 Data Logging

The system can log lap times to:
- **SD Card**: For detailed analysis (optional SD card module)
- **Serial Monitor**: Real-time debugging
- **WiFi**: Send data to remote server (ESP32 only)

### Log Format
```
Timestamp,Lap_Number,Lap_Time_ms,Best_Time_ms
2025-07-26 14:30:15,1,23456,23456
2025-07-26 14:30:42,2,22890,22890
```

## 🔬 Technical Specifications

### Timing Accuracy
- **Resolution**: 1 millisecond
- **Accuracy**: ±5ms (depending on sensor type)
- **Range**: 0.001s to 999.999s

### Power Consumption
- **Active Mode**: 150mA @ 5V
- **Sleep Mode**: 10mA @ 5V
- **Battery Life**: 8-12 hours (2000mAh Li-Po)

### Operating Conditions
- **Temperature**: -10°C to +50°C
- **Humidity**: 10% to 90% non-condensing
- **Vibration**: Standard automotive specifications

## 🧪 Testing & Validation

### Self-Test Procedures
1. **Sensor Test**: Verify detection range and sensitivity
2. **Display Test**: Check all display segments
3. **Timing Test**: Compare with reference timer
4. **Battery Test**: Verify voltage monitoring

### Calibration Verification
- Use a known-speed reference (metronome, stopwatch)
- Test with different car speeds
- Verify consistent detection across track width

## 🤝 Contributing

Contributions to the Lap Timer Module are welcome! Areas for improvement:

- Additional sensor type support
- Enhanced data analysis features
- Mobile app connectivity
- Advanced race management features

## 🐛 Troubleshooting

### Common Issues

**Inconsistent Detection**
- Check sensor alignment and height
- Verify detection threshold settings
- Clean sensor lenses/surfaces

**Display Not Working**
- Check I2C connections
- Verify display address (0x3C or 0x3D)
- Test with simple display example

**Timing Drift**
- Calibrate internal clock
- Check power supply stability
- Verify sensor mounting rigidity

## 📄 License

This module is part of the F1Tenth Utilities project and is licensed under the MIT License.

## 🔗 References

- [F1Tenth Official Documentation](https://f1tenth.org/)
- [ESP32 Documentation](https://docs.espressif.com/projects/esp-idf/)
- [Arduino Libraries](https://www.arduino.cc/reference/en/libraries/)

---

**Ready to time some laps! ⏱️🏁**
