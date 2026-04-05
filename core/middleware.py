import logging
import time
from .logging_context import (
    clear_request_context,
    generate_request_id,
    set_request_context,
)

logger = logging.getLogger(__name__)

class RequestContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = request.headers.get("X-Request-ID") or generate_request_id()
        user = "-"
        if hasattr(request, "user") and request.user.is_authenticated:
            user = str(request.user)

        set_request_context(
            request_id=request_id,
            method=request.method,
            path=request.path,
            user=user,
        )
        request.request_id = request_id
        start_time = time.perf_counter()

        logger.info(
            "Request masuk. method=%s, path=%s",
            request.method,
            request.path,
        )

        try:
            response = self.get_response(request)
        except Exception:
            logger.exception(
                "Request gagal karena exception. method=%s, path=%s",
                request.method,
                request.path,
            )
            clear_request_context()
            raise

        response["X-Request-ID"] = request_id
        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "Request selesai. status=%s, durasi_ms=%.2f",
            getattr(response, "status_code", "-"),
            duration_ms,
        )
        clear_request_context()
        return response