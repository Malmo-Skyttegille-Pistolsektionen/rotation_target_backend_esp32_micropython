from microdot import Microdot, Response
from common.common import program_state
from common.programs import programs  # Import the singleton instance

print("[API] Importing API routes...")

api_part = Microdot()
Response.default_content_type = "application/json"


@api_part.route(url_pattern="/status", methods=["GET"])
def handle_status(request):
    response = {
        "running": program_state["running_series_start"] is not None,
        "next_event": (
            {
                "program_id": program_state["program_id"],
                "series_index": program_state["current_series_index"],
                "event_index": program_state["current_event_index"] + 1,
            }
            if program_state["running_series_start"]
            and program_state["current_series_index"] is not None
            and program_state["current_event_index"] is not None
            else None
        ),
        "target_status": "shown" if program_state["target_status_shown"] else "hidden",
    }
    return response


@api_part.route(url_pattern="/targets/show", methods=["POST"])
def handle_targets_show(request):
    print(f"[API] {request.method} {request.path} called")
    program_state["target_status_shown"] = True
    return {"message": "Target is now shown"}


@api_part.route(url_pattern="/targets/hide", methods=["POST"])
def handle_targets_hide(request):
    print(f"[API] {request.method} {request.path} called")
    program_state["target_status_shown"] = False
    return {"message": "Target is now hidden"}


@api_part.route(url_pattern="/targets/toggle", methods=["POST"])
def handle_targets_toggle(request):
    print(f"[API] {request.method} {request.path} called")
    program_state["target_status_shown"] = not program_state["target_status_shown"]
    return {
        "message": f"Target is now {'shown' if program_state['target_status_shown'] else 'hidden'}"
    }


@api_part.route("/programs", methods=["GET"])
def programs_list(request):
    print(f"[API] {request.method} {request.path} called")
    result = programs.list()
    print("programs.list() called: ", result)
    print("[API] Returning:", result)
    return result


@api_part.route("/programs", methods=["POST"])
def programs_upload(request):
    print(f"[API] {request.method} {request.path} called")
    data = request.json
    program = programs.add(data)
    return program.to_dict(), 201


@api_part.route("/programs/<int:program_id>", methods=["GET"])
def programs_get(request, program_id):
    print(f"[API] {request.method} {request.path} called")
    program = programs.get(program_id)
    if program:
        return program.to_dict()
    print(f"[API] Program {program_id} not found")
    return {"error": "Not found"}, 404


@api_part.route("/programs/<int:program_id>/load", methods=["POST"])
def programs_load(request, program_id):
    print(f"[API] {request.method} {request.path} called")
    if programs.load(program_id):
        print(f"[API] Program {program_id} loaded")
        return {"message": "Program loaded", "program_id": program_id}
    print(f"[API] Program {program_id} not found for loading")
    return {"error": "Not found"}, 404


@api_part.route(url_pattern="/programs/start", methods=["POST"])
def handle_program_start(request):
    print(f"[API] {request.method} {request.path} called")
    if program_state["program_id"] is None:
        return {"error": "No program loaded"}, 400

    program_state["running_series_start"] = "started"
    return {"message": "Series started"}


@api_part.route(url_pattern="/programs/stop", methods=["POST"])
def handle_program_stop(request):
    print(f"[API] {request.method} {request.path} called")
    if program_state["running_series_start"] is None:
        return {"error": "No program running"}, 400

    program_state["running_series_start"] = None
    program_state["current_event_index"] = 0
    return {"message": "Program stopped and reset to the first event"}
