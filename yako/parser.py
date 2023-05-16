import yaml
from yako.scenario import Scenario 

def name_nodes(nodes: dict):
    for name, node in nodes.items():
        node['name'] = name

def parse_scenario(path: str):
    with open(path, 'r') as f:
        s = yaml.safe_load(f)
        s = s['scenario']
        name_nodes(s['nodes'])
        scenario = Scenario(name=s['name'], run_condition=s['run_condition'], nodes=s['nodes'])
        return scenario
