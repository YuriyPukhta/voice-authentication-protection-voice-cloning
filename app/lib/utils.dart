import 'dart:math';

import 'package:flutter/material.dart';
import 'package:flutter/widgets.dart';

double linearScaleAmplitude(double oldValue,
    {double oldMin = -100,
    double oldMax = 1,
    double newMin = 0,
    double newMax = 50}) {
  return ((oldValue - oldMin) * (newMax - newMin)) / (oldMax - oldMin) + newMin;
}

class ClipOvalShadowPainter extends CustomPainter {
  final Paint painter;
  final double radius;
  final bool active;

  ClipOvalShadowPainter(
      {required this.painter, required this.radius, required this.active});

  double getShape(Random random) {
    return 1 + random.nextDouble() / 4;
  }

  @override
  void paint(Canvas canvas, Size size) {
    int n = 20;
    var rng = Random();
    var path = Path();

    double centerX = size.width / 2;
    double centerY = size.height / 2;

    if (active) {
      double thetaStart = 2 * pi * 0 / n;
      double xStart = centerX + radius * cos(thetaStart);
      double yStart = centerY + radius * sin(thetaStart);
      path.moveTo(xStart, yStart);
      for (int i = 0; i < n; i += 2) {
        final double thetaFirst = 2 * pi * i / n;
        final double xFirst =
            centerX + (getShape(rng) * radius) * cos(thetaFirst);
        final double yFirst =
            centerY + (getShape(rng) * radius) * sin(thetaFirst);
        final double thetaSecond = 2 * pi * (i + 1) / n;
        final double xSecond = centerX + radius * cos(thetaSecond);
        final double ySecond = centerY + radius * sin(thetaSecond);
        path.quadraticBezierTo(xFirst, yFirst, xSecond, ySecond);
      }
      final double thetaEnd = 2 * pi * n - 1 / n;
      final double xEnd = centerX + (getShape(rng) * radius) * cos(thetaStart);
      final double yEnd = centerY + (getShape(rng) * radius) * sin(thetaEnd);

      path.quadraticBezierTo(xEnd, yEnd, xStart, yStart);
    }

    //canvas.drawCircle(Offset(centerX, centerY), radius, painter);

    canvas.drawPath(path, painter);
  }

  @override
  bool shouldRepaint(CustomPainter oldDelegate) {
    return true;
  }
}
