import contextvars
import uuid
request_id_ctx_var: contextvars.ContextVar[str] = contextvars.ContextVar(
    "request_id", default="-")


class RequestIDMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope["headers"])
        incoming = headers.get(b"x-request-id")

        request_id = incoming.decode(
            "utf-8") if incoming else str(uuid.uuid4())
        token = request_id_ctx_var.set(request_id)

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                message["headers"] = list(message.get("headers", [])) + [
                    (b"x-request-id", request_id.encode("utf-8"))
                ]
            await send(message)
            
        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            request_id_ctx_var.reset(token)
