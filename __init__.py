import server
from aiohttp import web

from .text_editor_node import (
    NODE_CLASS_MAPPINGS,
    NODE_DISPLAY_NAME_MAPPINGS,
    confirm_pending,
    pending_status,
)

WEB_DIRECTORY = "."

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']


@server.PromptServer.instance.routes.post("/ares_text_editor/confirm")
async def confirm(request):
    data = await request.json()
    if data.get("node_id") is None or "text" not in data:
        return web.Response(status=400, text="missing node_id or text")
    confirm_pending(str(data["node_id"]), data["text"])
    return web.Response(status=200)


@server.PromptServer.instance.routes.get("/ares_text_editor/status/{node_id}")
async def status(request):
    info = pending_status(request.match_info["node_id"])
    if info is None:
        return web.Response(status=404)
    return web.json_response(info)
