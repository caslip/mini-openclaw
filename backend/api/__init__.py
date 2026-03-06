from .chat import router as chat_router
from .compress import router as compress_router
from .config_api import router as config_router
from .files import router as files_router
from .sessions import router as sessions_router
from .tokens import router as tokens_router

__all__ = [
    "chat_router",
    "compress_router",
    "config_router",
    "files_router",
    "sessions_router",
    "tokens_router",
]
