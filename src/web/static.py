from microdot import Microdot, send_file

static_part = Microdot()

print("[STATIC] Importing static routes...")

MIME_TYPES = {
    ".svg": "image/svg+xml",
}


# Static File Handlers
@static_part.route("/")
async def index(request):
    print("[Static] Serving index.html")

    return send_file("static/webapp/index.html")


@static_part.route(url_pattern="/<path:path>")
async def static_files(request, path):
    try:
        print(f"[Static] Request ({request.path} ): {request.path} ")

        ext = None
        if "." in path:
            ext = "." + path.rsplit(".", 1)[1]

        if ext in MIME_TYPES:
            print(f"[Static] Serving file (content_type={MIME_TYPES[ext]}): {path}")
            return send_file("static/webapp/" + path, content_type=MIME_TYPES[ext])

        print(f"[Static] Serving file: {path}")
        return send_file(f"static/webapp/{path}")
    except OSError:
        return {"error": "resource not found"}, 404
