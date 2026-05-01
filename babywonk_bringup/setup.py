from setuptools import find_packages, setup
from pathlib import Path

package_name = 'babywonk_bringup'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (
            str(Path('share') / package_name / 'config'),
            [str(f) for f in Path('config').glob('*.yaml')],
        ),
        (
            str(Path('share') / package_name / 'launch'),
            [str(f) for f in Path('launch').glob('*_launch.py')],
        ),
        (
            str(Path('share') / package_name / 'rviz'),
            [str(f) for f in Path('rviz').glob('*.rviz')],
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='mgarrett12',
    maintainer_email='mgarrett12@cub.uca.edu',
    description='ROS 2 Jazzy bringup package for BabyWonk differential drive robot',
    license='GPL-3.0-only',
    extras_require={'test': ['pytest']},
    entry_points={
        'console_scripts': [
            'pico_interface = babywonk_bringup.pico_interface:main',
            'basic_pico_interface = babywonk_bringup.basic_pico_interface:main',
            'navigator = babywonk_bringup.navigator:main',
            'aruco_detector = babywonk_bringup.aruco_detector:main',
            'lidar_test = babywonk_bringup.lidar_test:main',
        ],
    },
)
