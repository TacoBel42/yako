import yaml
from yako.scenario import Scenario, RunnableModule

def name_nodes(nodes: dict):
    for name, node in nodes.items():
        node['name'] = name

def parse_modules(m):
    modules = {}
    for name, path in m.items():
        modules[name] = RunnableModule(name, path)
    return modules

def parse_scenario(path: str):
    with open(path, 'r') as f:
        f = yaml.safe_load(f)
        s = f['scenario']
        name_nodes(s['nodes'])
        
        modules = {}
        if m := f.get('modules'):
            modules = parse_modules(m)
        scenario = Scenario(
            name=s['name'], 
            run_condition=s['run_condition'],
            nodes=s['nodes'], 
            desc=s.get('desc'),
            scenario_modules=modules
        )
        return scenario
