import 'package:flutter/material.dart';

import 'blog_repository.dart';
import 'models.dart';

class BlogApp extends StatefulWidget {
  const BlogApp({super.key, required this.repository});

  final BlogRepository repository;

  @override
  State<BlogApp> createState() => _BlogAppState();
}

class _BlogAppState extends State<BlogApp> {
  AppUser? _currentUser;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Blog Mission Control',
      home: _currentUser == null
          ? LoginScreen(
              onLogin: (user) => setState(() => _currentUser = user),
              repository: widget.repository,
            )
          : FeedScreen(
              repository: widget.repository,
              user: _currentUser!,
              onLogout: () => setState(() => _currentUser = null),
            ),
    );
  }
}

class LoginScreen extends StatefulWidget {
  const LoginScreen({
    super.key,
    required this.onLogin,
    required this.repository,
  });

  final ValueChanged<AppUser> onLogin;
  final BlogRepository repository;

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _usernameController = TextEditingController();
  UserRole _selectedRole = UserRole.reader;

  @override
  void dispose() {
    _usernameController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Login')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            TextField(
              key: const Key('login_username'),
              controller: _usernameController,
              decoration: const InputDecoration(labelText: 'Username'),
            ),
            DropdownButton<UserRole>(
              key: const Key('login_role'),
              value: _selectedRole,
              onChanged: (role) {
                if (role != null) setState(() => _selectedRole = role);
              },
              items: UserRole.values
                  .map(
                    (role) => DropdownMenuItem(
                      value: role,
                      child: Text(role.name),
                    ),
                  )
                  .toList(),
            ),
            ElevatedButton(
              key: const Key('login_button'),
              onPressed: () async {
                final user = await widget.repository.login(
                  username: _usernameController.text.isEmpty
                      ? 'guest'
                      : _usernameController.text,
                  role: _selectedRole,
                );
                widget.onLogin(user);
              },
              child: const Text('Continue'),
            ),
          ],
        ),
      ),
    );
  }
}

class FeedScreen extends StatefulWidget {
  const FeedScreen({
    super.key,
    required this.repository,
    required this.user,
    required this.onLogout,
  });

  final BlogRepository repository;
  final AppUser user;
  final VoidCallback onLogout;

  @override
  State<FeedScreen> createState() => _FeedScreenState();
}

class _FeedScreenState extends State<FeedScreen> {
  @override
  Widget build(BuildContext context) {
    final posts = widget.repository.listPublished();
    return Scaffold(
      appBar: AppBar(
        title: Text('Feed (${widget.user.role.name})'),
        actions: [
          IconButton(onPressed: widget.onLogout, icon: const Icon(Icons.logout)),
        ],
      ),
      body: ListView.builder(
        itemCount: posts.length,
        itemBuilder: (context, index) {
          final post = posts[index];
          return ListTile(
            title: Text(post.title),
            subtitle: Text(post.author),
            onTap: () async {
              await Navigator.of(context).push(
                MaterialPageRoute(
                  builder: (_) => PostDetailScreen(
                    post: post,
                    user: widget.user,
                    repository: widget.repository,
                  ),
                ),
              );
              setState(() {});
            },
          );
        },
      ),
      floatingActionButton: widget.user.canAuthor
          ? FloatingActionButton(
              key: const Key('new_post_button'),
              onPressed: () async {
                await Navigator.of(context).push(
                  MaterialPageRoute(
                    builder: (_) => EditPostScreen(
                      user: widget.user,
                      repository: widget.repository,
                    ),
                  ),
                );
                setState(() {});
              },
              child: const Icon(Icons.add),
            )
          : null,
    );
  }
}

class PostDetailScreen extends StatelessWidget {
  const PostDetailScreen({
    super.key,
    required this.post,
    required this.user,
    required this.repository,
  });

  final BlogPost post;
  final AppUser user;
  final BlogRepository repository;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Post Detail')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(post.title, style: Theme.of(context).textTheme.headlineSmall),
            const SizedBox(height: 8),
            Text(post.body),
            const SizedBox(height: 16),
            if (user.canAuthor)
              ElevatedButton(
                key: const Key('edit_post_button'),
                onPressed: () async {
                  await Navigator.of(context).push(
                    MaterialPageRoute(
                      builder: (_) => EditPostScreen(
                        user: user,
                        repository: repository,
                        initialPost: post,
                      ),
                    ),
                  );
                  if (context.mounted) Navigator.of(context).pop();
                },
                child: const Text('Edit'),
              ),
          ],
        ),
      ),
    );
  }
}

class EditPostScreen extends StatefulWidget {
  const EditPostScreen({
    super.key,
    required this.user,
    required this.repository,
    this.initialPost,
  });

  final AppUser user;
  final BlogRepository repository;
  final BlogPost? initialPost;

  @override
  State<EditPostScreen> createState() => _EditPostScreenState();
}

class _EditPostScreenState extends State<EditPostScreen> {
  late final TextEditingController _titleController;
  late final TextEditingController _bodyController;

  @override
  void initState() {
    super.initState();
    _titleController = TextEditingController(text: widget.initialPost?.title ?? '');
    _bodyController = TextEditingController(text: widget.initialPost?.body ?? '');
  }

  @override
  void dispose() {
    _titleController.dispose();
    _bodyController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Author Post')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            TextField(
              key: const Key('post_title_input'),
              controller: _titleController,
              decoration: const InputDecoration(labelText: 'Title'),
            ),
            TextField(
              key: const Key('post_body_input'),
              controller: _bodyController,
              decoration: const InputDecoration(labelText: 'Body'),
            ),
            const SizedBox(height: 12),
            ElevatedButton(
              key: const Key('save_draft_button'),
              onPressed: () {
                if (widget.initialPost == null) {
                  widget.repository.createDraft(
                    title: _titleController.text,
                    body: _bodyController.text,
                    author: widget.user,
                  );
                } else {
                  widget.repository.updatePost(
                    post: widget.initialPost!,
                    title: _titleController.text,
                    body: _bodyController.text,
                  );
                }
                Navigator.of(context).pop();
              },
              child: const Text('Save Draft'),
            ),
            if (widget.user.canPublish)
              ElevatedButton(
                key: const Key('publish_button'),
                onPressed: () {
                  final post = widget.initialPost ??
                      widget.repository.createDraft(
                        title: _titleController.text,
                        body: _bodyController.text,
                        author: widget.user,
                      );
                  widget.repository.updatePost(
                    post: post,
                    title: _titleController.text,
                    body: _bodyController.text,
                  );
                  widget.repository.publish(post);
                  Navigator.of(context).pop();
                },
                child: const Text('Publish'),
              ),
          ],
        ),
      ),
    );
  }
}
