#!/usr/bin/python
# -*- coding: utf-8 -*-
import BigWorld
import items.vehicles
import os
import json
import random
import time
from Account import Account
from gui import g_tankActiveCamouflage
from gui.ClientHangarSpace import ClientHangarSpace
from VehicleAppearance import VehicleAppearance
from xml.dom import minidom
from debug_utils import *

class Wotrc(object):

    def __init__(self):
        path_items = minidom.parse(os.path.join(os.getcwd(), 'paths.xml')).getElementsByTagName('Path')
        for root in path_items:
            path = os.path.join(os.getcwd(), root.childNodes[0].data)
            if os.path.isdir(path):
                conf_file = os.path.join(path, 'scripts', 'client', 'mods', 'wotrc.json')
                if os.path.isfile(conf_file):
                    with open(conf_file) as data_file:
                        jsConfig = json.load(data_file)
                        break
        self.remap = jsConfig.get('remap', {})
        self.hangarCamo = {}

old_onBecomeNonPlayer = Account.onBecomeNonPlayer

def new_onBecomeNonPlayer(self):
    old_onBecomeNonPlayer(self)
    wotrc.hangarCamo.clear()

Account.onBecomeNonPlayer = new_onBecomeNonPlayer

old_va_getCamouflageParams = VehicleAppearance._VehicleAppearance__getCamouflageParams

def new_va_getCamouflageParams(self, vehicle):
    result = old_va_getCamouflageParams(self, vehicle)
    if result[0] is not None:
        return result
    arenaType = BigWorld.player().arena.arenaType
    camouflageKind = arenaType.vehicleCamouflageKind
    vDesc = vehicle.typeDescriptor
    customization = items.vehicles.g_cache.customization(vDesc.type.customizationNationID)
    camouflages = []
    for key in customization['camouflages']:
        camuflage = customization['camouflages'][key]
        kind = wotrc.remap.get(camuflage['texture'], camuflage['kind'])
        if kind == camouflageKind:
            camouflages.append(key)
    camouflages.append(None)
    camouflageId = vehicle.id % len(camouflages)
    return (camouflages[camouflageId], int(time.time()), 7)

VehicleAppearance._VehicleAppearance__getCamouflageParams = new_va_getCamouflageParams

old_cs_recreateVehicle = ClientHangarSpace.recreateVehicle

def new_cs_recreateVehicle(self, vDesc, vState, onVehicleLoadedCallback = None):
    if wotrc.hangarCamo.has_key(vDesc.type.compactDescr):
        vDesc.camouflages = wotrc.hangarCamo[vDesc.type.compactDescr]
    else:
        customization = items.vehicles.g_cache.customization(vDesc.type.customizationNationID)
        camouflages = customization['camouflages'].keys()
        camouflages.append(None)
        tmpCamouflages = []
        for i in range(0, 3):
            if vDesc.camouflages[i][0] is not None:
                tmpCamouflages.append(vDesc.camouflages[i])
            else:
                tmpCamouflages.append((random.choice(camouflages), int(time.time()), 7))
        vDesc.camouflages = tuple(tmpCamouflages)
        wotrc.hangarCamo[vDesc.type.compactDescr] = tuple(tmpCamouflages)
    old_cs_recreateVehicle(self, vDesc, vState, onVehicleLoadedCallback)

ClientHangarSpace.recreateVehicle = new_cs_recreateVehicle

wotrc = Wotrc()
