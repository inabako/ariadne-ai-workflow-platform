import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';

import 'package:ariadne_flutter_multiplatform_app/app/app.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('application starts and renders home page', (tester) async {
    await tester.pumpWidget(const AriadneFlutterApp());

    expect(find.text('Multi-platform ready'), findsOneWidget);
  });
}
