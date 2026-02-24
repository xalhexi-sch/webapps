# ~/webapps/app4/app.py
import os
from datetime import datetime

from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import NotFound
from jinja2 import Environment, FileSystemLoader, select_autoescape

# ------------------------
# Paths + config
# ------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# Allow override via env, else use username like school
BASE_URL = os.environ.get("BASE_URL") or f"/it21_{os.environ.get('USER', 'user')}/webapps/app4"

env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(["html", "xml"])
)

def url(path: str = "/") -> str:
    """Build URLs that always include BASE_URL prefix."""
    if not path.startswith("/"):
        path = "/" + path
    # Special case: '/' should become BASE_URL + '/'
    if path == "/":
        return BASE_URL + "/"
    return BASE_URL + path

def render(template, **context):
    context.update({
        "base_url": BASE_URL,
        "url": url,
    })
    return Response(env.get_template(template).render(**context), content_type="text/html")

# ------------------------
# Fake "DB" (later you can replace with real DB / Django)
# ------------------------
PRODUCTS = [
    {"id": 1, "name": "Gaming Laptop", "brand": "Dell", "price": 1500, "stock": 10, "tag": "Best Seller"},
    {"id": 2, "name": "Mechanical Keyboard", "brand": "Logitech", "price": 120, "stock": 25, "tag": "New"},
    {"id": 3, "name": "Noise-Cancel Headset", "brand": "Sony", "price": 280, "stock": 6, "tag": "Hot"},
    {"id": 4, "name": "USB-C Hub", "brand": "Anker", "price": 45, "stock": 40, "tag": "Value"},
]

def get_product(pid: int):
    for p in PRODUCTS:
        if p["id"] == pid:
            return p
    return None

# ------------------------
# Routes
# ------------------------
url_map = Map([
    Rule("/", endpoint="home"),
    Rule("/products", endpoint="products"),
    Rule("/products/<int:pid>", endpoint="product_detail"),
    Rule("/services", endpoint="services"),
    Rule("/contactus", endpoint="contactus", methods=["GET", "POST"]),
])

# ------------------------
# View functions
# ------------------------
def home(request):
    return render("home.html", active="home")

def products(request):
    q = (request.args.get("q") or "").strip()
    items = PRODUCTS
    if q:
        q_low = q.lower()
        items = [p for p in PRODUCTS if q_low in p["name"].lower() or q_low in p["brand"].lower()]
    return render("products.html", active="products", product_items=items, q=q)

def product_detail(request, pid):
    product = get_product(pid)
    if not product:
        return render("404.html", active="", message="Product not found.", path=request.path), 404
    return render("product_detail.html", active="products", product=product)

def services(request):
    services_list = [
        {"title": "Laptop Cleaning + Thermal Repaste", "desc": "Boost performance & reduce overheating.", "price": "₱499"},
        {"title": "PC Build Consultation", "desc": "Parts advice + compatibility check.", "price": "₱199"},
        {"title": "Basic Troubleshooting", "desc": "Fix common driver/software issues.", "price": "₱299"},
    ]
    return render("services.html", active="services", services=services_list)

def contactus(request):
    sent = request.args.get("sent") == "1"
    errors = {}
    values = {"name": "", "email": "", "message": ""}

    if request.method == "POST":
        values["name"] = (request.form.get("name") or "").strip()
        values["email"] = (request.form.get("email") or "").strip()
        values["message"] = (request.form.get("message") or "").strip()

        if len(values["name"]) < 2:
            errors["name"] = "Please enter your name."
        if "@" not in values["email"]:
            errors["email"] = "Please enter a valid email."
        if len(values["message"]) < 5:
            errors["message"] = "Message is too short."

        if not errors:
            # Save to a simple log file (you can switch to DB later)
            log_path = os.path.join(os.path.expanduser("~"), "contact_messages.log")
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"[{datetime.now().isoformat(timespec='seconds')}] {values['name']} <{values['email']}>: {values['message']}\n")

            # Redirect (prevents form resubmission)
            return Response("", status=302, headers={"Location": url("/contactus?sent=1")})

    return render("contactus.html", active="contactus", sent=sent, errors=errors, values=values)

# ------------------------
# WSGI app
# ------------------------
@Request.application
def app(request):
    adapter = url_map.bind_to_environ(request.environ)

    try:
        endpoint, values = adapter.match()
        result = globals()[endpoint](request, **values)

        # allow (Response, status) returns
        if isinstance(result, tuple) and len(result) == 2:
            resp, status = result
            if isinstance(resp, Response):
                resp.status_code = status
                return resp
        return result

    except NotFound:
        return Response(render("404.html", active="", message="Page not found.", path=request.path).get_data(),
                        status=404,
                        content_type="text/html")