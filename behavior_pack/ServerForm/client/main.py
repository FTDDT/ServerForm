# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi
import ServerForm.modConfig as modConfig
ClientSystem = clientApi.GetClientSystemCls()

screen_node = None
local_player_id = clientApi.GetLocalPlayerId()
engine_comp = clientApi.GetEngineCompFactory()
game_comp = engine_comp.CreateGame(local_player_id)


class Main(ClientSystem):
    def __init__(self, namespace, system_name):
        ClientSystem.__init__(self, namespace, system_name)

        self.mouse_scroll_speed = 15
        self.ListenForEvent(modConfig.Namespace.engine, modConfig.SystemName.engine, "UiInitFinished", self, self.UiInitFinished)
        self.ListenForEvent(modConfig.Namespace.engine, modConfig.SystemName.engine, "OnScriptTickClient", self, self.OnScriptTickClient)
        self.ListenForEvent(modConfig.Namespace.engine, modConfig.SystemName.engine, "MouseWheelClientEvent", self, self.MouseWheelClientEvent)
        self.ListenForEvent(modConfig.Namespace.engine, modConfig.SystemName.engine, "OnKeyPressInGame", self, self.OnKeyPressInGame)
        self.ListenForEvent(modConfig.Namespace.server, modConfig.SystemName.server, "GenerateUI", self, self.GenerateUI)
        self.BroadcastEvent("ServerFormLoaded", {"instance": self})

    def UiInitFinished(self, _event_data):
        global screen_node
        clientApi.RegisterUI(modConfig.UI.namespace, modConfig.UI.key, modConfig.UI.classPath, modConfig.UI.jsonPath)
        screen_node = clientApi.CreateUI(modConfig.UI.namespace, modConfig.UI.key, modConfig.UI.createParams)
        screen_node.Initialize(self)

        self.NotifyToServer("UiInitFinished", {"playerId": local_player_id})
        self.UnListenForEvent(modConfig.Namespace.engine, modConfig.SystemName.engine, "UiInitFinished", self, self.UiInitFinished)

    def OnScriptTickClient(self):
        self.UpdateContentsPosition()

    def MouseWheelClientEvent(self, _event_data):
        self.MayScrollServerForm(_event_data["direction"])

    def OnKeyPressInGame(self, _event_data):
        self.MayCloseServerForm(_event_data)

    def GenerateUI(self, _event_data):
        if screen_node:
            if screen_node.IsOpening():
                screen_node.ClearAndCloseServerForm()
            screen_node.OpenServerForm()
            screen_node.GenerateUI(_event_data["datas"])

    def CallbackProcessor(self, _event_data):
        screen_node.ClearAndCloseServerForm()

        button_path = _event_data["ButtonPath"]
        index = button_path.split("/")[-2]
        self.NotifyToServer("DoCallback", {"playerId": local_player_id, "index": index})

    def UpdateContentsPosition(self):
        if self.GetScreenNodeIsOpening():
            screen_node.UpdateContentsPosition()
        
    def GetScreenNodeIsOpening(self):
        return screen_node and screen_node.IsOpening()

    def MayScrollServerForm(self, direction):
        if self.GetScreenNodeIsOpening():
            if direction == 0:
                delta_y = -self.mouse_wheel_speed
            if direction == 1:
                delta_y = -self.mouse_wheel_speed
            contents = screen_node.GetControls()["/Contents"]
            offset = contents.GetOffsetDelta()
            contents.SetOffsetDelta((offset[0], offset[1] + delta_y))
            self.UpdateContentsPosition()

    def MayCloseServerForm(self, _datas):
        if self.GetScreenNodeIsOpening() and _datas["screenName"] == "hud_screen":
            if _datas["key"] == "27" and _datas["isDown"] == "1":
                screen_node.ClearAndCloseServerForm()
