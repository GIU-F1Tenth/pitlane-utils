#!/usr/bin/env python3

"""
Quick test script for the universal visualizer fixes
"""

import sys
import os
import subprocess
import time
from pathlib import Path


def test_visualizer(controller_type, duration=3):
    """Test a visualizer for a short duration."""

    script_dir = Path(__file__).parent
    cmd = [
        'python3', 'launch_visualizer.py', controller_type
    ]

    print(f"🧪 Testing {controller_type.upper()} visualizer...")

    try:
        # Start the process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=script_dir,
            text=True
        )

        # Wait a bit to see if it starts successfully
        time.sleep(duration)

        # Check if process is still running (good sign)
        if process.poll() is None:
            print(f"✅ {controller_type.upper()} visualizer started successfully")
            process.terminate()
            process.wait(timeout=5)
            return True
        else:
            # Process ended, check for errors
            stdout, stderr = process.communicate()
            print(f"❌ {controller_type.upper()} visualizer failed to start")
            if stderr:
                print(f"Error: {stderr}")
            return False

    except Exception as e:
        print(f"❌ {controller_type.upper()} test failed: {e}")
        return False


def main():
    print("🚀 Universal Controller Visualizer Test Suite")
    print("=" * 60)

    # Test different controller types
    controllers = ['lqr', 'lqg', 'mpc']

    results = {}
    for controller in controllers:
        results[controller] = test_visualizer(controller)
        print()

    print("📊 Test Results:")
    print("-" * 30)
    for controller, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {controller.upper()}: {status}")

    total_tests = len(results)
    passed_tests = sum(results.values())

    print(f"\n🎯 Overall: {passed_tests}/{total_tests} tests passed")

    if passed_tests == total_tests:
        print("\n🎉 All visualizers are working correctly!")
        print("\n📖 Usage:")
        print("  python3 launch_visualizer.py lqr")
        print("  python3 launch_visualizer.py lqg")
        print("  python3 launch_visualizer.py mpc")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} visualizer(s) need attention")


if __name__ == '__main__':
    main()
