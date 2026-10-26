# ProGuard rules for Seven RPG
# Directive: multi-agent-architect — keep domain classes for reflection/safety

# Keep domain models
-keep class com.sevenrpg.domain.** { *; }

# Keep Android components
-keep public class * extends android.app.Activity
-keep public class * extends android.app.Application
-keep public class * extends android.app.Service
-keep public class * extends android.content.BroadcastReceiver
-keep public class * extends android.content.ContentProvider

# Keep ViewModel
-keep public class * extends androidx.lifecycle.ViewModel {
    public <init>(...);
}

# Keep R class
-keep class com.sevenrpg.app.R { *; }

# Keep custom attributes
-keepclassmembers class * {
    @androidx.annotation.Keep *;
}

# Don't obfuscate model classes
-keepnames class com.sevenrpg.domain.** { *; }

# Keep enum values
-keepclassmembers enum * {
    public static **[] values();
    public static ** valueOf(java.lang.String);
}