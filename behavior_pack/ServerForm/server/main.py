# -*- coding: utf-8 -*-

import mod.server.extraServerApi as serverApi
import ServerForm.modConfig as modConfig
ServerSystem = serverApi.GetServerSystemCls()


class Main(ServerSystem):
    def __init__(self, namespace, systemName):
        ServerSystem.__init__(self, namespace, systemName)

        self.types = {
            "full": ("Button", "ButtonWithImage", "Text", "HorizontalRule"),
            "callback": ("Button", "ButtonWithImage")
        }
        self.callback_keys = ("instance", "callback", "args", "kwargs")

        self.loaded_ui_players = []
        self.callback_list = dict()

        self.ListenForEvent(modConfig.Namespace.client, modConfig.SystemName.client, "UiInitFinished", self, self.UiInitFinished)
        self.ListenForEvent(modConfig.Namespace.engine, modConfig.SystemName.engine, "DelServerPlayerEvent", self, self.DelServerPlayerEvent)
        self.ListenForEvent(modConfig.Namespace.client, modConfig.SystemName.client, "DoCallback", self, self.DoCallback)
        self.BroadcastEvent("ServerFormLoaded", {"instance": self})

    def UiInitFinished(self, _event_data):
        self.loaded_ui_players.append(_event_data["playerId"])
        self.BroadcastEvent("ServerFormLoaded", {"instance": self})

    def DelServerPlayerEvent(self, _event_data):
        player_id = _event_data["id"]
        if player_id in self.callback_list:
            del self.callback_list[player_id]
        if player_id in self.loaded_ui_players:
            self.loaded_ui_players.remove(player_id)

    def DoCallback(self, _event_data):
        player_id = _event_data["playerId"]
        index = _event_data["index"]
        if index in self.callback_list[player_id]:
            function_info = self.callback_list[player_id][index]
            function_info["callback"](player_id, *function_info["args"], **function_info["kwargs"])

    def FilterDatas(self, _datas):
        length = len(_datas)
        if length <= 0:
            return None

        real_index = 0
        filtering_datas = []
        callbacks = dict()
        full_types = self.types["full"]
        callback_types = self.types["callback"]
        callback_keys = self.callback_keys
        for index in range(0, length):
            raw_data = _datas[index]
            if ("type" not in raw_data) or (raw_data["type"] not in full_types):
                continue
            type = raw_data["type"]

            str_index = str(index)
            filtering_datas.append(dict())
            data = filtering_datas[real_index]
            data["index"] = str_index
            for key in raw_data:
                if key in callback_keys:
                    continue
                data[key] = raw_data[key]

            if type in callback_types:
                callbacks[str_index] = dict()
                callback = callbacks[str_index]
                for key in callback_keys:
                    if key in raw_data:
                        callback[key] = raw_data[key]
                    elif key == "instance" or key == "callback":
                        break
                    elif key == "args":
                        callback[key] = []
                    elif key == "kwargs":
                        callback[key] = dict()
            real_index += 1
        return filtering_datas, callbacks

    def SendUI(self, _player_id, _datas):
        filtering_datas = self.FilterDatas(_datas)
        if not filtering_datas:
            return False
        datas, callbacks = filtering_datas
        self.callback_list[_player_id] = callbacks
        self.NotifyToClient(_player_id, "GenerateUI", {"datas": datas})
        return True
