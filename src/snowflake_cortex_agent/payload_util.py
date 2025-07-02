import json
from pathlib import Path
from typing import Any, Tuple

from jinja2 import Environment, FileSystemLoader


class PayloadUtil:
    """Utility class to verify the agent_run.json.j2 template"""

    def __init__(self, template_dir: str):
        """Initialize the template verifier"""
        self.template_dir = Path(template_dir)
        self.env = Environment(
            autoescape=True,
            loader=FileSystemLoader(template_dir),
            variable_start_string="<%",
            variable_end_string="%>",
        )

    def load_template(self):
        """Load the agent_run.json.j2 template"""
        try:
            return self.env.get_template("agent_run.json.j2")
        except Exception as e:
            raise ValueError(f"Error loading template: {e}") from e

    def render_template(self, **kwargs) -> str | None:
        """Render the template with provided parameters"""
        template = self.load_template()
        if not template:
            return None

        try:
            rendered = template.render(**kwargs)
            return rendered
        except Exception as e:
            raise ValueError(f"Error rendering template: {e}") from e

    def validate_json(self, json_string: str) -> Tuple[bool, Any]:
        """Validate that the rendered template is valid JSON"""
        try:
            parsed = json.loads(json_string)
            return True, parsed
        except json.JSONDecodeError as e:
            raise e
