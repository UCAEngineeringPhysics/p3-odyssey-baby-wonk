from setuptools import setup

package_name = 'wonklet'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Lillian Slaton',
    maintainer_email='lslaton@cub.uca.edu',
    description='Autonomous navigation node for HomeR robot - The Odyssey project',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'navigate = wonklet.navigate:main',
        ],
    },
)