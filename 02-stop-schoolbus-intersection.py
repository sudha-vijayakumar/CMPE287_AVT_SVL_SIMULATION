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
forward = lgsvl.utils.transform_to_forward(spawns[0])
right = lgsvl.utils.transform_to_right(spawns[0])

# ego vehicle
state = lgsvl.AgentState()
state.transform = spawns[0]
state.velocity = 6 * forward
ego = sim.add_agent(env.str("LGSVL__VEHICLE_0", "2e9095fa-c9b9-4f3f-8d7d-65fa2bb03921"), lgsvl.AgentType.EGO, state)
ego.connect_bridge(BRIDGE_HOST, BRIDGE_PORT)

# school bus, 20m ahead, perpendicular to road, stopped
state = lgsvl.AgentState()
state.transform.position = spawns[0].position + 30.0 * forward
state.transform.rotation.y = spawns[0].rotation.y + 90.0
bus = sim.add_agent("SchoolBus", lgsvl.AgentType.NPC, state)

# sedan, 10m ahead, driving forward
state = lgsvl.AgentState()
state.transform.position = spawns[0].position + 10.0 * forward
state.transform.rotation = spawns[0].rotation
sedan = sim.add_agent("Sedan", lgsvl.AgentType.NPC, state)
# Even though the sedan is commanded to follow the lane, obstacle avoidance takes precedence and it will not drive into the bus
sedan.follow_closest_lane(True, 11.1)  # 11.1 m/s is ~40 km/h

vehicles = {
    ego: "EGO",
    bus: "SchoolBus",
    sedan: "Sedan",
}


# This function gets called whenever any of the 3 vehicles above collides with anything
def on_collision(agent1, agent2, contact):
    name1 = vehicles[agent1]
    name2 = vehicles[agent2] if agent2 is not None else "OBSTACLE"
    print("{} collided with {} at {}".format(name1, name2, contact))


# The above on_collision function needs to be added to the callback list of each vehicle
ego.on_collision(on_collision)
bus.on_collision(on_collision)
sedan.on_collision(on_collision)
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

input("Press Enter to run the simulation for 10 seconds")

# Drive into the sedan, bus, or obstacle to get a callback
sim.run(10)
