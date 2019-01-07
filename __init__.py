# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MinkowskiDimCalculator
                                 A QGIS plugin
 Minkowski fractal dimension calculation for vector layer features

                              -------------------
        begin                : 2019-01-01
        copyright            : (C) 2019 by Eduard Kazakov
        email                : silenteddie@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load MinkowskiDimCalculator class from file MinkowskiDimCalculator.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .minkowskiDimCalculator import MinkowskiDimCalculator
    return MinkowskiDimCalculator(iface)
