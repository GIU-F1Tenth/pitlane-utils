from setuptools import setup, find_packages
import os
from glob import glob

package_name = 'controller_visualizer'

setup(
    name=package_name,
    version='2.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Launch files
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        # Config files
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'config'), glob('config/*.json')),
        # Scripts
        (os.path.join('share', package_name, 'src'), glob('src/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Mohammed Azab',
    maintainer_email='mohammed@azab.io',
    description='Universal F1TENTH Controller Visualizer - Real-time visualization tool for LQR, LQG, MPC, and other F1TENTH controllers',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'universal_visualizer = src.universal_controller_visualizer:main',
            'launch_visualizer = launch_visualizer:main',
        ],
    },
)
