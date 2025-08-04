# 🚀 Quick Usage Guide for Universal Controller Visualizer

## ✅ What You Just Created

The **Universal Controller Visualizer** has been successfully created and is ready to use! Here's how to launch it from anywhere.

## 📍 Current Status

✅ **Package built successfully**  
✅ **Configuration files created**  
✅ **Launch scripts ready**  
✅ **Migration from old visualizers complete**  

## 🎯 Quick Launch Options

### Option 1: Direct Python Execution (Recommended)
```bash
# Navigate to the visualizer directory
cd ~/ws/src/race_stack/pitlane-utils/controller_visualizer

# Launch for different controllers
python3 launch_visualizer.py lqr
python3 launch_visualizer.py lqg  
python3 launch_visualizer.py mpc
```

### Option 2: ROS2 Launch (After Building)
```bash
# Build the package first
cd ~/ws
colcon build --packages-select controller_visualizer
source install/setup.bash

# Launch with ROS2
ros2 launch controller_visualizer lqr_visualizer.launch.py
ros2 launch controller_visualizer lqg_visualizer.launch.py
ros2 launch controller_visualizer mpc_visualizer.launch.py
```

### Option 3: Direct Script Execution
```bash
cd ~/ws/src/race_stack/pitlane-utils/controller_visualizer
python3 src/universal_controller_visualizer.py --controller lqr --config config/lqr_config.yaml
```

## 🛠️ If You Get "No such file or directory" Error

This usually means you're running from the wrong directory. Here's the solution:

```bash
# Always navigate to the visualizer directory first
cd ~/ws/src/race_stack/pitlane-utils/controller_visualizer

# Then run the script
python3 launch_visualizer.py lqr
```

## 📋 Available Commands

### Show Help
```bash
cd ~/ws/src/race_stack/pitlane-utils/controller_visualizer
python3 launch_visualizer.py
# Shows usage examples and available controllers
```

### List Available Configs
```bash
cd ~/ws/src/race_stack/pitlane-utils/controller_visualizer
python3 launch_visualizer.py lqr --list-configs
# Shows all configuration files
```

### Use Custom Config
```bash
cd ~/ws/src/race_stack/pitlane-utils/controller_visualizer
python3 launch_visualizer.py lqr --config my_custom_config.yaml
```

## 🎮 Controller Types Available

- **lqr** - Linear Quadratic Regulator  
- **lqg** - Linear Quadratic Gaussian
- **mpc** - Model Predictive Control
- **pid** - PID Controller
- **pure_pursuit** - Pure Pursuit
- **stanley** - Stanley Controller  
- **custom** - Custom Controller

## 🔧 Configuration Files

Located in `config/` directory:
- `lqr_config.yaml` - LQR-specific settings
- `lqg_config.yaml` - LQG-specific settings  
- `mpc_config.yaml` - MPC-specific settings
- `visualizer_config.yaml` - Universal settings

## 🎨 What the Visualizer Shows

### 4 Main Tabs:
1. **Trajectory** - Vehicle path, reference trajectory, orientation
2. **Control History** - Acceleration/steering commands vs actual
3. **Performance** - State error, velocity tracking, metrics  
4. **Diagnostics** - System status, topics, statistics

### Features:
- Real-time plotting at 10+ Hz
- Data export (JSON, CSV)
- Controller status monitoring
- Emergency stop detection
- Performance metrics

## 🚨 Troubleshooting

### "No such file or directory"
```bash
# Solution: Always cd to the visualizer directory first
cd ~/ws/src/race_stack/pitlane-utils/controller_visualizer
python3 launch_visualizer.py lqr
```

### "Import Error" 
```bash
# Install missing dependencies
pip3 install matplotlib numpy pyyaml
sudo apt install python3-tk
```

### "No data received"
```bash
# Make sure your controller is running and publishing to topics
ros2 topic list | grep drive
ros2 topic echo /drive
```

## 📚 Full Example Workflow

```bash
# 1. Navigate to visualizer
cd ~/ws/src/race_stack/pitlane-utils/controller_visualizer

# 2. Check available configs
python3 launch_visualizer.py lqr --list-configs

# 3. Launch visualizer for LQR controller
python3 launch_visualizer.py lqr

# 4. In another terminal, start your controller
ros2 launch lqr_controller lqr_controller.launch.py

# 5. The visualizer will show real-time data!
```

## 🎉 Success! 

The visualizer is ready to use. The enhanced script now provides:

✅ **Clear usage examples when run without arguments**  
✅ **Better error messages with helpful suggestions**  
✅ **Automatic dependency checking**  
✅ **Configuration file listing**  
✅ **Improved path handling**  

Just remember to **cd to the visualizer directory first**, then run the script!
