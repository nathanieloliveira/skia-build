diff --git a/src/utils/SkParse.cpp b/src/utils/SkParse.cpp
index 4cbdaa5822..a71e7299a9 100644
--- a/src/utils/SkParse.cpp
+++ b/src/utils/SkParse.cpp
@@ -199,12 +199,28 @@ const char* SkParse::FindMSec(const char str[], SkMSec* value)
     return str;
 }
 
+#if !defined(SK_BUILD_FOR_ANDROID)
+#include <locale.h>
+#endif
+
+#if defined(SK_BUILD_FOR_MAC) || defined(SK_BUILD_FOR_IOS)
+#include <xlocale.h>
+#include <cstring>
+#endif
+
+#if defined(SK_BUILD_FOR_WIN)
+  static const _locale_t kDefaultLocale = _create_locale(LC_ALL, "C");
+  #define strtof_l(a, b, c) _strtof_l((a), (b), (c))
+#else
+  static const locale_t kDefaultLocale = newlocale(LC_ALL_MASK, "C", nullptr);
+#endif
+
 const char* SkParse::FindScalar(const char str[], SkScalar* value) {
     SkASSERT(str);
     str = skip_ws(str);
 
     char* stop;
-    float v = (float)strtod(str, &stop);
+    float v = strtof_l(str, &stop, kDefaultLocale);
     if (str == stop) {
         return nullptr;
     }
