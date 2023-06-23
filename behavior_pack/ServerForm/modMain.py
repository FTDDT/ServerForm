# -*- coding: utf-8 -*-

from mod.common.mod import Mod
import mod.client.extraClientApi as clientApi
import mod.server.extraServerApi as serverApi
import ServerForm.modConfig as modConfig


@Mod.Binding(name="ServerForm", version="0.0.1")
class Main(object):

    def __init__(self):
        pass

    @Mod.InitServer()
    def ServerInit(self):
        serverApi.RegisterSystem(modConfig.Namespace.server, modConfig.SystemName.server, modConfig.ClassPath.server)
        pass

    @Mod.DestroyServer()
    def ServerDestroy(self):
        pass

    @Mod.InitClient()
    def ClientInit(self):
        clientApi.RegisterSystem(modConfig.Namespace.client, modConfig.SystemName.client, modConfig.ClassPath.client)
        pass

    @Mod.DestroyClient()
    def ClientDestroy(self):
        pass
