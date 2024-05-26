import 'dart:async';
import 'dart:convert';
import 'dart:math';

import 'package:auth_app/audio_recorder.dart';
import 'package:auth_app/microphone.dart';
import 'package:auth_app/new.dart';
import 'package:auth_app/widget/button.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class Auth extends StatefulWidget {
  const Auth({super.key});

  @override
  _AuthState createState() => _AuthState();
}

class _AuthState extends State<Auth> {
  final String apiUrl = 'http://127.0.0.1:8000/api/v1/auth';
  final TextEditingController nameController = TextEditingController();
  String? errorText;
  String result = '';

  @override
  void dispose() {
    nameController.dispose();
    super.dispose();
  }

  Future<void> _postData() async {
    if (nameController.text == "") {
      setState(() {
        errorText = "Enter name";
      });
      return;
    }

    try {
      final response = await http.post(
        Uri.parse(apiUrl),
        headers: <String, String>{
          'Content-Type': 'application/json; charset=UTF-8',
        },
        body: jsonEncode(<String, dynamic>{
          'username': nameController.text,
        }),
      );

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => RecorderAuth(
              text: responseData["text"],
              token: responseData["token"],
              timer: responseData["duration"],
            ),
          ),
        );
      } else if (response.statusCode == 401) {
        setState(() {
          errorText = "Enter correct name";
        });
      }
    } catch (e) {
      setState(() {
        result = 'Error: $e';
      });
    }
  }

  Future<void> _newAuth() async {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => const New(),
      ),
    );
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
              children: <Widget>[
                const SizedBox(height: 100),
                Padding(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 8, vertical: 16),
                  child: TextFormField(
                    onChanged: (_) {
                      setState(() {
                        errorText = null;
                      });
                    },
                    controller: nameController,
                    decoration: InputDecoration(
                        border: const UnderlineInputBorder(
                            borderSide: BorderSide(color: Colors.teal)),
                        labelText: 'Enter your username',
                        labelStyle: TextStyle(color: Colors.teal.shade900),
                        errorText: errorText),
                  ),
                ),
                Row(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    TextButton(
                      onPressed: _newAuth,
                      style: OutlinedButton.styleFrom(
                        foregroundColor: Colors.teal,
                      ),
                      child: const Padding(
                        padding: EdgeInsets.all(8.0),
                        child: Row(
                          mainAxisSize: MainAxisSize.max,
                          children: [
                            Text('New'),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(
                  height: 48,
                ),
                Center(
                    child: OutlinedButton(
                  onPressed: _postData,
                  style: OutlinedButton.styleFrom(
                    foregroundColor: Colors.teal,
                    side: const BorderSide(
                      color: Colors.teal,
                    ),
                  ),
                  child: const Padding(
                    padding: EdgeInsets.all(16.0),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      mainAxisSize: MainAxisSize.max,
                      children: [
                        Text("Next Step"),
                        SizedBox(
                          width: 16,
                        ),
                        Icon(Icons.mic),
                      ],
                    ),
                  ),
                )),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
