# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi

ViewBinder = clientApi.GetViewBinderCls()
ViewRequest = clientApi.GetViewViewRequestCls()
ScreenNode = clientApi.GetScreenNodeCls()

engine_comp = clientApi.GetEngineCompFactory()
game_comp = engine_comp.CreateGame(clientApi.GetLevelId())


class Main(ScreenNode):
    def __init__(self, namespace, name, param):
        ScreenNode.__init__(self, namespace, name, param)

        self._client = None
        self._is_opening = None
        self._controls = dict()
        self.default_text = ""
        self.default_image_path = "/textures/misc/missing_texture"

    def Initialize(self, client):
        self._client = client
        self._is_opening = True

        self._controls["/Background"] = self.GetBaseUIControl("/Background")
        self._controls["/Contents"] = self.GetBaseUIControl("/Contents").asInputPanel()

        self.ClearAndCloseServerForm()

    def IsOpening(self):
        return self._is_opening

    def GetControls(self):
        return self._controls

    def ClearServerForm(self):
        stack_controls = self.GetChildrenName("/Contents/Stacks")
        for path in stack_controls:
            self.RemoveComponent("/Contents/Stacks/" + path, "/Contents/Stacks")

    def OpenServerForm(self):
        if not self._is_opening:
            clientApi.HideSlotBarGui(True)
            game_comp.SimulateTouchWithMouse(True)
            self.SetIsHud(0)
            self.SetScreenVisible(True)
            self._is_opening = True

    def CloseServerForm(self):
        if self._is_opening:
            clientApi.HideSlotBarGui(False)
            game_comp.SimulateTouchWithMouse(False)
            self.SetIsHud(1)
            self.SetScreenVisible(False)
            self._is_opening = False

    def ClearAndCloseServerForm(self):
        self.ClearServerForm()
        self.CloseServerForm()

    def UpdateContentsPosition(self):
        screen_size = self._controls["/Background"].GetSize()
        contents_size = self._controls["/Contents"].GetSize()
        contents_pos = self._controls["/Contents"].GetOffsetDelta()

        upward_limit = 0
        downward_limit = screen_size[1] - contents_size[1]

        if downward_limit > upward_limit:
            downward_limit = upward_limit

        if contents_pos[1] > upward_limit:
            self._controls["/Contents"].SetOffsetDelta((contents_pos[0], upward_limit))
        if contents_pos[1] < downward_limit:
            self._controls["/Contents"].SetOffsetDelta((contents_pos[0], downward_limit))

    def GenerateUI(self, _datas):
        for data in _datas:
            self.GenerateControl(data)

    def GenerateControl(self, _data):
        control_type = _data["type"]
        if control_type == "Button":
            self.GenerateButton(_data)

        if control_type == "ButtonWithImage":
            self.GenerateButtonWithImage(_data)

        if control_type == "Text":
            self.GenerateText(_data)

        if control_type == "HorizontalRule":
            self.GenerateHorizontalRule(_data)

    def GenerateButton(self, _data):
        index = _data["index"]

        self.Clone("/Temp/Button", "/Contents/Stacks", index)
        button = self.GetBaseUIControl("/Contents/Stacks/" + index + "/button").asButton()
        button.AddTouchEventParams({"isSwallow": True})
        button.SetButtonTouchUpCallback(self._client.CallbackProcessor)

        if "text" in _data:
            self.GetBaseUIControl("/Contents/Stacks/" + index + "/button/text").asLabel().SetText(_data["text"])

    def GenerateButtonWithImage(self, _data):
        index = _data["index"]

        self.Clone("/Temp/ButtonWithImage", "/Contents/Stacks", index)
        button = self.GetBaseUIControl("/Contents/Stacks/" + index + "/button").asButton()
        button.AddTouchEventParams({"isSwallow": True})
        button.SetButtonTouchUpCallback(self._client.CallbackProcessor)

        if "text" in _data:
            self.GetBaseUIControl("/Contents/Stacks/" + index + "/button/text").asLabel().SetText(_data["text"])
        if "image_path" in _data:
            self.GetBaseUIControl("/Contents/Stacks/" + index + "/image").asImage().SetSprite(_data["image_path"])

    def GenerateText(self, _data):
        index = _data["index"]
        self.Clone("/Temp/Text", "/Contents/Stacks", index)
        if "left" in _data:
            self.GetBaseUIControl("/Contents/Stacks/" + index + "/left").asLabel().SetText(_data["left"])
        if "middle" in _data:
            self.GetBaseUIControl("/Contents/Stacks/" + index + "/middle").asLabel().SetText(_data["middle"])
        if "right" in _data:
            self.GetBaseUIControl("/Contents/Stacks/" + index + "/right").asLabel().SetText(_data["right"])

    def GenerateHorizontalRule(self, _data):
        index = _data["index"]
        self.Clone("/Temp/HorizontalRule", "/Contents/Stacks", index)
