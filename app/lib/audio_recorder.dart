import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'dart:math';

import 'package:auth_app/microphone.dart';
import 'package:auth_app/service/timer.dart';
import 'package:auth_app/widget/button.dart';
import 'package:auth_app/widget/timer.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:record/record.dart';
import 'package:http/http.dart' as http;
import 'package:auth_app/widget/audio_recorder_web.dart';

class RecorderAuth extends StatefulWidget {
  final String text;
  final String token;
  final int timer;
  const RecorderAuth(
      {super.key,
      required this.text,
      required this.token,
      required this.timer});

  @override
  State<RecorderAuth> createState() => _RecorderAuthState();
}

class _RecorderAuthState extends State<RecorderAuth> with AudioRecorderMixin {
  late String path;
  final String apiUrl = 'http://127.0.0.1:8000/api/v1/transcribe';
  final String apiUpdateUrl = 'http://127.0.0.1:8000/api/v1/update-session';
  bool success = false;
  bool error = false;
  String code = "";
  String? text;
  int? timerMaxSeconds;
  @override
  void initState() {
    timerMaxSeconds = widget.timer;
    text = widget.text;
    super.initState();
  }

  onStop(String path) async {
    final http.Response responseFile = await http.get(Uri.parse(path));

    final request = http.MultipartRequest('POST', Uri.parse(apiUrl))
      ..files.add(
        http.MultipartFile.fromBytes(
          'file',
          responseFile.bodyBytes,
          filename: 'audio.wav',
        ),
      )
      ..headers.addAll({
        "Authorization": "Bearer ${widget.token}",
      });

    final response = await request.send();
    var streamedResponse = await http.Response.fromStream(response);
    if (response.statusCode == 200) {
      var resBody = jsonDecode(streamedResponse.body);
      code = resBody['code'];
      setState(() {
        success = true;
      });
    } else if (response.statusCode != 500) {
      setState(() {
        error = true;
      });
    }
  }

  void reset() async {
    final response = await http.post(
      Uri.parse(apiUpdateUrl),
      headers: <String, String>{
        'Content-Type': 'application/json; charset=UTF-8',
        "Authorization": "Bearer ${widget.token}",
      },
    );

    if (response.statusCode == 200) {
      final responseData = jsonDecode(response.body);
      setState(() {
        text = responseData["text"];
        timerMaxSeconds = responseData["duration"];
      });
    } else {}
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        appBar: PreferredSize(
          preferredSize: const Size(24, 100),
          child: Text(
            'Voice Auth',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 60,
              color: Colors.teal,
              fontWeight: FontWeight.bold,
              fontStyle: FontStyle.italic,
              letterSpacing: 2,
              shadows: [
                Shadow(
                  color: Colors.teal.shade200,
                  blurRadius: 11,
                )
              ],
            ),
          ),
        ),
        body: Center(
          child: SizedBox(
            width: 500,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.start,
              children: <Widget>[
                const SizedBox(
                  height: 100,
                ),
                if (!success) ...[
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      OtpTimer(
                        key: Key(timerMaxSeconds.toString()),
                        timerMaxSeconds: timerMaxSeconds!,
                        onTimerStop: reset,
                      ),
                      Row(
                        children: [
                          const Text("Other phrase"),
                          IconButton(
                              onPressed: reset,
                              icon: const Icon(Icons.replay_outlined)),
                        ],
                      ),
                    ],
                  ),
                  const SizedBox(
                    height: 16,
                  ),
                  Container(
                    width: 500,
                    height: 100,
                    padding: const EdgeInsets.all(15),
                    decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(15),
                        border: Border.all(color: Colors.teal)),
                    child: Text(
                      text!,
                      style: const TextStyle(
                        fontSize: 15,
                        color: Colors.black,
                      ),
                    ),
                  ),
                  const SizedBox(
                    height: 100,
                  ),
                  Center(
                    child: Microphone(
                      onStop: onStop,
                    ),
                  ),
                ] else if (success) ...[
                  Center(
                    child: Column(
                      children: [
                        Container(
                            width: 150,
                            height: 150,
                            decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                color: Colors.teal.shade700),
                            child: Icon(
                              Icons.check_circle_outline_outlined,
                              size: 150 / 2,
                              color: Colors.white.withOpacity(1),
                            )),
                        const SizedBox(
                          height: 32,
                        ),
                        Text(
                          code,
                          style:
                              const TextStyle(color: Colors.teal, fontSize: 25),
                        )
                      ],
                    ),
                  ),
                ] else if (error) ...[
                  Center(
                    child: Column(
                      children: [
                        Container(
                            width: 150,
                            height: 150,
                            decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                color: Colors.red.shade700),
                            child: Icon(
                              Icons.replay_outlined,
                              size: 150 / 2,
                              color: Colors.white.withOpacity(1),
                            )),
                        const SizedBox(
                          height: 32,
                        ),
                        TextButton(
                          onPressed: () {
                            setState(() {
                              error = false;
                            });
                          },
                          child: const Text(
                            "Try again",
                            style: TextStyle(color: Colors.teal, fontSize: 25),
                          ),
                        ),
                      ],
                    ),
                  ),
                ]
              ],
            ),
          ),
        ),
      ),
    );
  }
}
