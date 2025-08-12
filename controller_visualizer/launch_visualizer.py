#!/usr/bin/env python3

"""
Quick Launch Script for Universal Controller Visualizer

This script provides a simple command-line interface to launch the visualizer
with common configurations.
"""

import argparse
import os
import sys
import subprocess
from pathlib import Path


def list_available_configs():
    """List all available configuration files."""
    script_dir = Path(__file__).parent
    config_dir = script_dir / 'config'

    print("📁 Available Configuration Files:")
    print("=" * 40)

    if not config_dir.exists():
        print("❌ Config directory not found!")
        return

    configs = list(config_dir.glob('*.yaml')) + list(config_dir.glob('*.json'))

    if not configs:
        print("❌ No configuration files found!")
        return

    for config_file in sorted(configs):
        size = config_file.stat().st_size
        print(f"  📄 {config_file.name} ({size} bytes)")

        # Try to read first few lines for description
        try:
            with open(config_file, 'r') as f:
                lines = f.readlines()[:5]
                for line in lines:
                    if line.strip().startswith('#') and ('controller' in line.lower() or 'config' in line.lower()):
                        desc = line.strip().lstrip('# ').strip()
                        print(f"     💡 {desc}")
                        break
        except BaseException:
            pass

    print(f"\n📊 Total: {len(configs)} configuration files")


def check_dependencies():
    """Check if required dependencies are available."""
    required_modules = ['matplotlib', 'numpy', 'yaml', 'tkinter']
    missing = []

    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)

    if missing:
        print("❌ Missing dependencies:")
        for module in missing:
            print(f"  - {module}")
        print("\n💡 Install with:")
        print(f"  pip3 install {' '.join(missing)}")
        print("  sudo apt install python3-tk  # for tkinter")
        return False

    return True


def main():
    # Show usage examples if no arguments provided
    if len(sys.argv) == 1:
        print("🚀 Universal F1TENTH Controller Visualizer")
        print("=" * 50)
        print("\n📖 Usage Examples:")
        print("  python3 launch_visualizer.py lqr")
        print("  python3 launch_visualizer.py lqg")
        print("  python3 launch_visualizer.py mpc")
        print("  python3 launch_visualizer.py lqr --config custom_config.yaml")
        print("\n🎮 Available Controllers:")
        print("  • lqr         - Linear Quadratic Regulator")
        print("  • lqg         - Linear Quadratic Gaussian")
        print("  • mpc         - Model Predictive Control")
        print("  • pid         - PID Controller")
        print("  • pure_pursuit - Pure Pursuit Controller")
        print("  • stanley     - Stanley Controller")
        print("  • custom      - Custom Controller")
        print("\n🔧 Options:")
        print("  --config, -c  - Custom configuration file")
        print("  --preset      - Quick presets (debug, performance, minimal, full)")
        print("  --node-name   - ROS2 node name")
        print("\n💡 Quick Start:")
        print("  python3 launch_visualizer.py lqr")
        print("  Or use ROS2 launch: ros2 launch controller_visualizer lqr_visualizer.launch.py")
        sys.exit(0)

    parser = argparse.ArgumentParser(
        description="Launch Universal F1TENTH Controller Visualizer",
        epilog="Examples:\n"
               "  python3 launch_visualizer.py lqr\n"
               "  python3 launch_visualizer.py mpc --config custom.yaml\n"
               "  python3 launch_visualizer.py lqg --preset performance",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Controller type
    parser.add_argument('controller',
                        choices=['lqr', 'lqg', 'mpc', 'pid', 'pure_pursuit', 'stanley', 'custom'],
                        help='Controller type to visualize')

    # Configuration options
    parser.add_argument('--config', '-c',
                        help='Custom configuration file path')

    parser.add_argument('--node-name',
                        default='controller_visualizer',
                        help='ROS2 node name')

    # Quick presets
    parser.add_argument('--preset',
                        choices=['debug', 'performance', 'minimal', 'full'],
                        help='Quick configuration preset')

    parser.add_argument('--list-configs', action='store_true',
                        help='List available configuration files')

    args = parser.parse_args()

    # Handle list configs option
    if args.list_configs:
        list_available_configs()
        return

    # Get script directory (handle both direct execution and ROS2 launch)
    script_dir = Path(__file__).parent.resolve()

    print(f"🔧 Script directory: {script_dir}")

    # Check dependencies first
    if not check_dependencies():
        print("\n❌ Please install missing dependencies before continuing.")
        sys.exit(1)

    # Determine config file
    if args.config:
        config_file = Path(args.config)
        if not config_file.is_absolute():
            config_file = script_dir / args.config
    elif args.preset:
        config_file = script_dir / 'config' / f'{args.preset}_config.yaml'
    else:
        config_file = script_dir / 'config' / f'{args.controller}_config.yaml'
        if not config_file.exists():
            config_file = script_dir / 'config' / 'visualizer_config.yaml'

    # Check if config file exists
    if not config_file.exists():
        print(f"❌ Configuration file not found: {config_file}")
        print(f"\n📁 Looking in: {script_dir / 'config'}")
        print("\n📋 Available configs:")
        config_dir = script_dir / 'config'
        if config_dir.exists():
            for f in sorted(config_dir.glob('*.yaml')):
                print(f"  ✓ {f.name}")
            for f in sorted(config_dir.glob('*.json')):
                print(f"  ✓ {f.name}")
        else:
            print("  ❌ Config directory not found!")
        print(f"\n💡 Use: python3 {Path(__file__).name} {args.controller} --list-configs")
        sys.exit(1)

    # Find visualizer script
    visualizer_script = script_dir / 'src' / 'universal_controller_visualizer.py'
    if not visualizer_script.exists():
        print(f"❌ Visualizer script not found: {visualizer_script}")
        print(f"📁 Script directory: {script_dir}")
        print("💡 Make sure you're running from the controller_visualizer directory")
        sys.exit(1)

    # Build command
    cmd = [
        'python3', str(visualizer_script),
        '--controller', args.controller,
        '--config', str(config_file)
    ]

    # Launch visualizer
    print(f"🚀 Launching {args.controller.upper()} Controller Visualizer...")
    print(f"📁 Config: {config_file.name} ({config_file})")
    print(f"🔧 Node: {args.node_name}")
    print(f"📄 Script: {visualizer_script.name}")
    print("Press Ctrl+C to stop...")
    print("=" * 60)

    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Visualizer stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error launching visualizer: {e}")
        print(f"\n🔍 Debug info:")
        print(f"  Command: {' '.join(cmd)}")
        print(f"  Working directory: {os.getcwd()}")
        print(f"  Script exists: {visualizer_script.exists()}")
        print(f"  Config exists: {config_file.exists()}")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        print("💡 Make sure Python 3 is installed and the visualizer script exists")
        sys.exit(1)


if __name__ == '__main__':
    main()
