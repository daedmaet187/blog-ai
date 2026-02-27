import 'package:flutter/material.dart';

void main() {
  runApp(const BlogApp());
}

class BlogApp extends StatelessWidget {
  const BlogApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Blog Mission Control',
      home: Scaffold(
        appBar: AppBar(title: const Text('Blog Mobile')),
        body: const Center(child: Text('Flutter app bootstrap ready ✅')),
      ),
    );
  }
}
