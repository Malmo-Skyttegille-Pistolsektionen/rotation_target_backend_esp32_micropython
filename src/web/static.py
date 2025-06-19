from microdot import Microdot, send_file

static_part = Microdot()

# Static File Handlers
@static_part.route("/")
async def index(request):
    return send_file("static/webapp/index.html")

@static_part.route(url_pattern="/<path:path>")
async def static_files(request, path):
    try:
        return send_file(f"static/webapp/{path}")
    except OSError:
        return {'error': 'resource not found'}, 404

