from .chat import router as chat_router
from .channels_api import router as channels_router
from .compress import router as compress_router
from .config_api import router as config_router
from .cron_api import router as cron_router
from .evolution_api import router as evolution_router
from .files import router as files_router
from .heartbeat_api import router as heartbeat_router
from .sessions import router as sessions_router
from .tokens import router as tokens_router

__all__ = [
    "chat_router",
    "channels_router",
    "compress_router",
    "config_router",
    "cron_router",
    "evolution_router",
    "files_router",
    "heartbeat_router",
    "sessions_router",
    "tokens_router",
]
