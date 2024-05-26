import 'dart:async';

import 'package:flutter/material.dart';

class OtpTimer extends StatefulWidget {
  final int timerMaxSeconds;
  final Function onTimerStop;
  const OtpTimer(
      {super.key, required this.timerMaxSeconds, required this.onTimerStop});

  @override
  _OtpTimerState createState() => _OtpTimerState();
}

class _OtpTimerState extends State<OtpTimer>
    with SingleTickerProviderStateMixin {
  final interval = const Duration(seconds: 1);
  late AnimationController _animationController;
  int currentSeconds = 0;

  @override
  void initState() {
    _animationController =
        AnimationController(vsync: this, duration: const Duration(seconds: 1));
    _animationController.repeat(reverse: true);
    startTimeout();
    super.initState();
  }

  String get timerText =>
      '${((widget.timerMaxSeconds - currentSeconds) ~/ 60).toString().padLeft(2, '0')}: ${((widget.timerMaxSeconds - currentSeconds) % 60).toString().padLeft(2, '0')}';

  startTimeout() {
    var duration = interval;
    Timer.periodic(duration, (timer) {
      setState(() {
        currentSeconds = timer.tick;
        if (timer.tick >= widget.timerMaxSeconds) {
          timer.cancel();
          _animationController.stop();
          widget.onTimerStop();
        }
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.end,
      crossAxisAlignment: CrossAxisAlignment.center,
      mainAxisSize: MainAxisSize.min,
      children: <Widget>[
        FadeTransition(
            opacity: _animationController,
            child: const Icon(
              Icons.circle,
              color: Colors.red,
              size: 12,
            )),
        const SizedBox(
          width: 5,
        ),
        Text(timerText)
      ],
    );
  }
}
