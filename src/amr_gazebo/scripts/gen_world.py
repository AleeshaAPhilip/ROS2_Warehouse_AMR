#!/usr/bin/env python3
"""Generate worlds/warehouse.sdf. Run once, commit the output."""
import os

models = []

def box(name, x, y, z, sx, sy, sz, rgb, collide=True):
    col = (f'<collision name="c"><geometry><box><size>{sx} {sy} {sz}</size></box></geometry></collision>'
           if collide else '')
    models.append(f'''
    <model name="{name}"><static>true</static><pose>{x} {y} {z} 0 0 0</pose>
      <link name="l">{col}
        <visual name="v"><geometry><box><size>{sx} {sy} {sz}</size></box></geometry>
          <material><ambient>{rgb} 1</ambient><diffuse>{rgb} 1</diffuse></material></visual>
      </link></model>''')

GREY, ORANGE, BLUE = '0.6 0.6 0.62', '0.85 0.5 0.1', '0.2 0.4 0.75'

# room: x in [-8, 8], y in [-6, 6], walls 2 m high
box('wall_n', 0,  6.1, 1.0, 16.4, 0.2, 2.0, GREY)
box('wall_s', 0, -6.1, 1.0, 16.4, 0.2, 2.0, GREY)
box('wall_e',  8.1, 0, 1.0, 0.2, 12.0, 2.0, GREY)
box('wall_w', -8.1, 0, 1.0, 0.2, 12.0, 2.0, GREY)

# 4 rows x 4 shelves (2.0 x 0.6 x 1.8 m) -> aisles about 1.4 m wide
for r, y in enumerate([3.6, 1.6, -1.6, -3.6]):
    for i, x in enumerate([-1.0, 1.0, 3.0, 5.0]):
        box(f'shelf_{r}_{i}', x, y, 0.9, 2.0, 0.6, 1.8, ORANGE if (r + i) % 2 else BLUE)

# pillars (extra features help SLAM)
box('pillar_n', -3.5,  3.0, 1.0, 0.4, 0.4, 2.0, GREY)
box('pillar_s', -3.5, -3.0, 1.0, 0.4, 0.4, 2.0, GREY)

# HOME pad (robot spawns here) and charging station (visual pads + solid charger post)
box('home_pad',   -6.0,  0.0, 0.005, 1.0, 1.0, 0.01, '0.1 0.7 0.2', collide=False)
box('charge_pad', -6.0, -4.5, 0.005, 1.0, 1.0, 0.01, '0.9 0.8 0.1', collide=False)
box('charger',    -7.6, -4.5, 0.40,  0.4, 0.6, 0.8,  '0.3 0.3 0.3')

sdf = f'''<?xml version="1.0"?>
<sdf version="1.9">
  <world name="warehouse">
    <physics name="1ms" type="ode"><max_step_size>0.001</max_step_size><real_time_factor>1.0</real_time_factor></physics>
    <plugin filename="gz-sim-physics-system" name="gz::sim::systems::Physics"/>
    <plugin filename="gz-sim-user-commands-system" name="gz::sim::systems::UserCommands"/>
    <plugin filename="gz-sim-scene-broadcaster-system" name="gz::sim::systems::SceneBroadcaster"/>
    <plugin filename="gz-sim-sensors-system" name="gz::sim::systems::Sensors">
      <render_engine>ogre2</render_engine>
    </plugin>
    <plugin filename="gz-sim-imu-system" name="gz::sim::systems::Imu"/>

    <scene><ambient>0.5 0.5 0.5 1</ambient><background>0.7 0.8 0.9 1</background></scene>
    <light type="directional" name="sun">
      <cast_shadows>true</cast_shadows><pose>0 0 10 0 0 0</pose>
      <diffuse>0.9 0.9 0.9 1</diffuse><direction>-0.5 0.1 -0.9</direction>
    </light>

    <model name="ground"><static>true</static><link name="l">
      <collision name="c"><geometry><plane><normal>0 0 1</normal><size>40 40</size></plane></geometry></collision>
      <visual name="v"><geometry><plane><normal>0 0 1</normal><size>40 40</size></plane></geometry>
        <material><ambient>0.75 0.75 0.75 1</ambient><diffuse>0.75 0.75 0.75 1</diffuse></material></visual>
    </link></model>
{''.join(models)}
  </world>
</sdf>
'''

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'worlds', 'warehouse.sdf')
os.makedirs(os.path.dirname(out), exist_ok=True)
open(out, 'w').write(sdf)
print('wrote', os.path.normpath(out))
