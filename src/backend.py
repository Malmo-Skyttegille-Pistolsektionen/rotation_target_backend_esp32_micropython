# https://awesome-micropython.com/
# import os
# print(os.listdir(''))


import sys
sys.path.append('/libs', 'src')
from microdot.microdot import Microdot, Response
import asyncio
from web.api import api_md
from web.sse import sse_md
from web.static import static_part


# Initialize Microdot app
def create_app():
    app = Microdot()
    Response.default_content_type = "application/json"
    app.mount(api_md, url_prefix='/api/v1')
    app.mount(sse_md, url_prefix='/sse/v1')
    app.mount(static_part, url_prefix='/')

    return app


async def main():
    app = create_app()
    # start the server in a background task
    server = asyncio.create_task(app.start_server(port=80, debug=True))
    print("Server started on port 80")

    # ... do other asynchronous work here ...

    # cleanup before ending the application
    await server

asyncio.run(main())