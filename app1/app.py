from jinja2 import Environment, FileSystemLoader
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

env = Environment(
    loader=FileSystemLoader(os.path.join(BASE_DIR, "templates")),
    autoescape=True
)

def app(environ, start_response):
    path = environ.get("PATH_INFO", "/")

    if path.endswith("/hello"):
        title = "Hello Page"
        message = "Rendered using Jinja2"
    else:
        title = "Home"
        message = "Plain Python + Gunicorn + Nginx"

    template = env.get_template("home.html")
    html = template.render(title=title, message=message)

    start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
    return [html.encode("utf-8")]
