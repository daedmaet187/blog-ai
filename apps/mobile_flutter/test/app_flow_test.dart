import 'package:blog_mobile/src/app.dart';
import 'package:blog_mobile/src/blog_repository.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('login shows feed and renders seeded posts', (tester) async {
    await tester.pumpWidget(BlogApp(repository: BlogRepository.seeded()));

    await tester.enterText(find.byKey(const Key('login_username')), 'reader_1');
    await tester.tap(find.byKey(const Key('login_button')));
    await tester.pumpAndSettle();

    expect(find.textContaining('Feed (reader)'), findsOneWidget);
    expect(find.text('Welcome to Beta'), findsOneWidget);
  });

  testWidgets('feed navigates to detail and shows body', (tester) async {
    await tester.pumpWidget(BlogApp(repository: BlogRepository.seeded()));

    await tester.tap(find.byKey(const Key('login_button')));
    await tester.pumpAndSettle();

    await tester.tap(find.text('Welcome to Beta'));
    await tester.pumpAndSettle();

    expect(find.text('Post Detail'), findsOneWidget);
    expect(find.text('This is the internal beta feed.'), findsOneWidget);
  });

  testWidgets('reader cannot publish, editor can create and publish', (tester) async {
    await tester.pumpWidget(BlogApp(repository: BlogRepository.seeded()));

    await tester.tap(find.byKey(const Key('login_button')));
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('new_post_button')), findsNothing);
    await tester.tap(find.byIcon(Icons.logout));
    await tester.pumpAndSettle();

    await tester.tap(find.byKey(const Key('login_role')));
    await tester.pumpAndSettle();
    await tester.tap(find.text('editor').last);
    await tester.pumpAndSettle();

    await tester.tap(find.byKey(const Key('login_button')));
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('new_post_button')), findsOneWidget);

    await tester.tap(find.byKey(const Key('new_post_button')));
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('publish_button')), findsOneWidget);
  });
}
