import 'models.dart';

class BlogRepository {
  BlogRepository({required List<BlogPost> posts}) : _posts = posts;

  factory BlogRepository.seeded() {
    return BlogRepository(
      posts: [
        BlogPost(
          id: '1',
          title: 'Welcome to Beta',
          body: 'This is the internal beta feed.',
          author: 'admin',
          published: true,
        ),
        BlogPost(
          id: '2',
          title: 'Roadmap Snapshot',
          body: 'Role-aware authoring lands in this release.',
          author: 'editor',
          published: true,
        ),
      ],
    );
  }

  final List<BlogPost> _posts;

  Future<AppUser> login({
    required String username,
    required UserRole role,
  }) async {
    return AppUser(username: username, role: role);
  }

  List<BlogPost> listPublished() {
    return _posts.where((post) => post.published).toList(growable: false);
  }

  BlogPost createDraft({
    required String title,
    required String body,
    required AppUser author,
  }) {
    final post = BlogPost(
      id: DateTime.now().microsecondsSinceEpoch.toString(),
      title: title,
      body: body,
      author: author.username,
      published: false,
    );
    _posts.insert(0, post);
    return post;
  }

  void updatePost({required BlogPost post, required String title, required String body}) {
    post.title = title;
    post.body = body;
  }

  void publish(BlogPost post) {
    post.published = true;
  }
}
