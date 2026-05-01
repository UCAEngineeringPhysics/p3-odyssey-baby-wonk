from setuptools import find_packages, setup
from pathlib import Path

package_name = 'babywonk_navigation'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (
            str(Path('share') / package_name / 'configs'),
            [str(f) for f in Path('configs').glob('*.yaml')],
        ),
        (
            str(Path('share') / package_name / 'launch'),
            [str(f) for f in Path('launch').glob('*_launch.py')],
        ),
        (
            str(Path('share') / package_name / 'rviz'),
            [str(f) for f in Path('rviz').glob('*.rviz')],
        ),
        (
            str(Path('share') / package_name / 'maps'),
            [str(f) for f in Path('maps').glob('*')],
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='mgarrett12',
    maintainer_email='mgarrett12@cub.uca.edu',
    description='SLAM mapping and Nav2 autonomous navigation package for BabyWonk',
    license='GPL-3.0-only',
    extras_require={'test': ['pytest']},
    entry_points={
        'console_scripts': [
            'navigator = babywonk_navigation.navigator:main',
        ],
    },
)
