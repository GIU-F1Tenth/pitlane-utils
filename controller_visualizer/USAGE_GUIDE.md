# Universal Controller Visualizer - Quick Start Guide

## 🎉 Migration Complete!

The visualization code has been successfully moved from `adaptive_lqr_lqg` to the new **Universal Controller Visualizer** in `pitlane-utils/controller_visualizer/`.

## 🚀 Quick Usage

### 1. Build the Package
```bash
cd ~/ws
colcon build --packages-select controller_visualizer
source install/setup.bash
```

### 2. Launch Visualizers

#### For LQR Controller
```bash
ros2 launch controller_visualizer lqr_visualizer.launch.py
```

#### For LQG Controller  
```bash
ros2 launch controller_visualizer lqg_visualizer.launch.py
```

#### For MPC Controller
```bash
ros2 launch controller_visualizer mpc_visualizer.launch.py
```

#### Universal (Any Controller)
```bash
ros2 launch controller_visualizer universal_visualizer.launch.py controller_type:=lqr
ros2 launch controller_visualizer universal_visualizer.launch.py controller_type:=lqg
ros2 launch controller_visualizer universal_visualizer.launch.py controller_type:=mpc
```

### 3. Direct Execution
```bash
# Quick launch script
cd ~/ws/src/race_stack/pitlane-utils/controller_visualizer
./launch_visualizer.py lqr

# Or direct execution
python3 src/universal_controller_visualizer.py --controller lqr --config config/lqr_config.yaml
```

## ✨ New Features

### Enhanced Capabilities
- **Multi-controller support**: LQR, LQG, MPC, PID, Pure Pursuit, Stanley
- **Real-time performance**: Optimized plotting with 10+ Hz update rates
- **Data export**: JSON and CSV export for analysis
- **Configurable interface**: YAML configuration files
- **Better diagnostics**: Enhanced monitoring and error detection

### GUI Improvements
- **Trajectory Tab**: Vehicle path, reference trajectory, orientation arrows
- **Control Tab**: Acceleration/steering history, command vs actual
- **Performance Tab**: State error, velocity tracking, metrics
- **Diagnostics Tab**: System status, topic info, statistics

### Configuration Flexibility
- **Topic mapping**: Customize ROS2 topics for any controller
- **Controller-specific**: Optimized configs for LQR, LQG, MPC
- **Visual settings**: Colors, plot styles, update rates
- **Export options**: Data formats, timestamps, metadata

## 📁 File Structure

```
pitlane-utils/controller_visualizer/
├── src/
│   └── universal_controller_visualizer.py    # Main visualizer
├── config/
│   ├── visualizer_config.yaml               # Universal config
│   ├── lqr_config.yaml                      # LQR-specific
│   ├── lqg_config.yaml                      # LQG-specific
│   └── mpc_config.yaml                      # MPC-specific
├── launch/
│   ├── universal_visualizer.launch.py       # Universal launcher
│   ├── lqr_visualizer.launch.py            # LQR launcher
│   ├── lqg_visualizer.launch.py            # LQG launcher
│   └── mpc_visualizer.launch.py            # MPC launcher
├── launch_visualizer.py                     # Quick launch script
├── migrate_visualization.py                 # Migration utility
└── README.md                               # Full documentation
```

## 🔧 Configuration Examples

### Custom Topic Mapping
```yaml
# config/custom_config.yaml
controller_type: "my_controller"
topics:
  control_output: "/my_robot/drive"
  odometry: "/my_robot/odom"
  diagnostics: "/my_controller/diagnostics"
  state_error: "/my_controller/error"
```

### Visual Customization
```yaml
plots:
  trajectory:
    vehicle_color: "red"
    reference_color: "blue"
    vehicle_size: 10
  control:
    show_constraints: true
    show_saturation_limits: true
```

## 🔄 Migration from Old Visualizers

### What Changed
- ❌ **Removed**: `adaptive_lqr_lqg/scripts/lqr_visualizer.py`
- ❌ **Removed**: `adaptive_lqr_lqg/scripts/lqg_visualizer.py`
- ❌ **Removed**: Parameter GUIs and standalone visualizers
- ✅ **Added**: Universal visualizer supporting all controllers
- ✅ **Added**: Enhanced configuration and features

### Old vs New Commands
```bash
# OLD (removed)
python3 adaptive_lqr_lqg/scripts/lqr_visualizer.py

# NEW (universal)
ros2 launch controller_visualizer lqr_visualizer.launch.py
```

### Backup Location
Old files are backed up in:
- `adaptive_lqr_lqg/backup_visualization/`

## 📊 Usage Examples

### Full System Launch
```bash
# Terminal 1: Start F1TENTH stack
ros2 launch stack_master bringup.launch.py

# Terminal 2: Start LQR controller  
ros2 launch lqr_controller lqr_controller.launch.py

# Terminal 3: Start visualizer
ros2 launch controller_visualizer lqr_visualizer.launch.py
```

### Comparison Testing
```bash
# Launch multiple visualizers for comparison
ros2 launch controller_visualizer lqr_visualizer.launch.py node_name:=lqr_viz &
ros2 launch controller_visualizer mpc_visualizer.launch.py node_name:=mpc_viz &
```

### Data Collection
```bash
# Start visualizer, run experiments, then export data from GUI
# Data includes vehicle states, control commands, performance metrics
```

## 🐛 Troubleshooting

### "No data received"
- Check controller is running: `ros2 topic list | grep drive`
- Verify topic names in config match actual topics
- Check ROS2 node connections: `ros2 node info controller_visualizer`

### "Import errors"
- Install dependencies: `pip3 install matplotlib pyyaml numpy`
- For GUI: `sudo apt install python3-tk`
- Optional interfaces: Build `giu_f1t_interfaces` package

### "Performance issues"
- Reduce `update_rate_hz` in config
- Decrease `max_history` for less memory usage
- Close unused tabs in visualizer

## 🎯 Next Steps

1. **Test the visualizer** with your controllers
2. **Customize configs** for your specific setup  
3. **Export data** for performance analysis
4. **Report issues** if any problems arise
5. **Enjoy improved visualization**! 🏁

---

The universal visualizer provides a much better experience with enhanced features, better performance, and support for all F1TENTH controllers!
