from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import NotFound
import sqlite3




from jinja2 import Environment, FileSystemLoader


# ------------------------
# Basic setup
# ------------------------


BASE_URL = "/it21_banas/webapps/app5"


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
    Rule("/register", endpoint="register",methods=["GET", "POST"]),
])


# ------------------------
# View functions
# ------------------------
def home(request):


    return render("home.html")


def register(request):
    error = None
    success = None


    if request.method == "POST":
        email = request.form.get("email").strip()
        password    = request.form.get("password").strip()
   


        if not email :
            error = "All fields are required."
        else:          
            success = f"Welcome, {email}! You are registered."


    return render("register.html", error=error, success=success)


def products(request):

    conn = sqlite3.connect("products.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, brand, price, stock FROM products")
    rows = cursor.fetchall()

    conn.close()

    product_items = []

    for row in rows:
        product_items.append({
            "id": row[0],
            "name": row[1],
            "brand": row[2],
            "price": row[3],
            "stock": row[4]
        })

    return render("products.html", product_items=product_items)
    
    
    product_items = [
        {
            "id": 1,
            "name": "Gaming Laptop",
            "brand": "Dell",
            "price": 1500,
            "stock": 10
        },
        {
            "id": 2,
            "name": "Mechanical Keyboard",
            "brand": "Logitech",
            "price": 120,
            "stock": 25
        }]
    
    return render("products.html", product_items = product_items)    


 
def services(request):


    return render("services.html")


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

