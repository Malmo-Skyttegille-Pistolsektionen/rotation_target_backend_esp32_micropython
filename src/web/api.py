from microdot import Microdot, Response
from common.common import program_state
from common.programs import   # Assuming you have an instance: programs = Programs()
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
    program_state["target_status_shown"] = True
    return {"message": "Target is now shown"}


@api_part.route(url_pattern="/targets/hide", methods=["POST"])
def handle_targets_hide(request):
    program_state["target_status_shown"] = False
    return {"message": "Target is now hidden"}


@api_part.route(url_pattern="/targets/toggle", methods=["POST"])
def handle_targets_toggle(request):
    program_state["target_status_shown"] = not program_state["target_status_shown"]
    return {
        "message": f"Target is now {'shown' if program_state['target_status_shown'] else 'hidden'}"
    }


@api_part.route("/programs", methods=["GET"])
def programs_list(request):
    print("[API] GET /programs called")
    # List all programs
    return [p.to_dict() for p in list_programs()]


@api_part.route("/programs", methods=["POST"])
def programs_upload(request):
    print("[API] POST /programs called")
    # Upload a new program
    data = request.json
    program = add_program(data)
    return program.to_dict(), 201


@api_part.route("/programs/<int:program_id>", methods=["GET"])
def programs_get(request, program_id):
    print(f"[API] GET /programs/{program_id} called")
    # Get a program by id
    program = get_program(program_id)
    if program:
        return program.to_dict()
    print(f"[API] Program {program_id} not found")
    return {"error": "Not found"}, 404


@api_part.route("/programs/<int:program_id>/load", methods=["POST"])
def programs_load(request, program_id):
    print(f"[API] POST /programs/{program_id}/load called")
    # Load a program by id
    if load_program(program_id):
        print(f"[API] Program {program_id} loaded")
        return {"message": "Program loaded", "program_id": program_id}
    print(f"[API] Program {program_id} not found for loading")
    return {"error": "Not found"}, 404


@api_part.route(url_pattern="/programs/start", methods=["POST"])
def handle_program_start(request):
    if program_state["program_id"] is None:
        return {"error": "No program loaded"}, 400

    program_state["running_series_start"] = "started"
    return {"message": "Program started"}


@api_part.route(url_pattern="/programs/stop", methods=["POST"])
def handle_program_stop(request):
    if program_state["running_series_start"] is None:
        return {"error": "No program running"}, 400

    program_state["running_series_start"] = None
    program_state["current_event_index"] = 0
    return {"message": "Program stopped and reset to the first event"}


