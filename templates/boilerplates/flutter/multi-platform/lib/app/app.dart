import 'package:flutter/material.dart';

import '../platform/platform_info_stub.dart';

class AriadneFlutterApp extends StatelessWidget {
  const AriadneFlutterApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Ariadne Flutter App',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.indigo),
        useMaterial3: true,
      ),
      home: const AriadneHomePage(),
    );
  }
}

class AriadneHomePage extends StatelessWidget {
  const AriadneHomePage({super.key});

  @override
  Widget build(BuildContext context) {
    final platformInfo = createPlatformInfo();
    return Scaffold(
      appBar: AppBar(title: const Text('Ariadne Flutter')),
      body: LayoutBuilder(
        builder: (context, constraints) {
          final isWide = constraints.maxWidth >= 720;
          return Center(
            child: ConstrainedBox(
              constraints: BoxConstraints(maxWidth: isWide ? 720 : 420),
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Multi-platform ready',
                      style:
                          TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 12),
                    Text('Current platform adapter: ${platformInfo.name}'),
                    const SizedBox(height: 12),
                    const Text(
                      'Place platform differences behind interfaces and keep UI responsive.',
                    ),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}
