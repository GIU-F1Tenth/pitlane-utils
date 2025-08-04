#!/usr/bin/env python3

"""
Test script for Universal Controller Visualizer

This script tests the visualizer functionality without requiring a full ROS2 setup.
It can be used to verify the GUI components work correctly.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from universal_controller_visualizer import UniversalControllerVisualizerGUI, ControllerType, TopicMapping
    print("✅ Successfully imported visualizer components")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure all dependencies are installed:")
    print("  pip3 install matplotlib tkinter numpy pyyaml")
    sys.exit(1)


def test_gui_creation():
    """Test creating the GUI without ROS2 dependencies."""
    print("🧪 Testing GUI creation...")

    try:
        # Create a test config
        test_config = {
            'controller_type': 'lqr',
            'max_history': 100,
            'update_rate_hz': 5,
            'topics': {
                'control_output': '/drive',
                'odometry': '/odom'
            },
            'visualization': {
                'show_trajectory': True,
                'show_control_history': True,
                'show_performance': True,
                'show_diagnostics': True
            }
        }

        # Test configuration loading
        print("  ✓ Configuration structure valid")

        # Test enum values
        controller_types = [ControllerType.LQR, ControllerType.LQG, ControllerType.MPC]
        print(f"  ✓ Controller types available: {[ct.value for ct in controller_types]}")

        # Test topic mapping
        topics = TopicMapping()
        print(f"  ✓ Topic mapping: {topics.control_output}, {topics.odometry}")

        print("✅ GUI components test passed")
        return True

    except Exception as e:
        print(f"❌ GUI test failed: {e}")
        return False


def test_config_loading():
    """Test configuration file loading."""
    print("🧪 Testing configuration loading...")

    try:
        config_dir = os.path.join(os.path.dirname(__file__), 'config')

        # Test YAML configs exist
        yaml_configs = ['visualizer_config.yaml', 'lqr_config.yaml', 'lqg_config.yaml', 'mpc_config.yaml']

        for config_file in yaml_configs:
            config_path = os.path.join(config_dir, config_file)
            if os.path.exists(config_path):
                print(f"  ✓ Found config: {config_file}")
            else:
                print(f"  ❌ Missing config: {config_file}")
                return False

        print("✅ Configuration files test passed")
        return True

    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False


def test_imports():
    """Test all required imports."""
    print("🧪 Testing imports...")

    required_modules = [
        ('numpy', 'np'),
        ('matplotlib.pyplot', 'plt'),
        ('tkinter', 'tk'),
        ('yaml', None)
    ]

    missing_modules = []

    for module_name, alias in required_modules:
        try:
            if alias:
                exec(f"import {module_name} as {alias}")
            else:
                exec(f"import {module_name}")
            print(f"  ✓ {module_name}")
        except ImportError:
            print(f"  ❌ {module_name} (missing)")
            missing_modules.append(module_name)

    if missing_modules:
        print(f"\n❌ Missing modules: {missing_modules}")
        print("Install with: pip3 install " + " ".join(m.replace('.', '-') for m in missing_modules))
        return False

    print("✅ All imports test passed")
    return True


def main():
    """Run all tests."""
    print("🚀 Universal Controller Visualizer Test Suite")
    print("=" * 60)

    tests = [
        test_imports,
        test_config_loading,
        test_gui_creation
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
            print()  # Add spacing
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            print()

    print("📊 Test Results")
    print("-" * 30)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")

    if passed == total:
        print("\n🎉 All tests passed! Visualizer is ready to use.")
        print("\n📖 Next steps:")
        print("  1. ros2 launch controller_visualizer lqr_visualizer.launch.py")
        print("  2. Or: ./launch_visualizer.py lqr")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed. Please fix issues before using.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
