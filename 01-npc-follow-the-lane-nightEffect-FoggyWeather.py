#!/usr/bin/env python3
#
# Copyright (c) 2019-2021 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

import os
import lgsvl
from environs import Env

env = Env()
SIMULATOR_HOST = os.environ.get("SIMULATOR_HOST", "127.0.0.1")
SIMULATOR_PORT = int(os.environ.get("SIMULATOR_PORT", 8181))
BRIDGE_HOST = os.environ.get("BRIDGE_HOST", "127.0.0.1")
BRIDGE_PORT = int(os.environ.get("BRIDGE_PORT", 9090))

sim = lgsvl.Simulator(SIMULATOR_HOST, SIMULATOR_PORT)
if sim.current_scene == "BorregasAve":
    sim.reset()
else:
    sim.load("BorregasAve")

spawns = sim.get_spawn()

state = lgsvl.AgentState()
state.transform = spawns[0]
ego = sim.add_agent(env.str("LGSVL__VEHICLE_0", "2e9095fa-c9b9-4f3f-8d7d-65fa2bb03921"), lgsvl.AgentType.EGO, state)
ego.connect_bridge(BRIDGE_HOST, BRIDGE_PORT)

state = lgsvl.AgentState()

forward = lgsvl.utils.transform_to_forward(spawns[0])
right = lgsvl.utils.transform_to_right(spawns[0])

# Time of day can be set from 0 ... 24
sim.set_time_of_day(19.0)
sim.weather = lgsvl.WeatherState(rain=0, fog=0.9, wetness=0, cloudiness=0.4, damage=0)

# 10 meters ahead, on left lane
state.transform.position = spawns[0].position + 10.0 * forward
state.transform.rotation = spawns[0].rotation

npc1 = sim.add_agent("Sedan", lgsvl.AgentType.NPC, state)

state = lgsvl.AgentState()

# 10 meters ahead, on right lane
state.transform.position = spawns[0].position + 4.0 * right + 10.0 * forward
state.transform.rotation = spawns[0].rotation

npc2 = sim.add_agent("SUV", lgsvl.AgentType.NPC, state, lgsvl.Vector(1, 1, 0))

# If the passed bool is False, then the NPC will not moved
# The float passed is the maximum speed the NPC will drive
# 11.1 m/s is ~40 km/h
npc1.follow_closest_lane(True, 11.1)

# 5.6 m/s is ~20 km/h
npc2.follow_closest_lane(True, 5.6)

input("Press Enter to run the simulation for 40 seconds")


# Dreamview setup
dv = lgsvl.dreamview.Connection(sim, ego, BRIDGE_HOST)
dv.set_hd_map('Borregas Ave')
dv.set_vehicle('Lincoln2017MKZ LGSVL')
modules = [
    'Localization',
    'Transform',
    'Routing',
    'Prediction',
    'Planning',
    'Control'
]
destination = spawns[0].destinations[0]
dv.setup_apollo(destination.position.x, destination.position.z, modules)

sim.run(40)
