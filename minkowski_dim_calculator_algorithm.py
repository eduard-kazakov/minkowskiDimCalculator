# -*- coding: utf-8 -*-
"""
Minkowski Dimension Calculator: QGIS Plugin

https://github.com/eduard-kazakov/minkowskiDimCalculator

Eduard Kazakov | ee.kazakov@gmail.com
"""

import math
import os
import random
from qgis.PyQt.QtCore import QMetaType
from qgis.PyQt.QtGui import QIcon
from qgis.core import (
    QgsFeature,
    QgsFeatureSink,
    QgsField,
    QgsFields,
    QgsGeometry,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterNumber,
    QgsProcessingParameterDefinition,
    QgsProcessingParameterString
)

class MinkowskiDimCalculatorAlgorithm(QgsProcessingAlgorithm):
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    
    K_SCALES = "K_SCALES"
    N_OFFSETS = "N_OFFSETS"
    DENSIFY_FACTOR = "DENSIFY_FACTOR"
    
    DIM_FIELD = "DIM_FIELD"
    R2_FIELD = "R2_FIELD"

    R2_WARNING_THRESHOLD = 0.85

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                "Input linear layer",
                [QgsProcessing.TypeVectorLine],
            )
        )
        
        # Advanced: number of scales
        p_k = QgsProcessingParameterNumber(
            self.K_SCALES,
            "Number of scales (K)",
            type=QgsProcessingParameterNumber.Integer,
            defaultValue=8,
            minValue=3,
            maxValue=20,
            optional=True,
        )
        p_k.setFlags(p_k.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(p_k)

        # Advanced: number of offsets per scale
        p_no = QgsProcessingParameterNumber(
            self.N_OFFSETS,
            "Grid offsets per scale",
            type=QgsProcessingParameterNumber.Integer,
            defaultValue=3,
            minValue=1,
            maxValue=10,
            optional=True,
        )
        p_no.setFlags(p_no.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(p_no)
        
        # Advanced: densification factor
        p_df = QgsProcessingParameterNumber(
            self.DENSIFY_FACTOR,
            "Vertices densification factor",
            type=QgsProcessingParameterNumber.Double,
            defaultValue=0.5,
            minValue=0.0,   # 0 = no densification
            maxValue=2.0,
            optional=True,
        )
        p_df.setFlags(p_df.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(p_df)
        
        # Advanced: field names
        p_fd = QgsProcessingParameterString(
            self.DIM_FIELD,
            "Output field for dimension",
            defaultValue="mink_dim",
            optional=True,
        )
        p_fd.setFlags(p_fd.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(p_fd)

        p_r2 = QgsProcessingParameterString(
            self.R2_FIELD,
            "Output field for R²",
            defaultValue="mink_r2",
            optional=True,
        )
        p_r2.setFlags(p_r2.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(p_r2)
        
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                "Minkowski dimension added",
            )
        )

    @staticmethod
    def _logspace_descending(s_max, s_min, k):
        if k == 1:
            return [s_min]
        r = (s_min / float(s_max)) ** (1.0 / (k - 1))
        vals = [s_max * (r ** i) for i in range(k)]
        vals[-1] = s_min
        return vals

    @staticmethod
    def _count_boxes_by_vertices(geom: QgsGeometry, s: float, shift_x: float, shift_y: float, densify_factor: float) -> int:
        """Vertex-based cover; optional densification with max segment length ~ s * densify_factor."""
        if geom.isEmpty():
            return 0

        # Densify unless factor == 0
        if densify_factor and densify_factor > 0.0:
            try:
                g = geom.densifyByDistance(max(1e-12, s * densify_factor))
            except Exception:
                g = geom
        else:
            g = geom

        seen = set()
        it = g.vertices()
        try:
            while True:
                pt = next(it)
                ix = math.floor((pt.x() - shift_x) / s)
                iy = math.floor((pt.y() - shift_y) / s)
                seen.add((ix, iy))
        except StopIteration:
            pass
        return len(seen)

    @staticmethod
    def _ols_slope_r2(xs, ys):
        n = len(xs)
        if n < 2:
            return float("nan"), float("nan")
        mx = sum(xs)/n
        my = sum(ys)/n
        num = sum((x-mx)*(y-my) for x,y in zip(xs,ys))
        den = sum((x-mx)**2 for x in xs)
        if den == 0:
            return float("nan"), float("nan")
        b = num/den
        a = my - b*mx
        ss_tot = sum((y-my)**2 for y in ys)
        ss_res = sum((y-(a+b*x))**2 for x,y in zip(xs,ys))
        r2 = 1.0 - (ss_res/ss_tot if ss_tot != 0 else float("nan"))
        return b, r2

    @staticmethod
    def _vertex_count(geom: QgsGeometry) -> int:
        c = 0
        it = geom.vertices()
        try:
            while True:
                next(it)
                c += 1
        except StopIteration:
            pass
        return c
    
    def processAlgorithm(self, parameters, context, feedback):
        src = self.parameterAsSource(parameters, self.INPUT, context)
        if src is None:
            raise QgsProcessingException("Invalid input layer")
            
        K_SCALES = int(self.parameterAsInt(parameters, self.K_SCALES, context) or 8)
        N_OFFSETS = int(self.parameterAsInt(parameters, self.N_OFFSETS, context) or 3)
        DF = float(self.parameterAsDouble(parameters, self.DENSIFY_FACTOR, context) or 0.5)
        
        dim_name_in = self.parameterAsString(parameters, self.DIM_FIELD, context) or "mink_dim"
        r2_name_in = self.parameterAsString(parameters, self.R2_FIELD, context) or "mink_r2"

        out_fields = QgsFields(src.fields())
        out_fields.append(QgsField(dim_name_in, QMetaType.Type.Double))
        out_fields.append(QgsField(r2_name_in, QMetaType.Type.Double))

        sink, dest = self.parameterAsSink(
            parameters, self.OUTPUT, context,
            out_fields, src.wkbType(), src.sourceCrs()
        )
        if sink is None:
            raise QgsProcessingException("Failed to create output sink.")

        total = src.featureCount() if src.featureCount() >= 0 else 0
        processed = 0

        K_SCALES = max(2, K_SCALES)     # at least 2 points for a slope
        N_OFFSETS = max(1, N_OFFSETS)
        DF = max(0.0, DF) # allow 0 to disable densification

        for f in src.getFeatures():
            if feedback.isCanceled():
                break

            feedback.setProgressText('Processing feature %s' % f.id())

            geom = f.geometry()
            fd = float("nan")
            r2 = float("nan")

            if geom and not geom.isEmpty():
                try:
                    env = geom.boundingBox()
                    w, h = env.width(), env.height()
                    diag = math.hypot(w, h)

                    length = geom.length()
                    vcount = max(1, self._vertex_count(geom))
                    seg = length / vcount if vcount > 0 else max(w, h)

                    s_max = max(1e-9, 0.5 * max(1e-12, min(w, h) if (w > 0 and h > 0) else diag/2.0))

                    s_min_by_span = s_max / (2 ** (K_SCALES - 1))
                    s_min_by_seg  = max(1e-9, seg / 3.0)
                    s_floor       = max(1e-9, s_max * 1e-3)
                    s_min = max(s_min_by_span, s_min_by_seg, s_floor)
                    if s_min >= s_max:
                        s_min = s_max / 8.0

                    sizes = self._logspace_descending(s_max, s_min, K_SCALES)

                    rng = random.Random(int(f.id()) & 0xFFFFFFFF)

                    log_inv_s, log_N = [], []
                    for s in sizes:
                        counts = []
                        for _ in range(N_OFFSETS):
                            dx = rng.uniform(0.0, s)
                            dy = rng.uniform(0.0, s)
                            counts.append(self._count_boxes_by_vertices(geom, s, dx, dy, DF))
                        Nk = max(1, min(counts))
                        log_inv_s.append(math.log(1.0 / s))
                        log_N.append(math.log(float(Nk)))

                    slope, r2 = self._ols_slope_r2(log_inv_s, log_N)
                    if r2 < self.R2_WARNING_THRESHOLD:
                        feedback.pushWarning('r2 value for this feature is below quality threshold (0.85). Please be aware using calculcated fractal dimension for it')
                        
                    fd = float(slope) if math.isfinite(slope) else float("nan")

                except Exception as e:
                    feedback.setProgressText('Feature %s skipped due to processing error (%s)' % (f.id(), str(e)))

            newf = QgsFeature(out_fields)
            newf.setGeometry(geom)
            attrs = f.attributes()
            attrs.append(fd if math.isfinite(fd) else None)
            attrs.append(r2 if math.isfinite(r2) else None)
            newf.setAttributes(attrs)
            sink.addFeature(newf, QgsFeatureSink.FastInsert)

            processed += 1

            if total:
                feedback.setProgress(int(100.0 * processed / total))

        return {self.OUTPUT: dest}
    
    def name(self):
        return "minkowski_dimension_calculator"
    
    def displayName(self):
        return "Minkowski Dimension Calculator"
    
    def shortHelpString(self):
        return (
            "Automatically estimates the Minkowski fractal dimension for each feature (also known as Minkowski–Bouligand dimension, box-counting dimension).\n"
            "Input is linear vector layer. Use built-in QGIS tool \"Polygons to lines\" to prepare polygon layers to be used in plugin.\n"
            "Algorithm:\n"
            "  • Builds a per-feature geometric ladder of box sizes from the feature’s extent and typical segment length.\n"
            "  • For each size, samples several random grid offsets and takes the minimal cover.\n"
            "  • Densifies vertices with max segment length = s * DENSIFY_FACTOR (0 disables densification).\n"
            "  • Fits log N(s) vs log(1/s) by OLS; slope is the dimension.\n\n"
            "Fields added (configurable names in Advanced):\n"
            "  • mink_dim   – estimated dimension\n"
            "  • mink_r2    – R² of the linear fit. Values below 0.85 should be considered as very unconfident\n\n"
            "Advanced parameters:\n"
            "  • Number of scales (K): more points along the log–log line (8–12 typical).\n"
            "  • Grid offsets per scale: mitigates grid alignment bias (3–5 typical).\n"
            "  • Densification factor: controls vertex insertion density at each scale; 0.5 is a good default."
        )
    
    def icon(self):
        return QIcon(os.path.join(os.path.dirname(__file__), 'icon.png'))

    def createInstance(self):
        return MinkowskiDimCalculatorAlgorithm()
