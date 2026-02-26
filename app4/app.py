from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import NotFound
from jinja2 import Environment, FileSystemLoader

# ------------------------
# Basic setup
# ------------------------
BASE_URL = "/it21_banas/webapps/app4"

env = Environment(loader=FileSystemLoader("templates"))

def render(template, **context):
    context.update({
        "base_url": BASE_URL,
    })
    return Response(
        env.get_template(template).render(**context),
        content_type="text/html"
    )

# ------------------------
# Routes
# ------------------------
url_map = Map([
    Rule("/", endpoint="home"),
    Rule("/products", endpoint="products"),
    Rule("/services", endpoint="services"),
    Rule("/contactus", endpoint="contactus"),
    Rule("/register", endpoint="register", methods=["GET", "POST"]),  # NEW ROUTE
])

# ------------------------
# View functions
# ------------------------
def home(request):
    return render("home.html")

def products(request):
    product_items = [
        {"id": 1, "name": "Gaming Laptop", "brand": "Dell", "price": 1500, "stock": 10},
        {"id": 2, "name": "Mechanical Keyboard", "brand": "Logitech", "price": 120, "stock": 25},
    ]
    return render("products.html", product_items=product_items)

def services(request):
    return render("services.html")

def contactus(request):
    return render("contactus.html")

def register(request):
    error = None
    success = None

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        if not email or not password:
            error = "All fields are required."
        else:
            success = f"Welcome, {email}! You are registered."

    return render("register.html", error=error, success=success)

# ------------------------
# WSGI app
# ------------------------
@Request.application
def app(request):
    adapter = url_map.bind_to_environ(request.environ)

    try:
        endpoint, values = adapter.match()
        return globals()[endpoint](request, **values)
    except NotFound:
        return Response("404 Not Found", status=404)