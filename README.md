
## Overview

This project provides a backend and web interface for controlling a target system using an ESP32 running MicroPython. It supports uploading and managing programs and audio files, and controls hardware via GPIO (e.g., for a DB9 connector using a MOSFET or relay).

- **Backend:** MicroPython + Microdot (async web server)  
- **Frontend:** Web app (static files)  
- **Hardware:** ESP32, DB9 connector, SOT23/SOT223 MOSFET or relay  

## Setup

## Hardware Setup

| ESP32 Pin | DB9 Pin | Function        | Notes                    |
|-----------|---------|----------------|--------------------------|
| GPIO5     | 2       | Target Control | Connect via SOT23 MOSFET |
| GND       | 5       | Ground         | Common ground            |

**Wiring Diagram:**

- The circuit uses a [BC547B NPN Transistor](https://www.electrokit.com/bc547b-to-92-npn-45v-100ma) (TO-92 package) 

[DB9 to ESP32 wiring with BC547B transistor](https://user-images.githubusercontent.com/docs/images/wiring - DB9.png)

```
ESP32 GPIO5 ----[1kΩ resistor]----|B  BC547B  C|---- DB9 Pin 2 (Target Control)
  |            |
     ESP32 GND -------|E
   |
  DB9 Pin 5 (Ground)
```

[View interactive wiring diagram](https://www.falstad.com/circuit/circuitjs.html?ctz=CQAgjCAMB0l3BWEBmAHAJmgdgGzoRmACzICcpkORIOESCkICApgLRhgBQA7iFuoxyRUfAU1xQeowUUb85YyJwBOIVFXE41GoqkaMw8Jb3XUiG0yF37OABzXJ0mh0-koo4cEfhTUj55YIEsbSoXoKNrxuQVpYyFoxkiZwAf6JIeFh-m4ZKYlxCcFSCKSuYnjUOVIVoW5VAC40-DToleWtHhAwCEJYREQIjpD4QehO3aQlpFik8VgEw2NejAAmzABmAIYArgA29dXCLdQlTjVKqjVXPcedRtU3V83n1R1XRy8Abkz9oQi-5xATicYGgOCQoPBHm6nAA5i4sq4EONJAAlbRmCw6fz6KyMJC4mH2U63EluZDQ5beYq-aKlUIhf7UGokl4AeyBEA0jFkpBEBOgXXAnA5zOoPMgfKYUEFnU4QA)


### 1. Clone the Repository

Clone this repository to your local machine:

```bash
git clone https://github.com/jimisola/msg_rotation-target-backend.git
cd msg_rotation-target-backend
```

### 2. Install Requirements

- Install MicroPython firmware on your ESP32.
- Install `mpremote`:

```bash
pip install mpremote
```

### 3. Configure WiFi

- Copy `wifi_credentials.py.example` to `wifi_credentials.py` and fill in your WiFi details.
- `wifi_credentials.py` is in `.gitignore` and will not be tracked by git.

## Uploading Code to ESP32

This project provides several VS Code tasks (see `.vscode/tasks.json`) for managing files on your ESP32 using `mpremote`.

### Device Path

When running a task, you will be prompted for the ESP32 device path (default: `/dev/ttyUSB0`).  
Adjust as needed for your system (e.g., `ttyACM0`).

### Available Tasks

- **Wipe ESP32 flash:**  
  Removes all files from the ESP32 filesystem.
- **Upload `/*.py` to ESP32:**  
  Uploads all Python files in the project root.
- **Upload `src` to ESP32:**  
  Uploads the `src` directory.
- **Upload `libs` to ESP32:**  
  Uploads the `libs` directory.
- **Upload `static` to ESP32:**  
  Uploads the `static` directory.
- **Upload all project folders to ESP32:**  
  Runs all upload tasks in sequence.
- **Wipe and Upload All:**  
  Wipes the ESP32 and uploads all project folders.

### To use a task:

1. Open the Command Palette in VS Code (`Ctrl+Shift+P`)
2. Type **"Run Task"**
3. Select the desired task

## Running the Backend

The backend is started automatically when the ESP32 boots (see `main.py` and `backend.py`).  
The web server will be available on the ESP32's IP address (check your router or serial output for the address).

## Development Workflow

1. Edit your code or static files.
2. Use the appropriate VS Code task to upload your changes to the ESP32 (see the "Available Tasks" section above).
3. After uploading, reset or reboot the ESP32 if the changes do not take effect automatically. You can do this by pressing the reset button on the board or using a serial terminal to send a reset command.

## Troubleshooting

- **MemoryError:**  
  Try uploading smaller files or reducing memory usage.
- **File not found:**  
  Ensure you have uploaded all required files and folders.
- **Device not found:**  
  Double-check the device path when prompted by VS Code tasks.

## File Structure

- `src` — Main Python source code (backend, API, logic)  
- `libs` — Third-party or shared Python libraries (e.g., Microdot, logging, typing)  
- `static` — Static files for the web interface  
- `tasks.json` — VS Code tasks for managing the ESP32  

## VS Code Tasks Reference

See `tasks.json` for full details.  
You can customize or add tasks as needed for your workflow.

## API Reference

See [`docs/openapi.yaml`](docs/openapi.yaml) for the full API specification.

You can view and interact with the API using [Swagger Editor](https://editor.swagger.io/) by uploading the `openapi.yaml` file.

## License

MIT