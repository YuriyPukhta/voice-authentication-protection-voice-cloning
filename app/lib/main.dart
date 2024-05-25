import 'package:auth_app/audio_recorder.dart';
import 'package:auth_app/auth.dart';
import 'package:flutter/material.dart';

void main() => runApp(const MyApp());

class MyApp extends StatefulWidget {
  const MyApp({super.key});

  @override
  State<MyApp> createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  bool showPlayer = false;
  String? audioPath;

  @override
  void initState() {
    showPlayer = false;
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(home: Auth());
  }
}
/*Recorder(
            onStop: (path) {
              if (kDebugMode) print('Recorded file path: $path');
              setState(() {
                audioPath = path;
                showPlayer = true;
              });
            },


            Recorder(
        text: "5555",
        token:
            'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NmVjMTM1MS1mZWZlLTQxNzktYTQ2Ni00ODEyNzU3ZTRhOWUiLCJleHAiOjE3MTYxNDU0Mzh9.0lvUnX9u_0QBb6eStBsGBCs3Yo3083qdlLu6ugAwihw',
      ),
          ),
                  body: const Center(child: New()),
          
          */