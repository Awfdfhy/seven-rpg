package com.sevenrpg.app

import android.content.Context
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import android.util.Base64
import java.nio.charset.StandardCharsets
import java.security.KeyStore
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec

data class AIConnectionConfig(
    val endpoint: String,
    val model: String,
    val apiKey: String
)

/**
 * Keeps provider settings in the app-private preferences and encrypts the API key
 * with an AES-GCM key held by Android Keystore. The key is never logged or exported.
 */
object AIConnectionStore {
    const val DEFAULT_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
    const val DEFAULT_MODEL = "openai/gpt-4.1-mini"

    private const val PREFS = "seven_rpg_ai_connection"
    private const val ENDPOINT = "endpoint"
    private const val MODEL = "model"
    private const val ENCRYPTED_KEY = "encrypted_api_key"
    private const val KEY_ALIAS = "seven_rpg_ai_connection_key"
    private const val IV_BYTES = 12

    fun load(context: Context): AIConnectionConfig? {
        val preferences = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
        val endpoint = preferences.getString(ENDPOINT, null) ?: return null
        val model = preferences.getString(MODEL, null) ?: return null
        val encryptedKey = preferences.getString(ENCRYPTED_KEY, null) ?: return null
        val apiKey = runCatching { decrypt(encryptedKey) }.getOrNull()?.trim().orEmpty()
        if (apiKey.isBlank()) return null
        return AIConnectionConfig(endpoint, model, apiKey)
    }

    fun save(context: Context, endpoint: String, model: String, apiKey: String): Boolean {
        val cleanEndpoint = endpoint.trim()
        val cleanModel = model.trim()
        val cleanKey = apiKey.trim()
        val endpointUri = runCatching { java.net.URI(cleanEndpoint) }.getOrNull() ?: return false
        if (endpointUri.scheme != "https" || endpointUri.host.isNullOrBlank()) return false
        if (cleanModel.isBlank() || cleanKey.isBlank()) return false

        return runCatching {
            val encrypted = encrypt(cleanKey)
            context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit()
                .putString(ENDPOINT, cleanEndpoint)
                .putString(MODEL, cleanModel)
                .putString(ENCRYPTED_KEY, encrypted)
                .commit()
        }.getOrDefault(false)
    }

    fun clear(context: Context): Boolean =
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit().clear().commit()

    private fun secretKey(): SecretKey {
        val keyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
        val existing = keyStore.getKey(KEY_ALIAS, null) as? SecretKey
        if (existing != null) return existing
        val generator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore")
        generator.init(
            KeyGenParameterSpec.Builder(
                KEY_ALIAS,
                KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
            )
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                .setRandomizedEncryptionRequired(true)
                .build()
        )
        return generator.generateKey()
    }

    private fun encrypt(value: String): String {
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.ENCRYPT_MODE, secretKey())
        val encrypted = cipher.doFinal(value.toByteArray(StandardCharsets.UTF_8))
        val combined = cipher.iv + encrypted
        return Base64.encodeToString(combined, Base64.NO_WRAP)
    }

    private fun decrypt(value: String): String {
        val combined = Base64.decode(value, Base64.NO_WRAP)
        require(combined.size > IV_BYTES) { "Stored AI credential is invalid" }
        val iv = combined.copyOfRange(0, IV_BYTES)
        val ciphertext = combined.copyOfRange(IV_BYTES, combined.size)
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.DECRYPT_MODE, secretKey(), GCMParameterSpec(128, iv))
        return String(cipher.doFinal(ciphertext), StandardCharsets.UTF_8)
    }
}
