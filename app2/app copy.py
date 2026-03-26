import os
from jinja2 import Environment, FileSystemLoader
from werkzeug.routing import Map, Rule
from werkzeug.wrappers import Request, Response
from werkzeug.exceptions import NotFound
from werkzeug.serving import run_simple
from werkzeug.middleware.shared_data import SharedDataMiddleware
from applogic.products import get_all_products, get_product_by_id, get_products_by_category

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env = Environment(loader=FileSystemLoader(os.path.join(BASE_DIR, 'templates')))

url_map = Map([
    Rule('/',        endpoint='home'),
    Rule('/about',   endpoint='about'),
    Rule('/contact', endpoint='contact'),
])

# Renderer
def render(template, context={}, status=200):
    html = env.get_template(template).render(context)
    return Response(html, status=status, content_type='text/html; charset=utf-8')

# Views
def home(request):
    context = {
        'title':   'Home',
        'heading': 'Hello, World!',
        'message': 'Welcome!',
    }
    return render('index.html', context)

def about(request):
    context = {
        'title':   'About',
        'heading': 'About Us',
        'message': 'This is the about page.',
    }
    return render('index.html', context)

def contact(request):
    context = {
        'title':   'Contact',
        'heading': 'Contact Us',
        'message': 'This is the contact page.',
    }
    return render('index.html', context)

def not_found(request):
    context = {
        'title':   '404',
        'heading': '404 - Not Found',
        'message': 'Page does not exist.',
    }
    return render('index.html', context, status=404)


# Product Views

def product_list(request):
    """GET /products — retrieve every product and render the list."""
    products = get_all_products()           # ← from products.py
    return render('products/list.html', {
        'title':    'Products',
        'products': products,
    })
    

# Router
VIEWS = {
    'home':    home,
    'about':   about,
    'contact': contact,
}

def wsgi_app(environ, start_response):
    request = Request(environ)
    adapter = url_map.bind_to_environ(environ)
    try:
        endpoint, kwargs = adapter.match()
        response = VIEWS[endpoint](request, **kwargs)
    except NotFound:
        response = not_found(request)
    except Exception:
        response = Response("Internal Server Error", status=500)
    return response(environ, start_response)

# static files middle ware
app = SharedDataMiddleware(wsgi_app, {
    '/static': os.path.join(BASE_DIR, 'static')
})

