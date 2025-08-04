#!/usr/bin/env python3

"""
MPC Controller Visualizer Launch File

Specialized launch file for MPC controller visualization with optimized settings.
"""

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    """Generate launch description for MPC controller visualizer."""

    # Package directory
    pkg_dir = FindPackageShare('controller_visualizer')

    # Launch arguments
    config_file_arg = DeclareLaunchArgument(
        'config_file',
        default_value=PathJoinSubstitution([pkg_dir, 'config', 'mpc_config.yaml']),
        description='Path to MPC visualizer configuration file'
    )

    node_name_arg = DeclareLaunchArgument(
        'node_name',
        default_value='mpc_visualizer',
        description='Name for the visualizer node'
    )

    # MPC Visualizer process
    mpc_visualizer_process = ExecuteProcess(
        cmd=[
            'python3',
            PathJoinSubstitution([pkg_dir, 'src', 'universal_controller_visualizer.py']),
            '--controller', 'mpc',
            '--config', LaunchConfiguration('config_file')
        ],
        name=LaunchConfiguration('node_name'),
        output='screen'
    )

    return LaunchDescription([
        config_file_arg,
        node_name_arg,
        mpc_visualizer_process
    ])
