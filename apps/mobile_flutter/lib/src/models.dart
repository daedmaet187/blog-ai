enum UserRole { reader, editor, admin }

class AppUser {
  const AppUser({required this.username, required this.role});

  final String username;
  final UserRole role;

  bool get canAuthor => role == UserRole.editor || role == UserRole.admin;
  bool get canPublish => canAuthor;
}

class BlogPost {
  BlogPost({
    required this.id,
    required this.title,
    required this.body,
    required this.author,
    this.published = true,
  });

  final String id;
  final String author;
  String title;
  String body;
  bool published;
}
