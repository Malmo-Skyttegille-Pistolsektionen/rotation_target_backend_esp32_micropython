from microdot import Microdot
from common import program_state

api_md = Microdot

# REST API Handlers (Base URL: /api/v1)
@api_md.route("/status", methods=["GET"])
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


@api_md.route("/targets/show", methods=["POST"])
def handle_targets_show(request):
    program_state["target_status_shown"] = True
    return {"message": "Target is now shown"}


@api_md.route("/targets/hide", methods=["POST"])
def handle_targets_hide(request):
    program_state["target_status_shown"] = False
    return {"message": "Target is now hidden"}


@api_md.route("/targets/toggle", methods=["POST"])
def handle_targets_toggle(request):
    program_state["target_status_shown"] = not program_state["target_status_shown"]
    return {
        "message": f"Target is now {'shown' if program_state['target_status_shown'] else 'hidden'}"
    }


@api_md.route("/programs", methods=["GET"])
def handle_programs(request):
    response = [{"id": 1, "title": "Program 1", "description": "Sample program"}]
    return response


@api_md.route("/programs/1/load", methods=["POST"])
def handle_program_load(request):
    program_state.update(
        {
            "program_id": 1,
            "running_series_start": None,
            "current_series_index": 0,
            "current_event_index": 0,
        }
    )
    return {"message": "Program loaded"}


@api_md.route("/programs/start", methods=["POST"])
def handle_program_start(request):
    if program_state["program_id"] is None:
        return {"error": "No program loaded"}, 400

    program_state["running_series_start"] = "started"
    return {"message": "Program started"}


@api_md.route("/programs/stop", methods=["POST"])
def handle_program_stop(request):
    if program_state["running_series_start"] is None:
        return {"error": "No program running"}, 400

    program_state["running_series_start"] = None
    program_state["current_event_index"] = 0
    return {"message": "Program stopped and reset to the first event"}


