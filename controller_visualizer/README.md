# Universal F1TENTH Controller Visualizer

A comprehensive, real-time visualization tool for monitoring any F1TENTH autonomous racing controller performance. This universal visualizer supports multiple controller types with a unified interface.

## 🎯 Features

### Multi-Controller Support
- **LQR** (Linear Quadratic Regulator)
- **LQG** (Linear Quadratic Gaussian)
- **MPC** (Model Predictive Control)
- **PID** (Proportional-Integral-Derivative)
- **Pure Pursuit**
- **Stanley Controller**
- **Custom Controllers**

### Real-Time Visualization
- Vehicle trajectory and reference path plotting
- Control input history (acceleration, steering)
- Performance metrics and diagnostics
- State error tracking
- Emergency stop monitoring

### Advanced Features
- Configurable topic mapping for different controllers
- Data export (JSON, CSV formats)
- Real-time performance monitoring
- Multiple visualization tabs
- Controller-specific optimizations

## 🚀 Quick Start

### Installation

1. **Prerequisites**:
   ```bash
   # ROS2 packages
   sudo apt install ros-humble-ackermann-msgs ros-humble-nav-msgs
   
   # Python dependencies
   pip3 install matplotlib tkinter numpy pyyaml
   ```

2. **Build the package**:
   ```bash
   cd ~/ws
   colcon build --packages-select controller_visualizer
   source install/setup.bash
   ```

### Basic Usage

1. **Launch with default LQR configuration**:
   ```bash
   ros2 launch controller_visualizer universal_visualizer.launch.py
   ```

2. **Launch for specific controller**:
   ```bash
   # For LQR
   ros2 launch controller_visualizer lqr_visualizer.launch.py
   
   # For MPC
   ros2 launch controller_visualizer mpc_visualizer.launch.py
   
   # For custom controller
   ros2 launch controller_visualizer universal_visualizer.launch.py controller_type:=mpc
   ```

3. **Direct execution with custom config**:
   ```bash
   python3 src/universal_controller_visualizer.py --controller lqr --config config/lqr_config.yaml
   ```

## 📊 GUI Interface

The visualizer provides multiple tabs for comprehensive monitoring:

### 1. **Trajectory Tab**
- Real-time vehicle position and orientation
- Reference trajectory overlay
- Path tracking visualization
- Vehicle orientation arrows

### 2. **Control History Tab**
- Acceleration command vs actual
- Steering angle commands
- Control input history plots
- Saturation indicator

### 3. **Performance Tab**
- State tracking error
- Velocity profile
- Controller performance metrics
- Real-time frequency monitoring

### 4. **Diagnostics Tab**
- Detailed controller status
- Topic information
- Data history statistics
- Configuration display

## ⚙️ Configuration

### Basic Configuration (`visualizer_config.yaml`)

```yaml
controller_type: "lqr"
max_history: 1000
update_rate_hz: 10

topics:
  control_output: "/drive"
  odometry: "/odom"
  trajectory: "/reference_trajectory"
  diagnostics: "/diagnostics"
  state_error: "/state_error"
  path_ready: "/path_ready"

visualization:
  show_trajectory: true
  show_control_history: true
  show_performance: true
  show_diagnostics: true
```

### Controller-Specific Configurations

#### LQR Controller (`lqr_config.yaml`)
```yaml
controller_type: "lqr"
topics:
  diagnostics: "/lqr/diagnostics"
  state_error: "/lqr/state_error"

lqr_features:
  show_gain_matrix: true
  show_state_weights: true
  real_time_tuning: false
```

#### MPC Controller (`mpc_config.yaml`)
```yaml
controller_type: "mpc"
topics:
  predicted_trajectory: "/mpc/predicted_trajectory"
  optimization_time: "/mpc/optimization_time"

mpc_features:
  show_prediction_horizon: true
  show_constraints: true
  prediction_horizon_length: 20
```

## 🔧 Topic Mapping

The visualizer automatically adapts to different topic configurations:

### Required Topics
- **Control Output**: `AckermannDriveStamped` on `/drive`
- **Odometry**: `Odometry` on `/odom`

### Optional Topics
- **Reference Trajectory**: `VehicleStateArray` on `/reference_trajectory`
- **Diagnostics**: `DiagnosticArray` on `/diagnostics`
- **State Error**: `Float32` on `/state_error`
- **Path Ready**: `Bool` on `/path_ready`
- **Emergency Stop**: `Bool` on `/emergency_stop`

### Custom Topic Mapping
```yaml
topics:
  control_output: "/my_controller/drive"
  odometry: "/my_robot/odom"
  diagnostics: "/my_controller/diagnostics"
  # ... other topics
```

## 📈 Data Export

### Export Formats
1. **JSON**: Complete data with metadata
2. **CSV**: Simplified tabular format

### Export Data
- Vehicle state history
- Control command history
- Performance metrics
- Configuration settings
- Reference trajectory

### Usage
```python
# In GUI: Control Panel → Export Data
# Select format and location
# Data includes timestamps and all collected metrics
```

## 🎮 Integration Examples

### With LQR Controller
```bash
# Terminal 1: Start your LQR controller
ros2 run lqr_controller lqr_node

# Terminal 2: Start visualizer
ros2 launch controller_visualizer lqr_visualizer.launch.py
```

### With MPC Controller
```bash
# Terminal 1: Start your MPC controller
ros2 run mpc_controller mpc_node

# Terminal 2: Start visualizer with MPC config
ros2 launch controller_visualizer mpc_visualizer.launch.py
```

### With Custom Controller
```bash
# Create custom config file
cp config/visualizer_config.yaml config/my_controller_config.yaml
# Edit topic mappings

# Launch with custom config
ros2 launch controller_visualizer universal_visualizer.launch.py \
  controller_type:=custom \
  config_file:=$(pwd)/config/my_controller_config.yaml
```

## 🛠️ Advanced Usage

### Real-Time Performance Monitoring
- Control loop frequency tracking
- Computation time analysis
- Failure detection and counting
- Emergency stop monitoring

### Multi-Controller Comparison
```bash
# Launch multiple visualizers
ros2 launch controller_visualizer lqr_visualizer.launch.py node_name:=lqr_vis &
ros2 launch controller_visualizer mpc_visualizer.launch.py node_name:=mpc_vis &
```

### Data Analysis Workflow
1. **Collect Data**: Run visualizer during autonomous driving
2. **Export Data**: Save to JSON/CSV format
3. **Analyze**: Use exported data for performance analysis
4. **Optimize**: Adjust controller parameters based on insights

## 🐛 Troubleshooting

### Common Issues

1. **"No data received"**
   - Check topic names in configuration
   - Verify controller is publishing
   - Use `ros2 topic list` to check available topics

2. **"Import error: giu_f1t_interfaces"**
   - This is optional - visualizer works without custom interfaces
   - Install custom message packages if available

3. **"GUI not showing"**
   - Ensure tkinter is installed: `sudo apt install python3-tk`
   - Check X11 forwarding if using SSH

4. **"Low frame rate"**
   - Reduce `update_rate_hz` in configuration
   - Decrease `max_history` for better performance

### Debug Mode
```bash
# Run with verbose output
python3 src/universal_controller_visualizer.py --controller lqr --config config/lqr_config.yaml -v
```

## 📋 Requirements

### System Requirements
- **OS**: Ubuntu 20.04/22.04 (ROS2 Humble/Foxy)
- **Python**: 3.8+
- **ROS2**: Humble or Foxy
- **Memory**: 512MB+ for GUI
- **Display**: Required for GUI

### Python Dependencies
```txt
rclpy
numpy
matplotlib
tkinter
pyyaml
tf-transformations
```

### ROS2 Dependencies
```txt
ackermann_msgs
nav_msgs
geometry_msgs
sensor_msgs
std_msgs
diagnostic_msgs
```

## 🤝 Contributing

### Adding New Controller Support

1. **Create controller-specific config**:
   ```yaml
   # config/my_controller_config.yaml
   controller_type: "my_controller"
   topics:
     diagnostics: "/my_controller/diagnostics"
     # ... other topics
   ```

2. **Add controller enum** (if needed):
   ```python
   class ControllerType(Enum):
       MY_CONTROLLER = "my_controller"
   ```

3. **Update topic mappings** for specific message types

### Feature Requests
- Open GitHub issue with feature description
- Include example use case
- Provide sample data if available

## 📄 License

MIT License - see LICENSE file for details.

## 👨‍💻 Author

**Mohammed Azab** - [mohammed@azab.io](mailto:mohammed@azab.io)

## 🙏 Acknowledgments

- F1TENTH community for autonomous racing platform
- ROS2 ecosystem for robotics framework
- matplotlib/tkinter for visualization capabilities

## 📚 Related Packages

- `lqr_controller` - LQR controller implementation
- `mpc_controller` - MPC controller implementation
- `stack_master` - F1TENTH stack management
- `perception` - Sensor processing for autonomous racing

---

**Happy Racing! 🏁**
