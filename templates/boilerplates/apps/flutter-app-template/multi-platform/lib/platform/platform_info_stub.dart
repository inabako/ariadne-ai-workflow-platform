import 'interfaces/platform_info.dart';

PlatformInfo createPlatformInfo() => const GenericPlatformInfo();

class GenericPlatformInfo implements PlatformInfo {
  const GenericPlatformInfo();

  @override
  String get name => 'generic';
}
