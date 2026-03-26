import os
from jinja2 import Environment, FileSystemLoader
from werkzeug.routing import Map, Rule
from werkzeug.wrappers import Request, Response
from werkzeug.exceptions import NotFound
from werkzeug.serving import run_simple
from werkzeug.middleware.shared_data import SharedDataMiddleware


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



# Router
VIEWS = {
    'home':           home,
    'about':          about,
    'contact':        contact,
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