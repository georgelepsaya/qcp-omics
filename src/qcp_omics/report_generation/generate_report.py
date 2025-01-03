from jinja2 import Environment, FileSystemLoader
import os


def generate_html_report(report_data, metadata, output_dir):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(script_dir, "templates")

    if not os.path.isdir(output_dir):
        raise ValueError(f"The specified output path '{output_dir}' is not a valid directory.")

    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template("report_template.jinja")

    html_content = template.render(data=report_data, metadata=metadata)

    output_file_path = os.path.join(output_dir, "report.html")

    with open(output_file_path, "w") as f:
        f.write(html_content)

    print(f"Report successfully generated at: {output_file_path}")
