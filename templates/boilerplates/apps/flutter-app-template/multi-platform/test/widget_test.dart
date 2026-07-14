import 'package:flutter_test/flutter_test.dart';

import 'package:ariadne_flutter_multiplatform_app/app/app.dart';

void main() {
  testWidgets('home page shows multi-platform guidance', (tester) async {
    await tester.pumpWidget(const AriadneFlutterApp());

    expect(find.text('Multi-platform ready'), findsOneWidget);
    expect(find.textContaining('Current platform adapter'), findsOneWidget);
  });
}
