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

    sourceSets {
        getByName("main") {
            // Keep the existing domain sources in place; avoid destructive source moves.
            java.srcDirs(".")
        }
    }
}

dependencies {
    testImplementation(libs.junit)
    testImplementation(kotlin("test"))
}
