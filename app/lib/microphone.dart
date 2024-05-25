import 'dart:async';
import 'dart:io';
import 'dart:math';

import 'package:auth_app/utils.dart';
import 'package:auth_app/widget/audio_recorder_web.dart';
import 'package:auth_app/widget/button.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/widgets.dart';
import 'package:record/record.dart';

class Microphone extends StatefulWidget {
  final void Function(String path) onStop;
  const Microphone({super.key, required this.onStop});

  @override
  State<Microphone> createState() => _MicrophoneState();
}

class _MicrophoneState extends State<Microphone> with AudioRecorderMixin {
  late final AudioRecorder _audioRecorder;
  StreamSubscription<RecordState>? _recordSub;
  RecordState _recordState = RecordState.stop;
  StreamSubscription<Amplitude>? _amplitudeSub;
  Amplitude? _amplitude;
  double microphoneRadius = 60;
  Color microphoneColor = Colors.teal.withOpacity(0.8);
  IconData microphoneIcon = Icons.mic;
  bool recordReady = false;
  late String recordPath;
  @override
  void initState() {
    _audioRecorder = AudioRecorder();

    _amplitudeSub = _audioRecorder
        .onAmplitudeChanged(const Duration(milliseconds: 100))
        .listen((amp) {
      setState(() => _amplitude = amp);
    });
    _recordSub = _audioRecorder.onStateChanged().listen((recordState) {
      _updateRecordState(recordState);
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
      recordReady = true;
      recordPath = path;
    }
  }

  Future<void> _reset() async {
    await _audioRecorder.cancel();
    setState(() {
      recordReady = false;
    });
  }

  void _updateRecordState(RecordState recordState) {
    setState(() => _recordState = recordState);
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
    return Column(
      children: [
        _buildRecordStopControl(),
        const SizedBox(
          height: 50,
        ),
        if (recordReady) ...[
          Center(
            child: Button(
                text: "Send record",
                onPress: () => widget.onStop(recordPath),
                icon: Icons.send),
          ),
          const SizedBox(
            height: 16,
          ),
          Center(
            child: Button(
              text: "reset",
              onPress: () {
                setInit();
                _reset();
              },
              icon: Icons.replay_outlined,
            ),
          ),
        ],
        if (!recordReady && _recordState == RecordState.stop) ...[
          const Text(
            "Press to start record",
            style: TextStyle(
              fontSize: 24,
              color: Colors.teal,
            ),
          )
        ] else if (!recordReady && _recordState != RecordState.stop) ...[
          const Text(
            "Hold to record release to send",
            style: TextStyle(
              fontSize: 24,
              color: Colors.teal,
            ),
          ),
          const Text(
            "Drag to reset",
            style: TextStyle(
              fontSize: 24,
              color: Colors.teal,
            ),
          )
        ]
      ],
    );
  }

  @override
  void dispose() {
    _recordSub?.cancel();
    _amplitudeSub?.cancel();
    _audioRecorder.dispose();
    super.dispose();
  }

  void setInit() {
    microphoneColor = Colors.teal.withOpacity(0.8);
    microphoneIcon = Icons.mic;
  }

  void setStart() {
    if (_recordState != RecordState.stop) {
      microphoneColor = Colors.teal.withOpacity(0.8);
      microphoneIcon = Icons.stop;
    }
  }

  void setEnd() {
    if (_recordState != RecordState.stop) {
      microphoneIcon = Icons.check;
      microphoneColor = Colors.green.withOpacity(1);
    }
  }

  void setCancel() {
    if (_recordState != RecordState.stop) {
      microphoneIcon = Icons.replay_outlined;
      microphoneColor = Colors.red.withOpacity(1);
    }
  }

  Widget _buildRecordStopControl() {
    return Stack(
      alignment: AlignmentDirectional.center,
      children: [
        RepaintBoundary(
            child: CustomPaint(
          painter: ClipOvalShadowPainter(
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
            if (!(_recordState != RecordState.stop) && !recordReady) {
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
              _reset();
              setInit();
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
