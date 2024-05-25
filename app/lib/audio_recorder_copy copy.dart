import 'dart:async';
import 'dart:math';

import 'package:auth_app/widget/audio_recorder_web.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/widgets.dart';
import 'package:record/record.dart';

double linearScaleAmplitude(double oldValue,
    {double oldMin = -100,
    double oldMax = 1,
    double newMin = 0,
    double newMax = 50}) {
  return ((oldValue - oldMin) * (newMax - newMin)) / (oldMax - oldMin) + newMin;
}

class _ClipOvalShadowPainter extends CustomPainter {
  final Paint painter;
  final double radius;
  final bool active;

  _ClipOvalShadowPainter(
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

class Recorder extends StatefulWidget {
  final void Function(String path) onStop;

  const Recorder({super.key, required this.onStop});

  @override
  State<Recorder> createState() => _RecorderState();
}

class _RecorderState extends State<Recorder> with AudioRecorderMixin {
  late final AudioRecorder _audioRecorder;
  StreamSubscription<RecordState>? _recordSub;
  final RecordState _recordState = RecordState.stop;
  StreamSubscription<Amplitude>? _amplitudeSub;
  Amplitude? _amplitude;
  double microphoneRadius = 60;
  Color microphoneColor = Colors.teal.withOpacity(0.8);
  IconData microphoneIcon = Icons.mic;

  @override
  void initState() {
    _audioRecorder = AudioRecorder();

    _amplitudeSub = _audioRecorder
        .onAmplitudeChanged(const Duration(milliseconds: 500))
        .listen((amp) {
      setState(() => _amplitude = amp);
    });

    super.initState();
  }

  Future<void> _start() async {
    try {
      if (await _audioRecorder.hasPermission()) {
        const encoder = AudioEncoder.wav;

        if (!await _isEncoderSupported(encoder)) {
          return;
        }

        final devs = await _audioRecorder.listInputDevices();
        debugPrint(devs.toString());

        const config = RecordConfig(encoder: encoder, numChannels: 1);

        await recordFile(_audioRecorder, config);
      }
    } catch (e) {
      if (kDebugMode) {
        print(e);
      }
    }
  }

  Future<void> _stop() async {
    final path = await _audioRecorder.stop();

    if (path != null) {
      widget.onStop(path);
    }
  }

  Future<void> _pause() => _audioRecorder.pause();

  Future<void> _resume() => _audioRecorder.resume();

  Future<bool> _isEncoderSupported(AudioEncoder encoder) async {
    final isSupported = await _audioRecorder.isEncoderSupported(
      encoder,
    );

    if (!isSupported) {
      debugPrint('${encoder.name} is not supported on this platform.');
      debugPrint('Supported encoders are:');

      for (final e in AudioEncoder.values) {
        if (await _audioRecorder.isEncoderSupported(e)) {
          debugPrint('- ${encoder.name}');
        }
      }
    }

    return isSupported;
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        body: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: <Widget>[
                _buildRecordStopControl(),
              ],
            ),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _recordSub?.cancel();
    _amplitudeSub?.cancel();
    _audioRecorder.dispose();
    super.dispose();
  }

  void setStart() {
    if (_recordState != RecordState.stop) {
      microphoneColor = Colors.teal.withOpacity(0.8);
      microphoneIcon = Icons.stop;
    }
  }

  void setEnd() {
    if (_recordState != RecordState.stop) {
      microphoneIcon = Icons.mic;
      microphoneColor = Colors.teal.withOpacity(0.3);
    }
  }

  void setCancel() {
    if (_recordState != RecordState.stop) {
      microphoneIcon = Icons.replay_outlined;
      microphoneColor = Colors.red.withOpacity(1);
    }
  }

  Widget _buildRecordStopControl() {
    late Icon icon;

    if (_recordState != RecordState.stop) {
      icon = const Icon(Icons.stop, color: Colors.red, size: 30);
    } else {
      final theme = Theme.of(context);
      icon = Icon(Icons.mic, color: theme.primaryColor, size: 30);
    }

    return Stack(
      alignment: AlignmentDirectional.center,
      children: [
        RepaintBoundary(
            child: CustomPaint(
          painter: _ClipOvalShadowPainter(
            radius: _recordState != RecordState.stop && _amplitude != null
                ? linearScaleAmplitude(_amplitude!.current,
                    newMin: microphoneRadius, newMax: microphoneRadius * 1.5)
                : microphoneRadius.toDouble(),
            painter: Paint()
              ..color = microphoneColor.withOpacity(0.3)
              ..strokeWidth = 15,
            active: _recordState != RecordState.stop,
          ),
        )),
        GestureDetector(
          onTapDown: (TapDownDetails) {
            if (!(_recordState != RecordState.stop)) {
              _start();
              setStart();
            }
          },
          onTapUp: (TapDownDetails) {
            if (_recordState != RecordState.stop) {
              _stop();
              setEnd();
            }
          },
          onHorizontalDragUpdate: (details) {
            if (_recordState != RecordState.stop) {
              if (details.localPosition.distance > 100) {
                setCancel();
              }
              if (details.localPosition.distance < 100) {
                setStart();
              }
            }
          },
          onHorizontalDragEnd: (details) {
            if (_recordState != RecordState.stop) {
              _stop();
              setEnd();
            }
          },
          child: Container(
              width: microphoneRadius + microphoneRadius,
              height: microphoneRadius + microphoneRadius,
              decoration:
                  BoxDecoration(shape: BoxShape.circle, color: microphoneColor),
              child: Icon(
                microphoneIcon,
                size: microphoneRadius / 2,
                color: Colors.white.withOpacity(1),
              )),
        ),
      ],
    );
  }
}
