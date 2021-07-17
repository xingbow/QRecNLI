# -*- coding: utf-8 -*-
import time
import json
import os
import sys

try:
    import globalVariable as GV
except ImportError:
    import app.dataService.globalVariable as GV

class DataService(object):
    def __init__(self):
        self.GV = GV
        print('=================================================')
        return

    def initialization(self, data):
        self.data = data
        result = {'test': 'test'}
        return result

    def test(self):
        print(self.GV.test)



if __name__ == '__main__':
    print('start')
    dataService = DataService()




