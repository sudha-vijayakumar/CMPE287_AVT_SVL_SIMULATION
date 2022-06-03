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

customSpawn = lgsvl.Transform(lgsvl.Vector(18,-2.5,-29))


# school bus, 20m ahead, perpendicular to road, stopped
state = lgsvl.AgentState()
forward = lgsvl.utils.transform_to_forward(spawns[0])
state.transform.position = customSpawn.position
bus = sim.add_agent("Jeep", lgsvl.AgentType.NPC, state)

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

sim.run()

