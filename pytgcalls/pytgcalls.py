from typing import Callable

from pyrogram import Client
from .methods import Methods
from .methods.listener import ListenerKick


class PyTgCalls(Methods):
    def __init__(self, port: int = 24859):
        self._app = None
        self._app_core = None
        self._sio = None
        self._host = '127.0.0.1'
        self._port = port
        self._init_js_core = False
        self._on_event_update = {
            'EVENT_UPDATE_HANDLER': [],
            'STREAM_END_HANDLER': [],
            'CUSTOM_API_HANDLER': []
        }
        self._my_id = 0
        self.is_running = False
        self._current_active_chats = []
        self._session_id = self._generate_session_id(20)
        super().__init__(self)

    def run(self, app: Client, before_start_callable: Callable = None):
        self._app = app
        try:
            self._app.start()
            self._my_id = self._app.get_me()['id'] # noqa
            if before_start_callable is not None:
                # noinspection PyBroadException
                try:
                    result = before_start_callable(self._my_id)
                    if isinstance(result, bool):
                        if not result:
                            return
                except Exception:
                    pass
            ListenerKick(self._app, self, self._my_id)
            self._spawn_process(
                self._run_js,
                (
                    f'{__file__.replace("pytgcalls.py", "")}js/core.js',
                    f'port={self._port}'
                )
            )
        except KeyboardInterrupt:
            pass
        self._start_web_app()
        self.is_running = True
        return self

    def _add_handler(self, type_event: str, func):
        self._on_event_update[type_event].append(func)
