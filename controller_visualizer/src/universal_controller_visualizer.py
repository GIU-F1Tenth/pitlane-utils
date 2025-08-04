#!/usr/bin/env python3

"""
Universal F1TENTH Controller Visualizer

A comprehensive real-time visualization tool for monitoring any F1TENTH controller performance.
This tool supports LQR, LQG, MPC, and other controllers with a unified interface.

Features:
- Multi-controller support (LQR, LQG, MPC, etc.)
- Real-time trajectory and control visualization
- Performance metrics and diagnostics
- Configurable topic mapping
- Export and data analysis capabilities

Author: Mohammed Azab <mohammed@azab.io>
License: MIT
Version: 2.0.0 (Universal)
"""

import sys
import os
import rclpy
import numpy as np
import threading
import time
import json
import yaml
from typing import Dict, List, Optional, Tuple, Any
from collections import deque
from dataclasses import dataclass, asdict
from enum import Enum

# GUI imports
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation

# ROS2 imports
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry
from ackermann_msgs.msg import AckermannDriveStamped
from std_msgs.msg import Bool, Float32, String
from diagnostic_msgs.msg import DiagnosticArray
from sensor_msgs.msg import LaserScan
try:
    from giu_f1t_interfaces.msg import VehicleStateArray
except ImportError:
    # Handle case where custom interfaces are not available
    VehicleStateArray = None
from tf_transformations import euler_from_quaternion


class ControllerType(Enum):
    """Supported controller types."""
    LQR = "lqr"
    LQG = "lqg"
    MPC = "mpc"
    PID = "pid"
    PURE_PURSUIT = "pure_pursuit"
    STANLEY = "stanley"
    CUSTOM = "custom"


@dataclass
class VehicleState:
    """Universal vehicle state data class."""
    x: float = 0.0
    y: float = 0.0
    velocity: float = 0.0
    yaw: float = 0.0
    steering_angle: float = 0.0
    acceleration: float = 0.0
    timestamp: float = 0.0


@dataclass
class ControlCommand:
    """Universal control command data class."""
    acceleration: float = 0.0
    steering_angle: float = 0.0
    speed: float = 0.0
    timestamp: float = 0.0


@dataclass
class PerformanceMetrics:
    """Universal performance metrics data class."""
    control_frequency: float = 0.0
    avg_control_time: float = 0.0
    max_control_time: float = 0.0
    consecutive_failures: int = 0
    path_ready: bool = False
    controller_active: bool = False
    emergency_stop: bool = False
    state_error: float = 0.0
    controller_type: str = "unknown"


@dataclass
class TopicMapping:
    """Topic configuration for different controllers."""
    # Core topics (required for all controllers)
    control_output: str = "/drive"
    odometry: str = "/odom"
    trajectory: str = "horizon_mapper/reference_trajectory"
    diagnostics: str = "/diagnostics"
    state_error: str = "/state_error"
    path_ready: str = "horizon_mapper/path_ready"
    emergency_stop: str = "/emergency_stop"
    controller_status: str = "/controller_status"

    # LQG-specific topics
    estimation_error: str = "/lqg/estimation_error"
    kalman_covariance: str = "/lqg/covariance"

    # MPC-specific topics
    predicted_trajectory: str = "/mpc/predicted_trajectory"
    optimization_time: str = "/mpc/optimization_time"
    solver_status: str = "/mpc/solver_status"

    # Additional optional topics for various controllers
    tracking_error: str = "/tracking_error"
    control_effort: str = "/control_effort"
    reference_velocity: str = "/reference_velocity"
    actual_velocity: str = "/actual_velocity"

    def __post_init__(self):
        """Filter out any additional unknown topics that might be passed."""
        # This allows for forward compatibility with new topic types
        pass


class UniversalVisualizerNode(Node):
    """ROS2 node for collecting data from any F1TENTH controller."""

    def __init__(self, controller_type: ControllerType, topic_mapping: TopicMapping, data_callback):
        super().__init__('universal_controller_visualizer')

        self.controller_type = controller_type
        self.topic_mapping = topic_mapping
        self.data_callback = data_callback

        # QoS profile for subscriptions
        self.qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE,
            depth=10
        )

        self.sensor_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            depth=5
        )

        # Data storage
        self.vehicle_state = VehicleState()
        self.control_command = ControlCommand()
        self.performance_metrics = PerformanceMetrics(controller_type=controller_type.value)
        self.reference_trajectory = []

        # For acceleration calculation
        self.prev_velocity = None
        self.prev_time = None

        # Setup subscriptions based on topic mapping
        self._setup_subscriptions()

        self.get_logger().info(f"Universal Visualizer Node initialized for {controller_type.value.upper()} controller")

    def _setup_subscriptions(self):
        """Setup ROS2 subscriptions based on topic mapping."""

        # Core subscriptions (always needed)
        self.odom_sub = self.create_subscription(
            Odometry, self.topic_mapping.odometry, self.odom_callback, self.sensor_qos)

        self.control_sub = self.create_subscription(
            AckermannDriveStamped, self.topic_mapping.control_output,
            self.control_callback, self.qos_profile)

        # Optional subscriptions (handle gracefully if topics don't exist)
        try:
            if VehicleStateArray:
                self.trajectory_sub = self.create_subscription(
                    VehicleStateArray, self.topic_mapping.trajectory,
                    self.trajectory_callback, self.qos_profile)
        except Exception as e:
            self.get_logger().warn(f"Could not subscribe to trajectory topic: {e}")

        try:
            self.diagnostics_sub = self.create_subscription(
                DiagnosticArray, self.topic_mapping.diagnostics,
                self.diagnostics_callback, self.qos_profile)
        except Exception as e:
            self.get_logger().warn(f"Could not subscribe to diagnostics topic: {e}")

        try:
            self.state_error_sub = self.create_subscription(
                Float32, self.topic_mapping.state_error,
                self.state_error_callback, self.qos_profile)
        except Exception as e:
            self.get_logger().warn(f"Could not subscribe to state error topic: {e}")

        try:
            self.path_ready_sub = self.create_subscription(
                Bool, self.topic_mapping.path_ready,
                self.path_ready_callback, self.qos_profile)
        except Exception as e:
            self.get_logger().warn(f"Could not subscribe to path ready topic: {e}")

    def odom_callback(self, msg: Odometry):
        """Handle odometry messages."""
        try:
            self.vehicle_state.x = msg.pose.pose.position.x
            self.vehicle_state.y = msg.pose.pose.position.y

            linear_vel = msg.twist.twist.linear
            self.vehicle_state.velocity = np.sqrt(linear_vel.x**2 + linear_vel.y**2)

            orientation = msg.pose.pose.orientation
            _, _, self.vehicle_state.yaw = euler_from_quaternion([
                orientation.x, orientation.y, orientation.z, orientation.w])

            # Calculate acceleration
            current_time = time.time()
            if self.prev_velocity is not None and self.prev_time is not None:
                dt = current_time - self.prev_time
                if dt > 0:
                    self.vehicle_state.acceleration = (self.vehicle_state.velocity - self.prev_velocity) / dt

            self.vehicle_state.timestamp = current_time
            self.prev_velocity = self.vehicle_state.velocity
            self.prev_time = current_time

            # Callback to GUI
            if self.data_callback:
                self.data_callback('vehicle_state', self.vehicle_state)

        except Exception as e:
            self.get_logger().error(f"Error in odometry callback: {e}")

    def control_callback(self, msg: AckermannDriveStamped):
        """Handle control command messages."""
        try:
            self.control_command.acceleration = msg.drive.acceleration
            self.control_command.steering_angle = msg.drive.steering_angle
            self.control_command.speed = msg.drive.speed
            self.control_command.timestamp = time.time()

            # Update vehicle state with control info
            self.vehicle_state.steering_angle = msg.drive.steering_angle

            # Callback to GUI
            if self.data_callback:
                self.data_callback('control_command', self.control_command)

        except Exception as e:
            self.get_logger().error(f"Error in control callback: {e}")

    def trajectory_callback(self, msg):
        """Handle reference trajectory messages."""
        try:
            self.reference_trajectory = []
            if hasattr(msg, 'states'):
                for state in msg.states:
                    self.reference_trajectory.append({
                        'x': state.x,
                        'y': state.y,
                        'v': getattr(state, 'v', 0.0),
                        'theta': getattr(state, 'theta', 0.0),
                        'delta': getattr(state, 'delta', 0.0)
                    })

            # Callback to GUI
            if self.data_callback:
                self.data_callback('reference_trajectory', self.reference_trajectory)

        except Exception as e:
            self.get_logger().error(f"Error in trajectory callback: {e}")

    def diagnostics_callback(self, msg: DiagnosticArray):
        """Handle diagnostics messages."""
        try:
            for status in msg.status:
                if any(controller in status.name.lower() for controller in ['lqr', 'lqg', 'mpc', 'controller']):
                    # Parse diagnostics
                    self.performance_metrics.controller_active = (status.level == 0)  # OK
                    self.performance_metrics.emergency_stop = (status.level == 2)  # ERROR

                    for kv in status.values:
                        if kv.key == "control_frequency":
                            self.performance_metrics.control_frequency = float(kv.value)
                        elif kv.key == "avg_control_time":
                            self.performance_metrics.avg_control_time = float(kv.value)
                        elif kv.key == "max_control_time":
                            self.performance_metrics.max_control_time = float(kv.value)
                        elif kv.key == "consecutive_failures":
                            self.performance_metrics.consecutive_failures = int(kv.value)
                        elif kv.key == "path_ready":
                            self.performance_metrics.path_ready = bool(kv.value)

            # Callback to GUI
            if self.data_callback:
                self.data_callback('performance_metrics', self.performance_metrics)

        except Exception as e:
            self.get_logger().error(f"Error in diagnostics callback: {e}")

    def state_error_callback(self, msg: Float32):
        """Handle state error messages."""
        try:
            self.performance_metrics.state_error = msg.data

            # Callback to GUI
            if self.data_callback:
                self.data_callback('state_error', msg.data)

        except Exception as e:
            self.get_logger().error(f"Error in state error callback: {e}")

    def path_ready_callback(self, msg: Bool):
        """Handle path ready messages."""
        try:
            self.performance_metrics.path_ready = msg.data

            # Callback to GUI
            if self.data_callback:
                self.data_callback('path_ready', msg.data)

        except Exception as e:
            self.get_logger().error(f"Error in path ready callback: {e}")


class UniversalControllerVisualizerGUI:
    """Main GUI class for universal controller visualization."""

    def __init__(self, config_file: Optional[str] = None):
        self.root = tk.Tk()
        self.root.title("Universal F1TENTH Controller Visualizer")
        self.root.geometry("1600x1000")
        self.root.configure(bg='#f0f0f0')

        # Load configuration
        self.config = self._load_config(config_file)
        self.controller_type = ControllerType(self.config.get('controller_type', 'lqr'))

        # Create topic mapping, filtering out unknown topics
        topics_config = self.config.get('topics', {})
        self.topic_mapping = self._create_topic_mapping(topics_config)

        # Data storage with history
        self.max_history = self.config.get('max_history', 1000)
        self.vehicle_history = deque(maxlen=self.max_history)
        self.control_history = deque(maxlen=self.max_history)
        self.error_history = deque(maxlen=self.max_history)
        self.reference_trajectory = []

        # Current data
        self.current_vehicle_state = VehicleState()
        self.current_control = ControlCommand()
        self.current_metrics = PerformanceMetrics()

        # Setup GUI
        self.setup_gui()

        # ROS2 node in separate thread
        self.ros_thread = None
        self.ros_node = None
        self.setup_ros_node()

        # Animation timer
        self.animation_running = True
        self.update_plots()

    def _load_config(self, config_file: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        default_config = {
            'controller_type': 'lqr',
            'max_history': 1000,
            'update_rate_hz': 10,
            'topics': {
                'control_output': '/drive',
                'odometry': '/odom',
                'trajectory': '/reference_trajectory',
                'diagnostics': '/diagnostics',
                'state_error': '/state_error',
                'path_ready': '/path_ready'
            },
            'visualization': {
                'show_trajectory': True,
                'show_control_history': True,
                'show_performance': True,
                'show_diagnostics': True
            }
        }

        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    if config_file.endswith('.yaml') or config_file.endswith('.yml'):
                        user_config = yaml.safe_load(f)
                    else:
                        user_config = json.load(f)

                # Merge with defaults
                for key, value in user_config.items():
                    if isinstance(value, dict) and key in default_config:
                        default_config[key].update(value)
                    else:
                        default_config[key] = value

            except Exception as e:
                print(f"Error loading config file {config_file}: {e}")
                print("Using default configuration")

        return default_config

    def _create_topic_mapping(self, topics_config: Dict[str, str]) -> TopicMapping:
        """Create topic mapping, filtering out unknown topics for compatibility."""

        # Get all valid field names from TopicMapping
        from dataclasses import fields
        valid_fields = {field.name for field in fields(TopicMapping)}

        # Filter topics to only include valid ones
        filtered_topics = {
            key: value for key, value in topics_config.items()
            if key in valid_fields
        }

        # Log any filtered out topics for debugging
        filtered_out = set(topics_config.keys()) - valid_fields
        if filtered_out:
            print(f"💡 Note: Ignoring unknown topics from config: {', '.join(filtered_out)}")

        return TopicMapping(**filtered_topics)

    def setup_gui(self):
        """Setup the main GUI layout."""

        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Control panel at top
        self.setup_control_panel(main_frame)

        # Create notebook for different tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Setup different tabs based on configuration
        if self.config['visualization']['show_trajectory']:
            self.setup_trajectory_tab()

        if self.config['visualization']['show_control_history']:
            self.setup_control_tab()

        if self.config['visualization']['show_performance']:
            self.setup_performance_tab()

        if self.config['visualization']['show_diagnostics']:
            self.setup_diagnostics_tab()

    def setup_control_panel(self, parent):
        """Setup the control panel with status indicators."""

        control_frame = ttk.LabelFrame(
            parent,
            text=f"{self.controller_type.value.upper()} Controller Status",
            padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        # Status indicators
        status_frame = ttk.Frame(control_frame)
        status_frame.pack(fill=tk.X)

        # Controller type and status
        ttk.Label(status_frame, text="Controller Type:").grid(row=0, column=0, padx=5, sticky=tk.W)
        self.controller_type_label = ttk.Label(status_frame, text=self.controller_type.value.upper(),
                                               foreground="blue", font=("Arial", 10, "bold"))
        self.controller_type_label.grid(row=0, column=1, padx=5, sticky=tk.W)

        ttk.Label(status_frame, text="Status:").grid(row=0, column=2, padx=5, sticky=tk.W)
        self.controller_status_label = ttk.Label(status_frame, text="Unknown", foreground="gray")
        self.controller_status_label.grid(row=0, column=3, padx=5, sticky=tk.W)

        # Path ready status
        ttk.Label(status_frame, text="Path Ready:").grid(row=0, column=4, padx=5, sticky=tk.W)
        self.path_ready_label = ttk.Label(status_frame, text="Unknown", foreground="gray")
        self.path_ready_label.grid(row=0, column=5, padx=5, sticky=tk.W)

        # Emergency stop status
        ttk.Label(status_frame, text="Emergency Stop:").grid(row=0, column=6, padx=5, sticky=tk.W)
        self.emergency_stop_label = ttk.Label(status_frame, text="Unknown", foreground="gray")
        self.emergency_stop_label.grid(row=0, column=7, padx=5, sticky=tk.W)

        # Current values frame
        values_frame = ttk.Frame(control_frame)
        values_frame.pack(fill=tk.X, pady=(10, 0))

        # Vehicle state values
        ttk.Label(values_frame, text="Position:").grid(row=0, column=0, padx=5, sticky=tk.W)
        self.position_label = ttk.Label(values_frame, text="(0.0, 0.0)")
        self.position_label.grid(row=0, column=1, padx=5, sticky=tk.W)

        ttk.Label(values_frame, text="Velocity:").grid(row=0, column=2, padx=5, sticky=tk.W)
        self.velocity_label = ttk.Label(values_frame, text="0.0 m/s")
        self.velocity_label.grid(row=0, column=3, padx=5, sticky=tk.W)

        ttk.Label(values_frame, text="Steering:").grid(row=0, column=4, padx=5, sticky=tk.W)
        self.steering_label = ttk.Label(values_frame, text="0.0 rad")
        self.steering_label.grid(row=0, column=5, padx=5, sticky=tk.W)

        # Control values
        ttk.Label(values_frame, text="Acceleration:").grid(row=1, column=0, padx=5, sticky=tk.W)
        self.acceleration_label = ttk.Label(values_frame, text="0.0 m/s²")
        self.acceleration_label.grid(row=1, column=1, padx=5, sticky=tk.W)

        ttk.Label(values_frame, text="State Error:").grid(row=1, column=2, padx=5, sticky=tk.W)
        self.state_error_label = ttk.Label(values_frame, text="0.0")
        self.state_error_label.grid(row=1, column=3, padx=5, sticky=tk.W)

        # Control buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(button_frame, text="Export Data", command=self.export_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear History", command=self.clear_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save Config", command=self.save_config).pack(side=tk.LEFT, padx=5)

    def setup_trajectory_tab(self):
        """Setup the trajectory visualization tab."""

        traj_frame = ttk.Frame(self.notebook)
        self.notebook.add(traj_frame, text="Trajectory")

        # Create matplotlib figure
        self.traj_fig = Figure(figsize=(12, 8), dpi=100)
        self.traj_ax = self.traj_fig.add_subplot(111)

        self.traj_canvas = FigureCanvasTkAgg(self.traj_fig, traj_frame)
        self.traj_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Initialize plot
        self.traj_ax.set_title("Vehicle Trajectory and Reference Path")
        self.traj_ax.set_xlabel("X Position [m]")
        self.traj_ax.set_ylabel("Y Position [m]")
        self.traj_ax.grid(True, alpha=0.3)
        self.traj_ax.set_aspect('equal')

    def setup_control_tab(self):
        """Setup the control inputs visualization tab."""

        control_frame = ttk.Frame(self.notebook)
        self.notebook.add(control_frame, text="Control History")

        # Create matplotlib figure with subplots
        self.control_fig = Figure(figsize=(12, 8), dpi=100)

        # Acceleration plot
        self.accel_ax = self.control_fig.add_subplot(2, 1, 1)
        self.accel_ax.set_title("Acceleration Command vs Actual")
        self.accel_ax.set_ylabel("Acceleration [m/s²]")
        self.accel_ax.grid(True, alpha=0.3)

        # Steering plot
        self.steer_ax = self.control_fig.add_subplot(2, 1, 2)
        self.steer_ax.set_title("Steering Angle Command")
        self.steer_ax.set_xlabel("Time [s]")
        self.steer_ax.set_ylabel("Steering Angle [rad]")
        self.steer_ax.grid(True, alpha=0.3)

        self.control_fig.tight_layout()

        self.control_canvas = FigureCanvasTkAgg(self.control_fig, control_frame)
        self.control_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def setup_performance_tab(self):
        """Setup the performance metrics visualization tab."""

        perf_frame = ttk.Frame(self.notebook)
        self.notebook.add(perf_frame, text="Performance")

        # Create matplotlib figure
        self.perf_fig = Figure(figsize=(12, 8), dpi=100)

        # State error plot
        self.error_ax = self.perf_fig.add_subplot(2, 1, 1)
        self.error_ax.set_title("State Error")
        self.error_ax.set_ylabel("Error Magnitude")
        self.error_ax.grid(True, alpha=0.3)

        # Velocity tracking plot
        self.vel_ax = self.perf_fig.add_subplot(2, 1, 2)
        self.vel_ax.set_title("Velocity Profile")
        self.vel_ax.set_xlabel("Time [s]")
        self.vel_ax.set_ylabel("Velocity [m/s]")
        self.vel_ax.grid(True, alpha=0.3)

        self.perf_fig.tight_layout()

        self.perf_canvas = FigureCanvasTkAgg(self.perf_fig, perf_frame)
        self.perf_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def setup_diagnostics_tab(self):
        """Setup the diagnostics information tab."""

        diag_frame = ttk.Frame(self.notebook)
        self.notebook.add(diag_frame, text="Diagnostics")

        # Create text widget for diagnostics
        self.diag_text = tk.Text(diag_frame, wrap=tk.WORD, font=("Courier", 10))

        # Scrollbar for text widget
        scrollbar = ttk.Scrollbar(diag_frame, orient=tk.VERTICAL, command=self.diag_text.yview)
        self.diag_text.configure(yscrollcommand=scrollbar.set)

        # Pack widgets
        self.diag_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def setup_ros_node(self):
        """Setup ROS2 node in separate thread."""

        def ros_thread_func():
            try:
                rclpy.init()
                self.ros_node = UniversalVisualizerNode(
                    self.controller_type, self.topic_mapping, self.data_callback)
                rclpy.spin(self.ros_node)
            except Exception as e:
                print(f"ROS node error: {e}")
            finally:
                if self.ros_node:
                    self.ros_node.destroy_node()
                rclpy.shutdown()

        self.ros_thread = threading.Thread(target=ros_thread_func, daemon=True)
        self.ros_thread.start()

    def data_callback(self, data_type: str, data):
        """Callback for receiving data from ROS node."""

        try:
            if data_type == 'vehicle_state':
                self.current_vehicle_state = data
                self.vehicle_history.append((time.time(), data))

            elif data_type == 'control_command':
                self.current_control = data
                self.control_history.append((time.time(), data))

            elif data_type == 'reference_trajectory':
                self.reference_trajectory = data

            elif data_type == 'performance_metrics':
                self.current_metrics = data

            elif data_type == 'state_error':
                self.error_history.append((time.time(), data))

        except Exception as e:
            print(f"Error in data callback: {e}")

    def update_status_labels(self):
        """Update status labels in control panel."""

        try:
            # Controller status
            if self.current_metrics.controller_active:
                self.controller_status_label.config(text="Active", foreground="green")
            elif self.current_metrics.emergency_stop:
                self.controller_status_label.config(text="Emergency Stop", foreground="red")
            else:
                self.controller_status_label.config(text="Inactive", foreground="orange")

            # Path ready status
            if self.current_metrics.path_ready:
                self.path_ready_label.config(text="Ready", foreground="green")
            else:
                self.path_ready_label.config(text="Not Ready", foreground="red")

            # Emergency stop status
            if self.current_metrics.emergency_stop:
                self.emergency_stop_label.config(text="ACTIVE", foreground="red")
            else:
                self.emergency_stop_label.config(text="Normal", foreground="green")

            # Vehicle state values
            self.position_label.config(
                text=f"({self.current_vehicle_state.x:.2f}, {self.current_vehicle_state.y:.2f})")
            self.velocity_label.config(text=f"{self.current_vehicle_state.velocity:.2f} m/s")
            self.steering_label.config(text=f"{self.current_vehicle_state.steering_angle:.3f} rad")
            self.acceleration_label.config(text=f"{self.current_vehicle_state.acceleration:.2f} m/s²")
            self.state_error_label.config(text=f"{self.current_metrics.state_error:.3f}")

        except Exception as e:
            print(f"Error updating status labels: {e}")

    def update_trajectory_plot(self):
        """Update the trajectory plot."""

        try:
            if not hasattr(self, 'traj_ax'):
                return

            self.traj_ax.clear()

            # Plot reference trajectory
            if self.reference_trajectory:
                ref_x = [point['x'] for point in self.reference_trajectory]
                ref_y = [point['y'] for point in self.reference_trajectory]
                self.traj_ax.plot(ref_x, ref_y, 'b-', linewidth=2, label='Reference Trajectory', alpha=0.7)

            # Plot vehicle history
            if len(self.vehicle_history) > 1:
                hist_x = [state[1].x for state in self.vehicle_history]
                hist_y = [state[1].y for state in self.vehicle_history]
                self.traj_ax.plot(hist_x, hist_y, 'r-', linewidth=1, label='Vehicle Path', alpha=0.8)

            # Plot current vehicle position
            if self.current_vehicle_state.timestamp > 0:
                self.traj_ax.plot(self.current_vehicle_state.x, self.current_vehicle_state.y,
                                  'ro', markersize=8, label='Current Position')

                # Draw vehicle orientation arrow
                arrow_length = 0.5
                dx = arrow_length * np.cos(self.current_vehicle_state.yaw)
                dy = arrow_length * np.sin(self.current_vehicle_state.yaw)
                self.traj_ax.arrow(self.current_vehicle_state.x, self.current_vehicle_state.y,
                                   dx, dy, head_width=0.1, head_length=0.1, fc='red', ec='red')

            self.traj_ax.set_title("Vehicle Trajectory and Reference Path")
            self.traj_ax.set_xlabel("X Position [m]")
            self.traj_ax.set_ylabel("Y Position [m]")
            self.traj_ax.grid(True, alpha=0.3)

            # Only show legend if there are labeled elements
            handles, labels = self.traj_ax.get_legend_handles_labels()
            if handles:
                self.traj_ax.legend()

            self.traj_ax.set_aspect('equal')

            self.traj_canvas.draw()

        except Exception as e:
            print(f"Error updating trajectory plot: {e}")

    def update_control_plots(self):
        """Update the control input plots."""

        try:
            if not hasattr(self, 'accel_ax') or len(self.control_history) < 2:
                return

            # Get time and control data
            times = [t[0] for t in self.control_history]
            commanded_accelerations = [t[1].acceleration for t in self.control_history]
            steering_angles = [t[1].steering_angle for t in self.control_history]

            # Get actual acceleration from vehicle state
            actual_accelerations = []
            for t in self.vehicle_history:
                actual_accelerations.append(t[1].acceleration)

            # Ensure arrays are same length
            min_len = min(len(times), len(commanded_accelerations), len(actual_accelerations))
            times = times[:min_len]
            commanded_accelerations = commanded_accelerations[:min_len]
            actual_accelerations = actual_accelerations[:min_len]

            # Normalize time to start from 0
            if times:
                start_time = times[0]
                times = [t - start_time for t in times]

            # Clear and plot acceleration
            self.accel_ax.clear()
            if len(commanded_accelerations) > 0:
                self.accel_ax.plot(times, commanded_accelerations, 'b-', linewidth=2, label='Commanded')
            if len(actual_accelerations) > 0:
                self.accel_ax.plot(times[:len(actual_accelerations)], actual_accelerations,
                                   'r-', linewidth=2, alpha=0.7, label='Actual')
            self.accel_ax.set_title("Acceleration Command vs Actual")
            self.accel_ax.set_ylabel("Acceleration [m/s²]")
            self.accel_ax.grid(True, alpha=0.3)

            # Only show legend if there are labeled elements
            handles, labels = self.accel_ax.get_legend_handles_labels()
            if handles:
                self.accel_ax.legend()

            self.accel_ax.axhline(y=0, color='k', linestyle='--', alpha=0.5)

            # Clear and plot steering
            self.steer_ax.clear()
            self.steer_ax.plot(times, steering_angles, 'r-', linewidth=2)
            self.steer_ax.set_title("Steering Angle Command")
            self.steer_ax.set_xlabel("Time [s]")
            self.steer_ax.set_ylabel("Steering Angle [rad]")
            self.steer_ax.grid(True, alpha=0.3)
            self.steer_ax.axhline(y=0, color='k', linestyle='--', alpha=0.5)

            self.control_fig.tight_layout()
            self.control_canvas.draw()

        except Exception as e:
            print(f"Error updating control plots: {e}")

    def update_performance_plots(self):
        """Update the performance plots."""

        try:
            if not hasattr(self, 'error_ax'):
                return

            # State error plot
            if len(self.error_history) > 1:
                error_times = [t[0] for t in self.error_history]
                error_values = [t[1] for t in self.error_history]

                if error_times:
                    start_time = error_times[0]
                    error_times = [t - start_time for t in error_times]

                self.error_ax.clear()
                self.error_ax.plot(error_times, error_values, 'g-', linewidth=2)
                self.error_ax.set_title("State Error")
                self.error_ax.set_ylabel("Error Magnitude")
                self.error_ax.grid(True, alpha=0.3)

            # Velocity plot
            if len(self.vehicle_history) > 1:
                vel_times = [t[0] for t in self.vehicle_history]
                velocities = [t[1].velocity for t in self.vehicle_history]

                if vel_times:
                    start_time = vel_times[0]
                    vel_times = [t - start_time for t in vel_times]

                self.vel_ax.clear()
                self.vel_ax.plot(vel_times, velocities, 'm-', linewidth=2, label='Actual')

                # Add reference velocity if available
                if self.reference_trajectory:
                    ref_velocities = [point['v'] for point in self.reference_trajectory]
                    if len(ref_velocities) > 0:
                        ref_times = np.linspace(0, vel_times[-1] if vel_times else 10, len(ref_velocities))
                        self.vel_ax.plot(ref_times, ref_velocities, 'b--', linewidth=2,
                                         label='Reference', alpha=0.7)

                self.vel_ax.set_title("Velocity Profile")
                self.vel_ax.set_xlabel("Time [s]")
                self.vel_ax.set_ylabel("Velocity [m/s]")
                self.vel_ax.grid(True, alpha=0.3)

                # Only show legend if there are labeled elements
                handles, labels = self.vel_ax.get_legend_handles_labels()
                if handles:
                    self.vel_ax.legend()

            self.perf_fig.tight_layout()
            self.perf_canvas.draw()

        except Exception as e:
            print(f"Error updating performance plots: {e}")

    def update_diagnostics_text(self):
        """Update the diagnostics text display."""

        try:
            if not hasattr(self, 'diag_text'):
                return

            # Clear text
            self.diag_text.delete(1.0, tk.END)

            # Add current diagnostics
            diag_info = f"""{self.controller_type.value.upper()} Controller Diagnostics
{'='*60}

Controller Information:
  Type: {self.controller_type.value.upper()}
  Status: {'Active' if self.current_metrics.controller_active else 'Inactive'}
  Emergency Stop: {self.current_metrics.emergency_stop}
  Path Ready: {self.current_metrics.path_ready}

Performance Metrics:
  Control Frequency: {self.current_metrics.control_frequency:.1f} Hz
  Average Control Time: {self.current_metrics.avg_control_time*1000:.2f} ms
  Maximum Control Time: {self.current_metrics.max_control_time*1000:.2f} ms
  Consecutive Failures: {self.current_metrics.consecutive_failures}
  State Error: {self.current_metrics.state_error:.4f}

Vehicle State:
  Position: ({self.current_vehicle_state.x:.3f}, {self.current_vehicle_state.y:.3f})
  Velocity: {self.current_vehicle_state.velocity:.3f} m/s
  Yaw: {self.current_vehicle_state.yaw:.3f} rad
  Steering Angle: {self.current_vehicle_state.steering_angle:.3f} rad
  Acceleration: {self.current_vehicle_state.acceleration:.3f} m/s²

Control Commands:
  Commanded Acceleration: {self.current_control.acceleration:.3f} m/s²
  Steering: {self.current_control.steering_angle:.3f} rad
  Speed Command: {self.current_control.speed:.3f} m/s

Topic Configuration:
  Control Output: {self.topic_mapping.control_output}
  Odometry: {self.topic_mapping.odometry}
  Trajectory: {self.topic_mapping.trajectory}
  Diagnostics: {self.topic_mapping.diagnostics}

Reference Trajectory:
  Number of Points: {len(self.reference_trajectory)}

Data History:
  Vehicle History Points: {len(self.vehicle_history)}
  Control History Points: {len(self.control_history)}
  Error History Points: {len(self.error_history)}

Last Updated: {time.strftime('%H:%M:%S')}
"""

            self.diag_text.insert(tk.END, diag_info)

        except Exception as e:
            print(f"Error updating diagnostics text: {e}")

    def update_plots(self):
        """Main update function called periodically."""

        if not self.animation_running:
            return

        try:
            # Update all displays
            self.update_status_labels()
            self.update_trajectory_plot()
            self.update_control_plots()
            self.update_performance_plots()
            self.update_diagnostics_text()

        except Exception as e:
            print(f"Error in update_plots: {e}")

        # Schedule next update
        update_rate = 1000 // self.config.get('update_rate_hz', 10)
        self.root.after(update_rate, self.update_plots)

    def export_data(self):
        """Export collected data to files."""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv"), ("All files", "*.*")]
            )

            if filename:
                data = {
                    'controller_type': self.controller_type.value,
                    'timestamp': time.time(),
                    'vehicle_history': [{'timestamp': t, 'state': asdict(s)} for t, s in self.vehicle_history],
                    'control_history': [{'timestamp': t, 'control': asdict(c)} for t, c in self.control_history],
                    'error_history': [{'timestamp': t, 'error': e} for t, e in self.error_history],
                    'reference_trajectory': self.reference_trajectory,
                    'current_metrics': asdict(self.current_metrics),
                    'config': self.config
                }

                if filename.endswith('.json'):
                    with open(filename, 'w') as f:
                        json.dump(data, f, indent=2, default=str)
                elif filename.endswith('.csv'):
                    # Export as CSV (simplified)
                    import csv
                    with open(filename, 'w', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(['timestamp', 'x', 'y', 'velocity', 'yaw', 'steering', 'acceleration',
                                         'cmd_acceleration', 'cmd_steering', 'state_error'])

                        for i, (t, state) in enumerate(self.vehicle_history):
                            control = self.control_history[i][1] if i < len(self.control_history) else ControlCommand()
                            error = self.error_history[i][1] if i < len(self.error_history) else 0.0

                            writer.writerow([t, state.x, state.y, state.velocity, state.yaw,
                                             state.steering_angle, state.acceleration,
                                             control.acceleration, control.steering_angle, error])

                messagebox.showinfo("Export", f"Data exported to {filename}")

        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {e}")

    def clear_history(self):
        """Clear all collected data history."""
        self.vehicle_history.clear()
        self.control_history.clear()
        self.error_history.clear()
        messagebox.showinfo("Clear", "Data history cleared")

    def save_config(self):
        """Save current configuration to file."""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".yaml",
                filetypes=[("YAML files", "*.yaml"), ("JSON files", "*.json"), ("All files", "*.*")]
            )

            if filename:
                if filename.endswith('.yaml') or filename.endswith('.yml'):
                    with open(filename, 'w') as f:
                        yaml.dump(self.config, f, default_flow_style=False)
                else:
                    with open(filename, 'w') as f:
                        json.dump(self.config, f, indent=2)

                messagebox.showinfo("Save Config", f"Configuration saved to {filename}")

        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save configuration: {e}")

    def on_closing(self):
        """Handle application closing."""

        self.animation_running = False

        try:
            if self.ros_node:
                self.ros_node.destroy_node()
        except BaseException:
            pass

        self.root.destroy()

    def run(self):
        """Run the GUI application."""

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()


def main():
    """Main entry point."""

    import argparse

    parser = argparse.ArgumentParser(description="Universal F1TENTH Controller Visualizer")
    parser.add_argument('--config', '-c', type=str, help='Configuration file path')
    parser.add_argument(
        '--controller',
        type=str,
        choices=[
            'lqr',
            'lqg',
            'mpc',
            'pid',
            'pure_pursuit',
            'stanley',
            'custom'],
        default='lqr',
        help='Controller type to visualize')

    args = parser.parse_args()

    try:
        # Create and run GUI
        app = UniversalControllerVisualizerGUI(config_file=args.config)

        # Override controller type from command line
        if args.controller:
            app.controller_type = ControllerType(args.controller)
            app.controller_type_label.config(text=args.controller.upper())

        print(f"🚀 Universal Controller Visualizer starting...")
        print(f"📊 Controller Type: {app.controller_type.value.upper()}")
        print(f"🔧 Config: {args.config if args.config else 'Default'}")
        print("Press Ctrl+C to stop...")

        app.run()

    except ImportError as e:
        messagebox.showerror("Error",
                             f"Missing dependencies: {e}\n\nPlease install required packages.")
    except KeyboardInterrupt:
        print("\n🛑 Universal Visualizer interrupted by user")
    except Exception as e:
        print(f"❌ Universal Visualizer error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
