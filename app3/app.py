from jinja2 import Environment, FileSystemLoader, select_autoescape
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

env = Environment(
    loader=FileSystemLoader(os.path.join(BASE_DIR, "templates")),
    autoescape=select_autoescape(["html", "xml"])
)


def app(environ, start_response):
    path = environ.get("PATH_INFO", "/")

    students = [
        {"ID": 1, "Name": "Alice Johnson", "Course": "Computer Science"},
        {"ID": 2, "Name": "Brian Smith", "Course": "Information Technology"},
        {"ID": 3, "Name": "Catherine Lee", "Course": "Business Administration"},
        {"ID": 4, "Name": "David Brown", "Course": "Mechanical Engineering"},
        {"ID": 5, "Name": "Emma Wilson", "Course": "Psychology"},
        {"ID": 6, "Name": "Frank Garcia", "Course": "Electrical Engineering"},
        {"ID": 7, "Name": "Grace Martinez", "Course": "Marketing"},
        {"ID": 8, "Name": "Henry Anderson", "Course": "Civil Engineering"},
        {"ID": 9, "Name": "Isabella Thomas", "Course": "Biology"},
        {"ID": 10, "Name": "James Taylor", "Course": "Accounting"}
    ]

    if path.endswith("/students"):
        title = "Students List"
        message = "Dynamic Table with Jinja2"
    else:
        title = "Home"
        message = "Plain Python + Gunicorn + Jinja2"

    template = env.get_template("home.html")
    html = template.render(title=title, message=message, students=students)

    start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
    return [html.encode("utf-8")]
