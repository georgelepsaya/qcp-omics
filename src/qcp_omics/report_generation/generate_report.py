from jinja2 import Environment, FileSystemLoader
import os
from typing import Any, Dict, List

def generate_html_report(report_data: List[Dict], metadata: Dict[str, Any], output_dir: str) -> None:
    """
    Generate an HTML report using Jinja2 templates.

    Args:
        report_data (Dict[str, Any]): A dictionary containing the data to be displayed in the report.
        metadata (Dict[str, Any]): A dictionary containing metadata for the report (e.g., title, author).
        output_dir (str): The directory where the generated HTML report will be saved.

    Raises:
        ValueError: If the specified output directory is not valid.
    """
    # Get the absolute path of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to the templates directory
    templates_dir = os.path.join(script_dir, "templates")

    # Ensure the output directory is valid
    if not os.path.isdir(output_dir):
        raise ValueError(f"The specified output path '{output_dir}' is not a valid directory.")

    # Initialize the Jinja2 environment with the templates directory
    env = Environment(loader=FileSystemLoader(templates_dir))

    # Load the specified template
    try:
        template = env.get_template("report_template.jinja")
    except Exception as e:
        raise RuntimeError(f"Failed to load template: {e}")

    # Render the HTML content using the provided data and metadata
    html_content = template.render(data=report_data, metadata=metadata)

    # Construct the output file path
    output_file_path = os.path.join(output_dir, "report.html")

    # Write the rendered HTML content to the output file
    try:
        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write(html_content)
    except Exception as e:
        raise IOError(f"Failed to write report to '{output_file_path}': {e}")

    print(f"Report successfully generated at: {output_file_path}")
