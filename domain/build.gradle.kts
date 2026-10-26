plugins {
    alias(libs.plugins.android.library)
    alias(libs.plugins.kotlin.android)
}

android {
    namespace = "com.sevenrpg.domain"
    compileSdk = 34

    defaultConfig {
        minSdk = 24
    }
}

dependencies {
    testImplementation(libs.junit)
    testImplementation(kotlin("test"))
}
