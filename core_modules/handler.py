import asyncio
import importlib
import json

from core_modules.get_window import get_window
from core_modules.tray import Tray
from global_modules import logs


class Handler:
    def __init__(self, tray: Tray):
        from global_modules.macro_manager import REGISTERED_PATH
        self.__REGISTERED_PATH = REGISTERED_PATH

        self.tray = tray
        self.window = get_window()

        self.actual_loaded = {}

        self.__get_registered_for_window()

    def __get_registered_for_window(self):
        with open(self.__REGISTERED_PATH, "r") as f:
            actual_json = json.loads(f.read())

        actual_loaded = {}

        if "default" in actual_json.keys():
            actual_loaded.update(actual_json["default"].items())

        for i in actual_json.keys():
            if i.lower() in self.window.lower():
                if actual_json[i] is None:
                    self.actual_loaded = {}
                    return
                else:
                    actual_loaded.update(actual_json[i].items())

        tmp = {}
        for key, value in actual_loaded.items():
            try:
                module = importlib.import_module(".".join(value.split(".")[:-1]))
                importlib.reload(module)

            except ModuleNotFoundError:
                return logs.error("handler", f"Module {'.'.join(value.split('.')[:-1])} not found")

            try:
                callback = eval(f"module.{value.split('.')[-1]}")

            except AttributeError as err:
                return logs.error("handler", f"Function {value} not found")

            tmp.update({key: callback})

        self.actual_loaded = {}
        self.actual_loaded.update(tmp)

    def update(self):
        pass  # TODO


Handler(Tray(asyncio.get_event_loop()))