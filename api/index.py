import os
import sys
from pathlib import Path

# Add the project directory to the Python path
project_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_dir))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'credit_system.settings')
os.environ.setdefault('VERCEL', 'True')

# Import Django and setup
import django
django.setup()

from django.core.handlers.wsgi import WSGIHandler

# Initialize WSGI application
application = WSGIHandler()

def handler(request, context=None):
    """
    Vercel Python handler function.
    Converts Vercel request to WSGI and Django response back to Vercel format.
    """
    # Create a mock WSGI environment from the Vercel request
    environ = {
        'REQUEST_METHOD': request.method,
        'SCRIPT_NAME': '',
        'PATH_INFO': request.path,
        'QUERY_STRING': request.url.query or '',
        'SERVER_NAME': request.url.hostname or 'localhost',
        'SERVER_PORT': '443' if request.url.hostname else '80',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'HTTP_HOST': request.headers.get('host', ''),
        'HTTP_ACCEPT': request.headers.get('accept', '*/*'),
        'HTTP_ACCEPT_ENCODING': request.headers.get('accept-encoding', ''),
        'HTTP_ACCEPT_LANGUAGE': request.headers.get('accept-language', ''),
        'HTTP_USER_AGENT': request.headers.get('user-agent', ''),
        'wsgi.input': None,
        'wsgi.errors': sys.stderr,
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.multithread': True,
        'wsgi.multiprocess': True,
        'wsgi.run_once': False,
    }

    # Add headers
    for key, value in request.headers.items():
        http_key = f'HTTP_{key.upper().replace("-", "_")}'
        environ[http_key] = value

    # Add body for POST/PUT requests
    if request.method in ['POST', 'PUT', 'PATCH']:
        if hasattr(request, 'body') and request.body:
            environ['wsgi.input'] = request.body
            environ['CONTENT_LENGTH'] = str(len(request.body))

    # Create response start callback
    status = '200 OK'
    response_headers = []

    def start_response(status, response_headers, exc_info=None):
        return lambda x: None

    # Get response from Django
    response = application(environ, start_response)

    # Convert response to Vercel format
    status_code = int(status.split()[0])
    headers = {k: v for k, v in response_headers}

    # Build response body
    body = b''.join(response)

    from django.http import JsonResponse
    return JsonResponse(
        content=body.decode('utf-8') if body else '{}',
        status=status_code,
        headers=headers
    )

