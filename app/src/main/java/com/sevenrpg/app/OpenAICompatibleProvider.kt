package com.sevenrpg.app

import com.sevenrpg.domain.AIProvider
import com.sevenrpg.domain.AIProviderCapabilities
import com.sevenrpg.domain.Proposal
import org.json.JSONArray
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.nio.charset.StandardCharsets

/**
 * Real OpenAI-compatible chat-completions adapter.
 * Provider prose is treated as untrusted narration; the app creates a narrowly scoped
 * narrative event and validates it with DomainReducer before applying it.
 */
class OpenAICompatibleProvider(
    private val config: AIConnectionConfig
) : AIProvider {

    override fun generateNarrative(
        goal: String,
        context: Map<String, Any>,
        revision: Int
    ): Proposal {
        require(goal.isNotBlank()) { "Action must not be blank" }
        require(revision > 0) { "Revision must be positive" }

        val systemPrompt = """
            أنت محرك السرد في Seven RPG، لعبة تقمص أدوار يكون اللاعب صاحب القرار.
            اكتب باللغة العربية، وركّز على نتيجة الفعل الذي طلبه اللاعب فقط.
            لا تخترع قراراً جديداً للاعب، ولا تغيّر حقائق العالم أو عناصره بنفسك.
            قدّم وصفاً واضحاً ومتماسكاً للمشهد، من 2 إلى 5 جمل، دون JSON أو مقدمات.
        """.trimIndent()

        val userPayload = JSONObject()
            .put("player_action", goal.take(200))
            .put("game_context", JSONObject(context))
            .put("state_revision", revision)
            .toString()

        val messages = JSONArray()
            .put(JSONObject().put("role", "system").put("content", systemPrompt))
            .put(JSONObject().put("role", "user").put("content", userPayload))

        val requestBody = JSONObject()
            .put("model", config.model)
            .put("messages", messages)
            .put("temperature", 0.7)
            .put("max_tokens", 500)
            .toString()

        val connection = (URL(config.endpoint).openConnection() as HttpURLConnection)
        try {
            connection.requestMethod = "POST"
            connection.connectTimeout = 15_000
            connection.readTimeout = 60_000
            connection.doOutput = true
            connection.setRequestProperty("Authorization", "Bearer ${config.apiKey}")
            connection.setRequestProperty("Content-Type", "application/json; charset=utf-8")
            connection.setRequestProperty("Accept", "application/json")
            connection.outputStream.use { output ->
                output.write(requestBody.toByteArray(StandardCharsets.UTF_8))
            }

            val status = connection.responseCode
            val responseStream = if (status in 200..299) connection.inputStream else connection.errorStream
            val responseText = responseStream?.bufferedReader(StandardCharsets.UTF_8)?.use { it.readText() }.orEmpty()
            if (status !in 200..299) {
                val safeMessage = runCatching {
                    JSONObject(responseText).optJSONObject("error")?.optString("message")
                }.getOrNull().orEmpty().take(240)
                throw IllegalStateException("AI provider returned HTTP $status: ${safeMessage.ifBlank { "request failed" }}")
            }

            val response = JSONObject(responseText)
            val content = response.optJSONArray("choices")
                ?.optJSONObject(0)
                ?.optJSONObject("message")
                ?.optString("content")
                ?.trim()
                .orEmpty()
            if (content.isBlank()) {
                throw IllegalStateException("AI provider returned an empty response")
            }

            val eventId = "evt_${revision}_${Integer.toHexString((goal + content).hashCode())}"
            val event = mapOf(
                "eventId" to eventId,
                "type" to "narrative_advance",
                "revisionBase" to revision,
                "authorized" to true,
                "payload" to mapOf(
                    "description" to content.take(2_000),
                    "derivedFrom" to goal.take(200)
                )
            )
            return Proposal(
                type = "narrative_response",
                prose = content.take(2_000),
                events = listOf(event),
                attemptsUnauthorizedMutation = false,
                revisionBase = revision,
                provider = "openai-compatible",
                callId = eventId
            )
        } finally {
            connection.disconnect()
        }
    }

    override fun cancel(callId: String): Boolean = false

    override fun declareCapabilities(): AIProviderCapabilities = AIProviderCapabilities(
        provider = "openai-compatible",
        streaming = false,
        cancellation = false,
        structuredOutput = true,
        timeoutSupport = true,
        retrySupport = false,
        maxRevisionBase = 1_000_000
    )
}
