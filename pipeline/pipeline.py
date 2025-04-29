from typing import List

class PipelineStep:
    def __init__(self, name):
        self.name = name

    def compute(self, data):
        raise NotImplementedError()

class DscimPipeline:
    def __init__(self, steps: List[PipelineStep]):
        self.steps = steps

    def compute(self, initial_data=None):
        data = initial_data
        for step in self.steps:
            data = step.compute(data)
        return data

    def visualize(self):
        from graphviz import Digraph
        dot = Digraph()
        for i, step in enumerate(self.steps):
            dot.node(str(i), f"{step.name}\n{step.__class__.__name__}")
            if i > 0:
                dot.edge(str(i - 1), str(i))
        return dot