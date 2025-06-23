from microdot import Microdot, send_file
import logging

static_part = Microdot()

logging.debug("[STATIC] Importing static routes...")

MIME_TYPES = {
    ".svg": "image/svg+xml",
}


# Static File Handlers
@static_part.route("/")
async def index(request):
    logging.debug("[Static] Serving index.html")

    return send_file("static/webapp/index.html", max_age=3600)


@static_part.get(url_pattern="/<path:path>")
async def static_files(request, path):
    try:
        logging.debug(f"[Static] Request ({request.path} ): {request.path} ")

        ext = None
        if "." in path:
            ext = "." + path.rsplit(".", 1)[1]

        if ext in MIME_TYPES:
            logging.debug(
                f"[Static] Serving file (content_type={MIME_TYPES[ext]}): {path}"
            )
            return send_file(
                "static/webapp/" + path, content_type=MIME_TYPES[ext], max_age=3600
            )

        logging.debug(f"[Static] Serving file: {path}")
        return send_file(f"static/webapp/{path}", max_age=3600)
    except OSError:
        return {"error": "resource not found"}, 404
