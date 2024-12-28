from jinja2 import Environment, FileSystemLoader
import os


def generate_html_report(report_data, metadata, output_path="report.html"):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(script_dir, "templates")

    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template("report_template.jinja")

    html_content = template.render(data=report_data, metadata=metadata)
    with open(output_path, "w") as f:
        f.write(html_content)
