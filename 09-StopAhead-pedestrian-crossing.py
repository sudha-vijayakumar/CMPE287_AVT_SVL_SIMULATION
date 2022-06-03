#!/usr/bin/env python3
#
# Copyright (c) 2019-2021 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#

from environs import Env
import lgsvl
import os
env = Env()
SIMULATOR_HOST = os.environ.get("LGSVL__SIMULATOR_HOST", "127.0.0.1")
SIMULATOR_PORT = int(os.environ.get("LGSVL__SIMULATOR_PORT", 8181))
BRIDGE_HOST = os.environ.get("BRIDGE_HOST", "127.0.0.1")
BRIDGE_PORT = int(os.environ.get("BRIDGE_PORT", 9090))
sim = lgsvl.Simulator(env.str("LGSVL__SIMULATOR_HOST", lgsvl.wise.SimulatorSettings.simulator_host), env.int("LGSVL__SIMULATOR_PORT", lgsvl.wise.SimulatorSettings.simulator_port))
if sim.current_scene == lgsvl.wise.DefaultAssets.map_borregasave:
    sim.reset()
else:
    sim.load(lgsvl.wise.DefaultAssets.map_borregasave, 42)

spawns = sim.get_spawn()
layer_mask = 0
layer_mask |= 1 << 0  # 0 is the layer for the road (default)

# EGO
state = lgsvl.AgentState()
ego_position = lgsvl.Vector(342.0, 0.0, -87.7)
hit = sim.raycast(ego_position, lgsvl.Vector(0, -1, 0), layer_mask)
state.transform.position = hit.point
state.transform.rotation = lgsvl.Vector(0.0, 15.0, 0.0)
forward = lgsvl.Vector(0.2, 0.0, 0.8)
state.velocity = forward * 15
ego = sim.add_agent(env.str("LGSVL__VEHICLE_0", "2e9095fa-c9b9-4f3f-8d7d-65fa2bb03921"), lgsvl.AgentType.EGO, state)
ego.connect_bridge(BRIDGE_HOST, BRIDGE_PORT)
# Pedestrian
state = lgsvl.AgentState()
pedestrian_position = lgsvl.Vector(350.0, 0.0, -12)
hit = sim.raycast(pedestrian_position, lgsvl.Vector(0, -1, 0), layer_mask)
pedestrian_rotation = lgsvl.Vector(0.0, 105.0, 0.0)
state.transform.position = hit.point
state.transform.rotation = pedestrian_rotation
pedestrian = sim.add_agent("Bob", lgsvl.AgentType.PEDESTRIAN, state)

state = lgsvl.AgentState()
pedestrian1_position = lgsvl.Vector(370.0, 0.0, -12)
hit = sim.raycast(pedestrian1_position, lgsvl.Vector(0, -1, 0), layer_mask)
pedestrian1_rotation = lgsvl.Vector(0.0, 105.0, 0.0)
state.transform.position = hit.point
state.transform.rotation = pedestrian1_rotation
pedestrian1 = sim.add_agent("Zoe", lgsvl.AgentType.PEDESTRIAN, state)

agents = {ego: "EGO", pedestrian: "Bob", pedestrian1: "Zoe"}


# Executed upon receiving collision callback -- pedestrian is expected to walk into colliding objects
def on_collision(agent1, agent2, contact):
    name1 = agents[agent1]
    name2 = agents[agent2] if agent2 is not None else "OBSTACLE"
    print("{} collided with {}".format(name1, name2))


ego.on_collision(on_collision)
pedestrian.on_collision(on_collision)
pedestrian1.on_collision(on_collision)
# This block creates the list of waypoints that the pedestrian will follow
# Each waypoint is an position vector paired with the speed that the pedestrian will walk to
waypoints = []

trigger = None
speed = 3
hit = sim.raycast(
    pedestrian_position + lgsvl.Vector(7.4, 0.0, -2.2),
    lgsvl.Vector(0, -1, 0),
    layer_mask,
)
effector = lgsvl.TriggerEffector("TimeToCollision", {})
trigger = lgsvl.WaypointTrigger([effector])
wp = lgsvl.WalkWaypoint(
    position=hit.point, speed=speed, idle=0, trigger_distance=0, trigger=trigger
)
waypoints.append(wp)

hit = sim.raycast(
    pedestrian_position + lgsvl.Vector(12.4, 0.0, -3.4),
    lgsvl.Vector(0, -1, 0),
    layer_mask,
)
wp = lgsvl.WalkWaypoint(
    position=hit.point, speed=speed, idle=0, trigger_distance=0, trigger=None
)
waypoints.append(wp)


def on_waypoint(agent, index):
    print("waypoint {} reached".format(index))


def agents_traversed_waypoints():
    print("All agents traversed their waypoints.")
    sim.stop()


# The above function needs to be added to the list of callbacks for the pedestrian
pedestrian.on_waypoint_reached(on_waypoint)
pedestrian1.on_waypoint_reached(on_waypoint)
sim.agents_traversed_waypoints(agents_traversed_waypoints)

# The pedestrian needs to be given the list of waypoints. A bool can be passed as the 2nd argument that controls
# whether or not the pedestrian loops over the waypoints (default false)
pedestrian.follow(waypoints, False)

input("Press Enter to run")

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
sim.run(20)
