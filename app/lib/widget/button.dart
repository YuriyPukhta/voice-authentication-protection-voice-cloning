import 'package:flutter/material.dart';

class Button extends StatelessWidget {
  final String text;
  final void Function() onPress;
  final IconData? icon;
  final Color color;

  const Button({
    super.key,
    required this.text,
    required this.onPress,
    this.icon,
    this.color = Colors.teal,
  });

  @override
  Widget build(BuildContext context) {
    return OutlinedButton(
      onPressed: onPress,
      style: OutlinedButton.styleFrom(
        foregroundColor: Colors.teal,
        side: const BorderSide(
          color: Colors.teal,
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Row(
          mainAxisSize: MainAxisSize.max,
          children: [
            Text(text),
            const SizedBox(
              width: 16,
            ),
            if (icon != null) ...[
              Icon(icon),
            ],
          ],
        ),
      ),
    );
  }
}
