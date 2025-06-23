import os
from microdot import Microdot, Response
from common.programs import programs
from common.program_executor import program_executor
from common.target import hide, show  # Import the singleton instance
from common.common import program_state
from common.audios import audios  # Singleton instance of Audios

print("[API] Importing API routes...")

api_part = Microdot()
Response.default_content_type = "application/json"


@api_part.get("/status")
async def status(request):
    response = {
        "running": program_state.running_series_start is not None,
        "next_event": (
            {
                "program_id": program_state.program.id,
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
        program = programs.add_uploaded(program_data=data)
        print(f"[API] HERE!!!!")

        result = [
            {
                "id": program.id,
            }
        ]

        return result, 201
    except Exception as e:
        print(f"[API] Program upload failed: {e}")
        return {"ture"}, 400


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


@api_part.get("/audios")
async def audios_list(request):
    print(f"[API] {request.method} {request.path} called")
    builtin = [audio.to_dict() for audio in audios.get_all().values() if audio.readonly]
    uploaded = [
        audio.to_dict() for audio in audios.get_all().values() if not audio.readonly
    ]
    return {"builtin": builtin, "uploaded": uploaded}


@api_part.post("/audios")
async def audios_upload(request):
    print(f"[API] {request.method} {request.path} called")
    # Expecting multipart/form-data with file, title, codec
    if request.files is None or "file" not in request.files:
        return {"error": "No file uploaded"}, 400
    file = request.files["file"]
    title = request.form.get("title")
    codec = request.form.get("codec")
    if not title or not codec:
        return {"error": "Missing title or codec"}, 400

    # Save file to /resources/audio/
    filename = file.filename
    save_path = f"resources/audio/{filename}"
    os.makedirs("resources/audio", exist_ok=True)
    with open(save_path, "wb") as f:
        f.write(file.read())

    audio = await audios.add_uploaded(title=title, filename=filename, codec=codec)
    result = [
        {
            "id": audio.id,
        }
    ]

    return result, 201


@api_part.delete("/audios/<int:audio_id>/delete")
async def audios_delete(request, audio_id):
    print(f"[API] {request.method} {request.path} called")
    if not isinstance(audio_id, int) or audio_id < 0:
        return {"error": "Invalid ID"}, 400
    deleted = audios.delete_uploaded(audio_id)
    if deleted:
        return {"message": "Audio deleted successfully"}
    else:
        return {"error": "Audio not found"}, 404
