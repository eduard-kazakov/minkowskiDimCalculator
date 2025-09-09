# -*- coding: utf-8 -*-
"""
Minkowski Dimension Calculator: QGIS Plugin

https://github.com/eduard-kazakov/minkowskiDimCalculator

Eduard Kazakov | ee.kazakov@gmail.com
"""

from qgis.core import QgsProcessingProvider
from qgis.PyQt.QtGui import QIcon
from .minkowski_dim_calculator_algorithm import MinkowskiDimCalculatorAlgorithm
import os

class MinkowskiDimCalculatorProvider(QgsProcessingProvider):

    def __init__(self):
        QgsProcessingProvider.__init__(self)

    def unload(self):
        pass

    def loadAlgorithms(self):
        self.addAlgorithm(MinkowskiDimCalculatorAlgorithm())

    def id(self):
        return 'minkowski_dim_calculator_provider'

    def name(self):
        return 'Minkowski dimension calculator'

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(__file__), 'icon.png'))

    def longName(self):
        return 'Minkowski dimension calculator'
