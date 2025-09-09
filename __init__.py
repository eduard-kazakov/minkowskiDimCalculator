# -*- coding: utf-8 -*-
"""
Minkowski Dimension Calculator: QGIS Plugin

https://github.com/eduard-kazakov/minkowskiDimCalculator

Eduard Kazakov | ee.kazakov@gmail.com
"""

# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load MinkowskiDimCalculator class from file MinkowskiDimCalculator.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .minkowski_dim_calculator import MinkowskiDimCalculatorPlugin
    return MinkowskiDimCalculatorPlugin()
