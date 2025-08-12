#!/usr/bin/env python3

"""
Universal Controller Visualizer Launch File

This launch file starts the universal controller visualizer with configurable parameters.
It can be used to visualize any F1TENTH controller type (LQR, LQG, MPC, etc.).
"""

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    """Generate launch description for universal controller visualizer."""

    # Package directory
    pkg_dir = FindPackageShare('controller_visualizer')

    # Launch arguments
    controller_type_arg = DeclareLaunchArgument(
        'controller_type',
        default_value='lqr',
        description='Controller type to visualize (lqr, lqg, mpc, pid, pure_pursuit, stanley, custom)'
    )

    config_file_arg = DeclareLaunchArgument(
        'config_file',
        default_value=PathJoinSubstitution([pkg_dir, 'config', 'visualizer_config.yaml']),
        description='Path to visualizer configuration file'
    )

    # Visualizer process
    visualizer_process = ExecuteProcess(
        cmd=[
            'python3',
            PathJoinSubstitution([pkg_dir, 'src', 'universal_controller_visualizer.py']),
            '--controller', LaunchConfiguration('controller_type'),
            '--config', LaunchConfiguration('config_file')
        ],
        name='universal_controller_visualizer',
        output='screen'
    )

    return LaunchDescription([
        controller_type_arg,
        config_file_arg,
        visualizer_process
    ])
