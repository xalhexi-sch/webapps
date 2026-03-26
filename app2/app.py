import os
from jinja2 import Environment, FileSystemLoader
from werkzeug.routing import Map, Rule
from werkzeug.wrappers import Request, Response
from werkzeug.exceptions import NotFound
from werkzeug.serving import run_simple
from werkzeug.middleware.shared_data import SharedDataMiddleware
from applogic.products import (
    get_all_products,
    get_product_by_id,
    get_products_by_category,
    create_product,
    update_product,
    delete_product,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env = Environment(loader=FileSystemLoader(os.path.join(BASE_DIR, 'templates')))

url_map = Map([
    Rule('/',        endpoint='home'),
    Rule('/about',   endpoint='about'),
    Rule('/contact', endpoint='contact'),

    # products
    Rule('/products',                 endpoint='product_list',   methods=['GET']),
    Rule('/products/create',          endpoint='product_create', methods=['GET', 'POST']),
    Rule('/products/<int:id>',        endpoint='product_detail', methods=['GET']),
    Rule('/products/<int:id>/edit',   endpoint='product_edit',   methods=['GET', 'POST']),
    Rule('/products/<int:id>/delete', endpoint='product_delete', methods=['POST']),

])

# Renderer
def render(template, context={}, status=200):
    html = env.get_template(template).render(context)
    return Response(html, status=status, content_type='text/html; charset=utf-8')

# Redirect helper               ← ADD THIS RIGHT HERE
def redirect(location):
    return Response(status=302, headers={'Location': location})


def home(request):
    return render('home.html', {          # was 'index.html'
        'heading': 'Hello, World!',
        'message': 'Welcome!',
    })

def about(request):
    return render('about.html', {         # was 'index.html'
        'heading': 'About Us',
        'message': 'This is the about page.',
    })

def contact(request):
    return render('contact.html', {       # was 'index.html'
        'heading': 'Contact Us',
        'message': 'This is the contact page.',
    })

def not_found(request):
    return render('404.html', {}, status=404)   # was 'index.html'


def product_list(request):
    products = get_all_products()
    return render('products/list.html', {
        'products': products,
    })

def product_detail(request, id):
    product = get_product_by_id(id)
    if product is None:
        return not_found(request)
    return render('products/detail.html', {
        'product': product,
    })

def product_create(request):
    error = None
    if request.method == 'POST':
        name     = request.form.get('product_name', '').strip()
        desc     = request.form.get('product_description', '').strip()
        category = request.form.get('product_category', '').strip()
        price    = request.form.get('product_price', '').strip()
        if not name:
            error = 'Product name is required.'
        elif not price:
            error = 'Product price is required.'
        else:
            try:
                price = float(price)
            except ValueError:
                error = 'Price must be a valid number (e.g. 299.00).'
        if error is None:
            create_product(name=name, price=price,
                           description=desc or None, category=category or None)
            return redirect('/it21-banas/products')

    return render('products/form.html', {
        'title':   'Add Product',
        'action':  '/it21-banas/products/create',
        'product': None,
        'error':   error,
    })

def product_edit(request, id):
    product = get_product_by_id(id)
    if product is None:
        return not_found(request)
    error = None
    if request.method == 'POST':
        name     = request.form.get('product_name', '').strip()
        desc     = request.form.get('product_description', '').strip()
        category = request.form.get('product_category', '').strip()
        price    = request.form.get('product_price', '').strip()
        if not name:
            error = 'Product name is required.'
        elif not price:
            error = 'Product price is required.'
        else:
            try:
                price = float(price)
            except ValueError:
                error = 'Price must be a valid number (e.g. 299.00).'
        if error is None:
            update_product(product_id=id, name=name, price=price,
                           description=desc or None, category=category or None)
            return redirect(f'/it21-banas/products/{id}')

    return render('products/form.html', {
        'title':   f'Edit — {product.product_name}',
        'action':  f'/it21-banas/products/{id}/edit',
        'product': product,
        'error':   error,
    })

def product_delete(request, id):
    delete_product(id)
    return redirect('/it21-banas/products')



# Router
VIEWS = {
    'home':           home,
    'about':          about,
    'contact':        contact,
    'product_list':   product_list,
    'product_create': product_create,
    'product_detail': product_detail,
    'product_edit':   product_edit,
    'product_delete': product_delete,
}


def wsgi_app(environ, start_response):
    request = Request(environ)
    adapter = url_map.bind_to_environ(environ)
    try:
        endpoint, kwargs = adapter.match()
        response = VIEWS[endpoint](request, **kwargs)
    except NotFound:
        response = not_found(request)
    except Exception as e:
        import traceback
        traceback.print_exc()                        # ← ADD THIS
        response = Response(f"Error: {e}", status=500)
    return response(environ, start_response)

# static files middle ware
app = SharedDataMiddleware(wsgi_app, {
    '/static': os.path.join(BASE_DIR, 'static')
})

