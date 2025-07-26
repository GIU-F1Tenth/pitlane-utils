# Display Module

*📋 Planned Module - Coming Soon*

A flexible display system for showing real-time telemetry data, race statistics, and system status on OLED or LCD screens for F1Tenth racing applications.

## 🎯 Planned Features

### Display Capabilities
- **Multiple Screen Support**: OLED (128x64, 128x32) and LCD (16x2, 20x4)
- **Real-time Data**: Speed, acceleration, sensor readings
- **Race Statistics**: Lap times, best lap, sector times
- **System Status**: Battery level, connection status, error messages
- **Customizable Layouts**: User-configurable display screens

### Data Sources
- **Serial Input**: Receive data from main F1Tenth computer
- **Direct Sensors**: Connect sensors directly to display module
- **Wireless**: WiFi/Bluetooth data reception
- **SD Card**: Historical data playback

### User Interface
- **Button Navigation**: Cycle through different display modes
- **Auto-switching**: Intelligent screen changes based on race state
- **Brightness Control**: Automatic and manual brightness adjustment
- **Sleep Mode**: Power saving when inactive

## 🛠️ Planned Hardware

### Microcontroller Options
- **ESP32**: For WiFi connectivity and advanced features
- **Arduino Nano**: For basic display functionality
- **Raspberry Pi Pico**: For advanced processing needs

### Display Options
- **Primary**: 128x64 OLED (SSD1306/SSD1309)
- **Secondary**: 16x2 LCD with I2C backpack
- **Advanced**: Color TFT displays for enhanced visuals

### Interface Components
- Rotary encoder for navigation
- Push buttons for mode selection
- Status LEDs
- Buzzer for alerts

## 📋 Development Roadmap

### Phase 1: Basic Display (Planned)
- [ ] Basic OLED display functionality
- [ ] Serial data reception
- [ ] Simple text-based layouts
- [ ] Basic navigation system

### Phase 2: Enhanced Features (Future)
- [ ] Multiple display type support
- [ ] Wireless data reception
- [ ] Graphical display elements
- [ ] Data logging capabilities

### Phase 3: Advanced Integration (Future)
- [ ] Integration with ROS systems
- [ ] Real-time plotting capabilities
- [ ] Mobile app connectivity
- [ ] Cloud data synchronization

## 🔌 Planned Integration

### F1Tenth Car Integration
- Mount display module on car dashboard
- Connect to existing car computer via serial/USB
- Power from car's electrical system
- Display real-time driving data

### Pit Station Setup
- Larger displays for pit crew monitoring
- Multiple car tracking capabilities
- Race management features
- Historical data analysis

### Track Infrastructure
- Timing tower displays
- Spectator information screens
- Race progress indicators
- Leaderboard displays

## 📊 Display Layouts (Planned)

### Race Mode
```
Speed: 15.2 km/h     Batt: 87%
Lap: 3/10      Time: 01:23.45
Best: 01:20.12    Last: 01:24.67
Pos: 2nd           Gap: +0.34s
```

### Debug Mode
```
CPU: 45%    RAM: 234MB/512MB
Temp: 42°C    Throttle: 67%
Steering: +15°    Brake: 23%
IMU: OK  LIDAR: OK  CAM: OK
```

### Setup Mode
```
> Display Settings
  Data Sources
  Calibration
  System Info
```

## 🤝 Contributing

This module is in the planning phase. Contributions welcome for:

- Feature suggestions and requirements
- Hardware recommendations
- UI/UX design ideas
- Integration scenarios

## 📞 Contact

For questions about the Display Module development:
- Create an issue with the `display-module` label
- Join the discussion in the planning documents
- Contribute to the design specifications

---

**Stay tuned for updates! 📺✨**

*This module is part of the F1Tenth Utilities Collection*
