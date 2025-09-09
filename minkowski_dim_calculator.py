# -*- coding: utf-8 -*-
"""
Minkowski Dimension Calculator: QGIS Plugin

https://github.com/eduard-kazakov/minkowskiDimCalculator

Eduard Kazakov | ee.kazakov@gmail.com
"""

import os
import sys
import inspect

from qgis.core import QgsApplication
from .minkowski_dim_calculator_provider import MinkowskiDimCalculatorProvider

cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]

if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

class MinkowskiDimCalculatorPlugin(object):

    def __init__(self):
        self.provider = None

    def initProcessing(self):
        self.provider = MinkowskiDimCalculatorProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def initGui(self):
        self.initProcessing()

    def unload(self):
        QgsApplication.processingRegistry().removeProvider(self.provider)
