import 'package:flutter/material.dart';

import 'src/app.dart';
import 'src/blog_repository.dart';

void main() {
  runApp(BlogApp(repository: BlogRepository.seeded()));
}
