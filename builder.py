from jinja2 import Environment, FileSystemLoader

def build_condition_re(question: str):
    question = question.lower()
    reg = question.replace('*', '[а-яА-я]*').replace('?', '[а-яА-я]?')
    return f"bool(re.compile('{reg}').match(message.text.lower()))"

def build_new_scenario(name: str, desc: str, question: str, answer: str) -> str:
    environment = Environment(loader=FileSystemLoader('templates/'))
    template = environment.get_template('simple.template.yml')
    scenario = template.render(name=name, desc=desc, condition=build_condition_re(question), answer=answer)
    with open("example_scenarios/" + name + "_auto" + ".yml", "w") as f:
        f.write(scenario)
    return "example_scenarios/" +  name + "_auto" + ".yml"