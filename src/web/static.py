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

    return send_file("static/webapp/index.html", max_age=3600)


@static_part.get(url_pattern="/<path:path>")
async def static_files(request, path):
    try:
        logging.debug(f"[Static] Serving ({request.path} ): {request.path} ")
        return send_file(f"static/webapp/{path}")
    except OSError:
        return {"error": "resource not found"}, 404
    finally:
        logging.debug(f"[Static] Finished serving ({request.path} ): {request.path} ")
