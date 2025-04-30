# dscim/pipeline/pipeline.py
from typing import List
from IPython.display import display, HTML, Javascript
import uuid
import json

class PipelineStep:
    def __init__(self, name: str):
        self.name = name

    def compute(self, data: dict = None) -> dict:
        # Initialize inputs for first step
        inputs = data or {}
        outputs = self.process(inputs)
        if not isinstance(outputs, dict):
            raise TypeError(f"Step '{self.name}' must return a dict from process().")
        return outputs

    def process(self, inputs: dict) -> dict:
        raise NotImplementedError("Each step must implement process(inputs) -> dict.")

    def get_metadata(self) -> dict:
        """
        Return static metadata for each step (used in visualization).
        """
        return {
            "name": self.name,
            "class": self.__class__.__name__,
        }

    def describe_output(self) -> dict:
        """
        Describe the expected output dimensions for each step.
        Override in subclasses if dims are known ahead of time.
        """
        return {}

class DscimPipeline:
    def __init__(self, steps: List[PipelineStep]):
        self.steps = steps
        self.shape_trace = []

        # Prepopulate shape_trace with static metadata + expected outputs
        for step in self.steps:
            self.shape_trace.append({
                "step": step.name,
                "dims": step.describe_output(),
                "meta": step.get_metadata()
            })

    def compute(self, initial_data=None):
        data = initial_data
        for i, step in enumerate(self.steps):
            try:
                data = step.compute(data)
                self.shape_trace[i]["status"] = "success"
            except Exception as e:
                self.shape_trace[i]["status"] = "error"
                self.shape_trace[i]["error_msg"] = str(e)
                raise e  # Optional: halt or continue
            dims = {}
            if isinstance(data, dict):
                for k, v in data.items():
                    if hasattr(v, "dims"):
                        dims[k] = dict(v.sizes)
            self.shape_trace[i]["dims"] = dims
        return data

    def visualize(self):
        from graphviz import Digraph
        dot = Digraph()
        for i, step in enumerate(self.steps):
            label = f"{step.name}\n{step.__class__.__name__}"
            dot.node(str(i), label)
            if i > 0:
                dot.edge(str(i - 1), str(i))
        return dot

    def visualize_html(self):
        html = "<div style='font-family:monospace'><h3>DSCIM Pipeline</h3><ol>"
        for i, trace in enumerate(self.shape_trace):
            meta = trace.get("meta", {})
            html += f"<li><b>{meta.get('name')}</b> <i>({meta.get('class')})</i><ul>"
            for k, v in meta.items():
                if k not in ("name", "class") and v is not None:
                    html += f"<li><code>{k}</code>: {v}</li>"
            dims = trace.get("dims", {})
            if dims:
                html += "<li><b>Output dimensions:</b><ul>"
                for k, shape in dims.items():
                    html += f"<li>{k}: {shape}</li>"
                html += "</ul></li>"
            else:
                html += "<li><i><small>Output dimensions not yet available</small></i></li>"
            html += "</ul></li>"
        html += "</ol></div>"
        display(HTML(html))

    
    def visualize_interactive(self):
        uid = uuid.uuid4().hex
        div_id = f"cy-{uid}"
        info_id = f"info-{uid}"

        nodes = []
        edges = []

        for i, trace in enumerate(self.shape_trace):
            meta = trace.get("meta", {})
            dims = trace.get("dims", {})

            # Extract and format details
            details = f"<b>Step:</b> {meta.get('name')}<br><b>Class:</b> {meta.get('class')}<br>"
            for k, v in meta.items():
                if k not in ("name", "class") and v is not None:
                    details += f"<code>{k}</code>: {v}<br>"
            if dims:
                details += "<b>Output dimensions:</b><ul>"
                for dk, dv in dims.items():
                    details += f"<li>{dk}: {dv}</li>"
                details += "</ul>"
            else:
                details += "<i>Output dimensions not yet available</i>"

            # Determine node color based on status
            status = trace.get("status", "pending")
            color = {
                "success": "#20e827",
                "error": "#f8d7da",
                "pending": "#f0f0f0"
            }[status]

            nodes.append({
                "data": {
                    "id": str(i),
                    "label": f"{meta.get('name')} ({meta.get('class')})",
                    "details": details
                },
                "style": {
                    "background-color": color
                }
            })

            if i > 0:
                edges.append({
                    "data": {
                        "source": str(i - 1),
                        "target": str(i)
                    }
                })

        return HTML(f"""
        <div style="font-family: sans-serif;">
        <h3>DSCIM Pipeline</h3>
        <div id="{div_id}" style="width:100%; height:300px; border:1px solid #ccc; margin-bottom:12px;"></div>
        <div id="{info_id}" style="padding:12px; border:1px solid #ddd; background:#f9f9f9; font-family:monospace;">
            <i>Click a node to view details</i>
        </div>
        </div>
        <script src="https://unpkg.com/cytoscape/dist/cytoscape.min.js"></script>
        <script>
        (function() {{
        var cy = cytoscape({{
            container: document.getElementById('{div_id}'),
            elements: {{
                nodes: {json.dumps(nodes)},
                edges: {json.dumps(edges)}
            }},
            style: [
                {{
                    selector: 'node',
                    style: {{
                        'content': 'data(label)',
                        'shape': 'roundrectangle',
                        'text-valign': 'center',
                        'text-halign': 'center',
                        'font-size': '13px',
                        'padding': '10px',
                        'text-wrap': 'wrap',
                        'width': 'label',
                        'height': 'label'
                    }}
                }},
                {{
                    selector: 'edge',
                    style: {{
                        'width': 2,
                        'line-color': '#888',
                        'target-arrow-shape': 'triangle',
                        'target-arrow-color': '#888',
                        'curve-style': 'bezier'
                    }}
                }}
            ],
            layout: {{
                name: 'grid',
                rows: 1,
                spacingFactor: 1.4,
                padding: 10
            }}
        }});

        cy.on('tap', 'node', function(evt) {{
            document.getElementById('{info_id}').innerHTML = evt.target.data('details');
        }});
        }})();
        </script>
        """)
