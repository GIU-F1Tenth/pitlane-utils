#!/usr/bin/env python3

"""
Visualization Code Migration Script

This script removes the old visualization code from adaptive_lqr_lqg and provides
migration instructions for using the new universal controller visualizer.
"""

import os
import shutil
import sys
from pathlib import Path


def main():
    print("🔄 F1TENTH Controller Visualization Migration")
    print("=" * 60)

    # Define paths
    old_package_dir = Path("/home/mohammedazab/ws/src/race_stack/lqg_controller/adaptive_lqr_lqg")
    scripts_dir = old_package_dir / "scripts"

    # Files to remove (visualization-related)
    files_to_remove = [
        "lqr_visualizer.py",
        "lqr_visualizer_standalone.py",
        "lqg_visualizer.py",
        "launch_visualizer.sh",
        "visualizer_config.ini",
        "requirements.txt",  # Will be replaced with controller-only requirements
        "requirements_gui.txt",
        "VISUALIZER_SUMMARY.md",
        "README_GUI.md",
        "demo.py",
        "launch_gui.py",
        "lqr_parameter_gui.py",
        "lqr_parameter_gui_standalone.py"
    ]

    # Create backup directory
    backup_dir = old_package_dir / "backup_visualization"
    backup_dir.mkdir(exist_ok=True)

    print(f"📁 Package directory: {old_package_dir}")
    print(f"💾 Backup directory: {backup_dir}")
    print()

    # Show what will be removed
    print("📋 Files scheduled for removal:")
    files_found = []
    for file_name in files_to_remove:
        file_path = scripts_dir / file_name
        if file_path.exists():
            files_found.append(file_path)
            print(f"  ✓ {file_name}")
        else:
            print(f"  ✗ {file_name} (not found)")

    print()
    print(f"📊 Total files to remove: {len(files_found)}")
    print()

    # Ask for confirmation
    response = input("🤔 Proceed with migration? (y/N): ").lower().strip()
    if response != 'y' and response != 'yes':
        print("❌ Migration cancelled by user")
        return

    print()
    print("🚀 Starting migration...")

    # Backup files before removal
    print("💾 Creating backup...")
    backup_count = 0
    for file_path in files_found:
        try:
            backup_path = backup_dir / file_path.name
            shutil.copy2(file_path, backup_path)
            backup_count += 1
            print(f"  📋 Backed up: {file_path.name}")
        except Exception as e:
            print(f"  ❌ Failed to backup {file_path.name}: {e}")

    print(f"✅ Backed up {backup_count} files")
    print()

    # Remove files
    print("🗑️  Removing visualization files...")
    removed_count = 0
    for file_path in files_found:
        try:
            file_path.unlink()
            removed_count += 1
            print(f"  🗑️  Removed: {file_path.name}")
        except Exception as e:
            print(f"  ❌ Failed to remove {file_path.name}: {e}")

    print(f"✅ Removed {removed_count} files")
    print()

    # Create minimal requirements.txt for controller only
    create_controller_requirements(scripts_dir)

    # Create migration notice
    create_migration_notice(scripts_dir)

    print("🎉 Migration completed successfully!")
    print()
    print("📖 Next Steps:")
    print("  1. Use the new universal visualizer in pitlane-utils/controller_visualizer/")
    print("  2. Launch with: ros2 launch controller_visualizer lqr_visualizer.launch.py")
    print("  3. Or: ros2 launch controller_visualizer lqg_visualizer.launch.py")
    print("  4. Check backup_visualization/ for old files if needed")
    print()
    print("🔗 Universal visualizer supports both LQR and LQG controllers with improved features!")


def create_controller_requirements(scripts_dir):
    """Create a minimal requirements file for controller-only functionality."""

    controller_requirements = """# F1TENTH LQR/LQG Controller Requirements
# Core controller dependencies only (visualization moved to pitlane-utils)

# ROS2 Python client
rclpy

# Numerical computing
numpy>=1.20.0
scipy>=1.7.0

# Configuration
pyyaml

# Transformations
tf-transformations

# Optional: Enhanced numerical operations
numba>=0.56.0

# Development/Testing (optional)
pytest>=6.0.0
flake8>=4.0.0

# Note: Visualization dependencies moved to pitlane-utils/controller_visualizer
# For visualization, use: ros2 launch controller_visualizer lqr_visualizer.launch.py
"""

    req_path = scripts_dir / "requirements.txt"
    with open(req_path, 'w') as f:
        f.write(controller_requirements)

    print(f"📝 Created minimal requirements.txt")


def create_migration_notice(scripts_dir):
    """Create a migration notice explaining the changes."""

    migration_notice = """# Visualization Migration Notice

## ⚠️ Important: Visualization Code Moved

The visualization code for LQR and LQG controllers has been **moved** to a new location for better organization and reusability.

### Old Location (Removed)
- `adaptive_lqr_lqg/scripts/lqr_visualizer.py` ❌
- `adaptive_lqr_lqg/scripts/lqg_visualizer.py` ❌
- `adaptive_lqr_lqg/scripts/lqr_parameter_gui.py` ❌

### New Location (Universal Visualizer)
- `pitlane-utils/controller_visualizer/` ✅

## 🚀 How to Use the New Visualizer

### For LQR Controller
```bash
ros2 launch controller_visualizer lqr_visualizer.launch.py
```

### For LQG Controller
```bash
ros2 launch controller_visualizer lqg_visualizer.launch.py
```

### Universal Usage (Any Controller)
```bash
ros2 launch controller_visualizer universal_visualizer.launch.py controller_type:=lqr
ros2 launch controller_visualizer universal_visualizer.launch.py controller_type:=lqg
ros2 launch controller_visualizer universal_visualizer.launch.py controller_type:=mpc
```

## ✨ New Features

The universal visualizer provides **enhanced features**:

- **Multi-controller support** (LQR, LQG, MPC, etc.)
- **Improved performance** with optimized plotting
- **Better configuration** with YAML config files
- **Data export** capabilities (JSON, CSV)
- **Real-time diagnostics** with enhanced monitoring
- **Unified interface** for all F1TENTH controllers

## 🔄 Migration Benefits

1. **Centralized visualization**: One tool for all controllers
2. **Reduced duplication**: No more scattered visualization code
3. **Enhanced features**: Better plots, export, configuration
4. **Future-proof**: Supports new controllers easily
5. **Cleaner packages**: Controllers focus on control logic only

## 📋 Configuration

The new visualizer uses YAML configuration files:

- `config/lqr_config.yaml` - LQR-specific settings
- `config/lqg_config.yaml` - LQG-specific settings
- `config/visualizer_config.yaml` - Universal settings

## 🔧 Custom Configuration

For custom topic mappings, edit the config files:

```yaml
topics:
  control_output: "/drive"
  odometry: "/odom"
  diagnostics: "/my_controller/diagnostics"
  state_error: "/my_controller/state_error"
```

## 📚 Documentation

See the full documentation:
- `pitlane-utils/controller_visualizer/README.md`
- Launch files with examples
- Configuration file comments

## 💾 Backup

Old visualization files are backed up in:
- `backup_visualization/` directory

## 🤝 Support

For questions or issues:
- Check the README in `pitlane-utils/controller_visualizer/`
- Open GitHub issue if problems persist
- Use the universal visualizer for all new projects

---

**The new universal visualizer provides a better experience for all F1TENTH controllers!** 🏁
"""

    notice_path = scripts_dir / "MIGRATION_NOTICE.md"
    with open(notice_path, 'w') as f:
        f.write(migration_notice)

    print(f"📝 Created migration notice")


if __name__ == "__main__":
    main()
