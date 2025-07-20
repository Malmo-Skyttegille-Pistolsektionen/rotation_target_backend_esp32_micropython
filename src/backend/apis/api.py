import os
from backend.common.io_utils import dir_exists, make_dirs
from microdot import Microdot, Response
from backend.repositories.programs import programs
from backend.executor.program_executor import program_executor
from backend.io.targets import hide, show
from backend.repositories import program_state
from backend.repositories.audios import audios
from backend.version import VERSION
from libs.microdot.multipart import with_form_data
import logging

logging.debug("[API] Importing API routes...")

api_part = Microdot()
Response.default_content_type = "application/json"


@api_part.get("/version")
async def get_version(request):
    return {
        "major": VERSION.MAJOR,
        "minor": VERSION.MINOR,
        "patch": VERSION.PATCH,
    }


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
    logging.debug(f"[API] {request.method} {request.path} called")
    show()
    return {"message": "Target is now shown"}


@api_part.post("/targets/hide")
async def handle_targets_hide(request):
    logging.debug(f"[API] {request.method} {request.path} called")
    hide()
    return {"message": "Target is now hidden"}


@api_part.post("/targets/toggle")
async def handle_targets_toggle(request):
    logging.debug(f"[API] {request.method} {request.path} called")
    if program_state.target_status_shown:
        hide()
    else:
        show()
    return {
        "message": f"Target is now {'shown' if program_state.target_status_shown else 'hidden'}"
    }


@api_part.get("/programs")
async def programs_list(request):
    logging.debug(f"[API] {request.method} {request.path} called")
    result = [
        {
            "id": program.id,
            "title": program.title,
            "description": program.description,
            "readonly": program.readonly,
        }
        for program in programs.get_all().values()
    ]

    return result


@api_part.post("/programs")
async def programs_upload(request):
    logging.debug(f"[API] {request.method} {request.path} called")
    data = request.json

    try:
        program = await programs.add_uploaded(program_data=data)

        result = [
            {
                "id": program.id,
            }
        ]

        return result, 201
    except Exception as e:
        logging.debug(f"[API] Program upload failed: {e}")
        return {"ture"}, 400


@api_part.get("/programs/<int:program_id>")
async def programs_get(request, program_id):
    logging.debug(f"[API] {request.method} {request.path} called")

    program = programs.get(program_id)
    if program:
        return program.to_dict()
    logging.debug(f"[API] Program {program_id} not found")
    return {"error": "Not found"}, 404


@api_part.post("/programs/<int:program_id>/load")
async def programs_load(request, program_id):
    logging.debug(f"[API] {request.method} {request.path} called")

    if await program_executor.load(program_id):
        return {"message": "Program loaded", "program_id": program_id}

    logging.debug(f"[API] Program {program_id} not found for loading")
    return {"error": "Program ID not found"}, 404


@api_part.post("/programs/start")
async def handle_program_start(request):
    logging.debug(f"[API] {request.method} {request.path} called")

    if not await program_executor.start():
        return {"error": "No program loaded"}, 400

    return {"message": "Series started"}


@api_part.post("/programs/stop")
async def handle_program_stop(request):
    logging.debug(f"[API] {request.method} {request.path} called")

    if not await program_executor.stop():
        return {"error": "No program running"}, 400

    return {"message": "Series stopped and reset to the first event"}


@api_part.delete("/programs/<int:program_id>/delete")
async def programs_delete(request, program_id):
    logging.debug(f"[API] {request.method} {request.path} called")

    if not isinstance(program_id, int) or program_id < 0:
        return {"error": "Invalid ID"}, 400

    deleted = await programs.delete(program_id)
    if deleted:
        return {"message": "Program deleted successfully"}
    else:
        return {"error": "Program not found"}, 404


@api_part.post("/programs/series/<int:series_index>/skip_to")
async def skip_to_series(request, series_index):
    logging.debug(f"[API] {request.method} {request.path} called")

    success = await program_executor.skip_to_series(series_index)
    if not success:
        return {"error": "No program loaded or invalid series index"}, 400

    logging.info(
        f"Skipped to series {series_index} in program {getattr(program_state.program, 'id', None)}"
    )
    return {"message": f"Skipped to series {series_index}"}


@api_part.get("/audios")
async def audios_list(request):
    logging.debug(f"[API] {request.method} {request.path} called")
    audio = [audio.to_dict() for audio in audios.get_all().values()]
    return {"audios": audio}


@api_part.post("/audios")
@with_form_data
async def audios_upload(request):
    logging.debug(f"[API] {request.method} {request.path} called")
    logging.debug(
        f"[API] Request files: {getattr(
        request, 'files', None)}"
    )
    logging.debug(f"[API] Request form: {getattr(request, 'form', None)}")

    if (
        not hasattr(request, "files")
        or request.files is None
        or "file" not in request.files
    ):
        logging.debug("[API] No file uploaded in request")
        return {"error": "No file uploaded"}, 400

    file = request.files["file"]
    title = request.form.get("title")
    codec = request.form.get("codec")
    logging.debug(
        f"[API] Uploaded file: {file.filename}, title: {title}, codec: {codec}"
    )

    if not title or not codec:
        logging.debug("[API] Missing title or codec in form data")
        return {"error": "Missing title or codec"}, 400

    filename = file.filename
    save_path = f"resources/audio/{filename}"
    make_dirs("resources/audio")

    try:
        file.save(save_path)
        logging.debug(f"[API] File saved to {save_path}")
    except Exception as e:
        logging.debug(f"[API] Failed to save file: {e}")
        return {"error": "Failed to save file"}, 500

    try:
        audio = await audios.add_uploaded(title=title, filename=filename, codec=codec)
        logging.debug(f"[API] Audio uploaded successfully: {audio.to_dict()}")

        result = {"id": audio.id}

        return result, 201
    except Exception as e:
        logging.debug(f"[API] Failed to add uploaded audio: {e}")
        return {"error": "Failed to add audio"}, 500


@api_part.delete("/audios/<int:audio_id>/delete")
async def audios_delete(request, audio_id):
    logging.debug(f"[API] {request.method} {request.path} called")
    if not isinstance(audio_id, int) or audio_id < 0:
        return {"error": "Invalid ID"}, 400
    deleted = audios.delete_uploaded(audio_id)
    if deleted:
        return {"message": "Audio deleted successfully"}
    else:
        return {"error": "Audio not found"}, 404
