#include <jni.h>
#include <string.h>

// Stub: report everything clean. Original returned a JSON string with fdFrida/fridaLibLoaded etc.
jstring Java_com_mikoloy_device_1trust_DeviceTrustNative_collectNativeSignals(JNIEnv* env, jobject thiz) {
    return (*env)->NewStringUTF(env, "{}");
}
