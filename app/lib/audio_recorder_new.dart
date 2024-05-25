import 'dart:async';
import 'dart:io';

import 'package:auth_app/microphone.dart';
import 'package:auth_app/widget/button.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:record/record.dart';
import 'package:http/http.dart' as http;
import 'package:auth_app/widget/audio_recorder_web.dart';

class RecorderNew extends StatefulWidget {
  final String text;
  final String token;

  const RecorderNew({super.key, required this.text, required this.token});

  @override
  State<RecorderNew> createState() => _RecorderNewState();
}

class _RecorderNewState extends State<RecorderNew> with AudioRecorderMixin {
  late String path;
  final String apiUrl = 'http://127.0.0.1:8000/api/v1/register';
  bool success = false;
  bool error = false;
  @override
  void initState() {
    super.initState();
  }

  onStop(String path) async {
    final http.Response responseData = await http.get(Uri.parse(path));

    final request = http.MultipartRequest('POST', Uri.parse(apiUrl))
      ..files.add(
        http.MultipartFile.fromBytes(
          'file',
          responseData.bodyBytes,
          filename: 'audio.wav', // You may need to adjust the file extension
        ),
      )
      ..headers.addAll({
        "Authorization": "Bearer ${widget.token}",
      });

    final response = await request.send();
    if (response.statusCode == 200) {
      setState(() {
        success = true;
      });
    } else if (response.statusCode > 500) {
      setState(() {
        error = true;
      });
    }
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
                    const Text(
                      "We need fragment of your voice",
                      style: TextStyle(
                        fontSize: 15,
                        color: Colors.black,
                      ),
                    ),
                    Container(
                      width: 500,
                      height: 100,
                      padding: const EdgeInsets.all(15),
                      decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(15),
                          border: Border.all(color: Colors.teal)),
                      child: Text(
                        widget.text,
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
                  ] else if (error) ...[
                    Container(
                        width: 150,
                        height: 150,
                        decoration: BoxDecoration(
                            shape: BoxShape.circle, color: Colors.red.shade700),
                        child: Icon(
                          Icons.replay_outlined,
                          size: 150 / 2,
                          color: Colors.white.withOpacity(1),
                        )),
                  ]
                ],
              ),
            ),
          )),
    );
  }
}
