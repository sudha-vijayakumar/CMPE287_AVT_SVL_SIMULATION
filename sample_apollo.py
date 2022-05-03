import lgsvl
from environs import Env
import json
import time
import os
import datetime

#fetch env varables if not set it equal to this value. 
env = Env()
LGSVL__SIMULATOR_HOST = env.str("LGSVL__SIMULATOR_HOST", "127.0.0.1")
LGSVL__SIMULATOR_PORT = env.int("LGSVL__SIMULATOR_PORT", 8181)
LGSVL__AUTOPILOT_0_HOST = env.str("LGSVL__AUTOPILOT_0_HOST", "127.0.0.1")
LGSVL__AUTOPILOT_0_PORT = env.int("LGSVL__AUTOPILOT_0_PORT", 9090)

#initializing the simulator obs
sim = lgsvl.Simulator("127.0.0.1", LGSVL__SIMULATOR_PORT)

#load the borregas ave if it is loaded reset it
if sim.current_scene == "BorregasAve":
    sim.reset()
else:
    sim.load("BorregasAve", seed=100)

#get the spawn points for hte map
spawns = sim.get_spawn()

#lgsvl.Transform(lgsvl.Vector(agent["transform"]["position"]["x"],agent["transform"]["position"]["y"],agent["transform"]["position"]["z"]),
#            lgsvl.Vector(agent["transform"]["rotation"]["x"],agent["transform"]["rotation"]["y"],agent["transform"]["rotation"]["z"])
custom_destination = lgsvl.Transform(lgsvl.Vector(x, y, z))

#take the first spawn point and first destination.
#these are the ones that work. changes may not work
destination = spawns[0].destinations[0]
state = lgsvl.AgentState()
state.transform = spawns[0]






for i in range(5):
    # add self driving car, from car, Apollo 6.0 (modular testing)
    ego = sim.add_agent("2e9095fa-c9b9-4f3f-8d7d-65fa2bb03921", lgsvl.AgentType.EGO, state)

    # add connect to the apollo
    ego.connect_bridge(LGSVL__AUTOPILOT_0_HOST, LGSVL__AUTOPILOT_0_PORT)
    dv = lgsvl.dreamview.Connection(sim, ego, LGSVL__AUTOPILOT_0_HOST)

    #can use to avoid setting in the dreamview UI
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
    dv.setup_apollo(destination.position.z, destination.position.y, modules)

    #set the destination programmatic 
    dv.set_destination(destination.position.x, destination.position.z, destination.position.y)
    sim.run(10)

    sim.reset()
