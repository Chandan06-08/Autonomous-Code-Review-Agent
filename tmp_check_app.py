from backend.main import app
print(app.title)
print([route.path for route in app.routes if route.path.startswith('/api')])
