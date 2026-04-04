from contextvars import ContextVar
from uuid import uuid4
import logging


request_id_var = ContextVar("request_id", default="-")
request_method_var = ContextVar("request_method", default="-")
request_path_var = ContextVar("request_path", default="-")
request_user_var = ContextVar("request_user", default="-")


def generate_request_id() -> str:
    return uuid4().hex


def set_request_context(*, request_id: str, method: str = "-", path: str = "-", user: str = "-") -> None:
    request_id_var.set(request_id)
    request_method_var.set(method)
    request_path_var.set(path)
    request_user_var.set(user)


def clear_request_context() -> None:
    request_id_var.set("-")
    request_method_var.set("-")
    request_path_var.set("-")
    request_user_var.set("-")


class RequestContextFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_var.get()
        record.request_method = request_method_var.get()
        record.request_path = request_path_var.get()
        record.request_user = request_user_var.get()
        return True