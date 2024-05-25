import 'dart:async';
import 'dart:convert';
import 'dart:math';

import 'package:auth_app/audio_recorder_new.dart';
import 'package:auth_app/microphone.dart';
import 'package:auth_app/widget/button.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class New extends StatefulWidget {
  const New({super.key});

  @override
  _NewState createState() => _NewState();
}

class _NewState extends State<New> {
  final String apiUrl = 'http://127.0.0.1:8000/api/v1/request';
  final TextEditingController nameController = TextEditingController();

  String result = ''; // To store the result from the API call

  @override
  void dispose() {
    nameController.dispose();
    super.dispose();
  }

  Future<void> _postData() async {
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
            builder: (context) => RecorderNew(
              text: responseData["text"],
              token: responseData["token"],
            ),
          ),
        );
      } else {}
    } catch (e) {
      setState(() {
        result = 'Error: $e';
      });
    }
  }

  Future<void> _newAuth() async {
    Navigator.pop(context);
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
                  Padding(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 8, vertical: 16),
                    child: TextFormField(
                      controller: nameController,
                      decoration: const InputDecoration(
                        border: UnderlineInputBorder(
                            borderSide: BorderSide(color: Colors.teal)),
                        labelText: 'Enter your username',
                      ),
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
                              Text('Already have account'),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(
                    height: 16,
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
          )),
    );
  }
}
