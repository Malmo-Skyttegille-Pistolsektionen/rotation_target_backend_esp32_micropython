import asyncio
from microdot import Microdot, Response
from common.programs import programs
from program_executor import program_executor
from target import hide, show  # Import the singleton instance
from common.common import program_state

print("[API] Importing API routes...")

api_part = Microdot()
Response.default_content_type = "application/json"


@api_part.get("/status")
async def status(request):
    response = {
        "running": program_state.running_series_start is not None,
        "next_event": (
            {
                "program_id": program_state.program_id,
                "series_index": program_state.current_series_index,
                "event_index": program_state.current_event_index
                + 1,  # might not be correct if current_event_index is 0
            }
            if program_state.running_series_start
            and program_state.current_series_index is not None
            and program_state.current_event_index is not None
            else None
        ),
        "target_status": "shown" if program_state.target_status_shown else "hidden",
    }
    return response


@api_part.post("/targets/show")
async def handle_targets_show(request):
    print(f"[API] {request.method} {request.path} called")
    show()
    return {"message": "Target is now shown"}


@api_part.post("/targets/hide")
async def handle_targets_hide(request):
    print(f"[API] {request.method} {request.path} called")
    hide()
    return {"message": "Target is now hidden"}


@api_part.post("/targets/toggle")
async def handle_targets_toggle(request):
    print(f"[API] {request.method} {request.path} called")
    if program_state.target_status_shown:
        hide()
    else:
        show()
    return {
        "message": f"Target is now {'shown' if program_state.target_status_shown else 'hidden'}"
    }


@api_part.get("/programs")
async def programs_list(request):
    print(f"[API] {request.method} {request.path} called")
    result = [
        {
            "id": program.id,
            "title": program.title,
            "description": program.description,
        }
        for program in programs.get_all().values()
    ]

    print("programs.list() called: ", result)
    print("[API] Returning:", result)
    return result


@api_part.post("/programs")
async def programs_upload(request):
    print(f"[API] {request.method} {request.path} called")
    data = request.json

    try:
        program = programs.upload(program_data=data)
        return program.to_dict(), 201
    except Exception as e:
        print(f"[API] Program upload failed: {e}")
        return {"error": "Invalid program structure"}, 400


@api_part.get("/programs/<int:program_id>")
async def programs_get(request, program_id):
    print(f"[API] {request.method} {request.path} called")

    program = programs.get(program_id)
    if program:
        return program.to_dict()
    print(f"[API] Program {program_id} not found")
    return {"error": "Not found"}, 404


@api_part.post("/programs/<int:program_id>/load")
async def programs_load(request, program_id):
    print(f"[API] {request.method} {request.path} called")

    if await program_executor.load(program_id):
        return {"message": "Program loaded", "program_id": program_id}

    print(f"[API] Program {program_id} not found for loading")
    return {"error": "Program ID not found"}, 404


@api_part.post("/programs/start")
async def handle_program_start(request):
    print(f"[API] {request.method} {request.path} called")

    if not await program_executor.start():
        return {"error": "No program loaded"}, 400

    return {"message": "Series started"}


@api_part.post("/programs/stop")
async def handle_program_stop(request):
    print(f"[API] {request.method} {request.path} called")

    if not await program_executor.stop():
        return {"error": "No program running"}, 400

    return {"message": "Series stopped and reset to the first event"}


@api_part.delete("/programs/<int:program_id>/delete")
async def programs_delete(request, program_id):
    print(f"[API] {request.method} {request.path} called")

    if not isinstance(program_id, int) or program_id < 0:
        return {"error": "Invalid ID"}, 400

    deleted = programs.delete(program_id)
    if deleted:
        return {"message": "Program deleted successfully"}
    else:
        return {"error": "Program not found"}, 404
