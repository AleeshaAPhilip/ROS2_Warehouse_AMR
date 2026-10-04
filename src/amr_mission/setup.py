import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'amr_mission'

setup(
    name=package_name,
    version='1.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='aleesha',
    maintainer_email='aleeshaaphilip2004@gmail.com',
    description='Mission executor and dynamic obstacle for the warehouse AMR',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'mission_executor = amr_mission.mission_executor:main',
            'dynamic_obstacle = amr_mission.dynamic_obstacle:main',
        ],
    },
)
