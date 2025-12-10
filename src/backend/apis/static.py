from microdot import Microdot, send_file
import logging

from microdot.microdot import Response

static_part = Microdot()

logging.debug("[STATIC] Importing static routes...")

# Set content type not set by microdot
Response.types_map["svg"] = "image/svg+xml"
Response.types_map["ico"] = "image/x-icon"


# Static File Handlers
@static_part.route("/")
async def index(request):
    logging.debug("[Static] Serving index.html")

    return send_file("src/static/webapp/index.html", max_age=3600)


@static_part.get(url_pattern="/<path:path>")
async def static_files(request, path):
    try:
        filename = f"src/static/webapp/{path}"
        logging.debug(f"[Static] Serving ({request.path} ): {filename} ")
        return send_file(filename)
    except OSError:
        return {"error": "resource not found"}, 404
