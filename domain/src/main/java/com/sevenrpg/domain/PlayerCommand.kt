package com.sevenrpg.domain

import java.time.Instant
import java.util.UUID

/**
 * Typed player command — untrusted text parsed into structured command.
 * Directive: multi-agent-architect — player controls consequential choices.
 */
data class PlayerCommand(
    val commandId: String,
    val playerId: String,
    val sceneId: String,
    val action: String, // player-submitted, untrusted text
    val revisionBase: Int, // state revision this command is based on
    val timestamp: Instant = Instant.now()
) {
    fun toMap(): Map<String, Any> {
        return mapOf(
            "commandId" to commandId,
            "playerId" to playerId,
            "sceneId" to sceneId,
            "action" to action,
            "revisionBase" to revisionBase,
            "timestamp" to timestamp.toString()
        )
    }

    companion object {
        fun create(
            playerId: String,
            sceneId: String,
            action: String,
            revisionBase: Int
        ): PlayerCommand {
            return PlayerCommand(
                commandId = "cmd_${revisionBase}_${UUID.randomUUID().toString().substring(0, 8)}",
                playerId = playerId,
                sceneId = sceneId,
                action = action,
                revisionBase = revisionBase
            )
        }

        fun fromMap(data: Map<String, Any>): PlayerCommand {
            return PlayerCommand(
                commandId = data["commandId"] as String,
                playerId = data["playerId"] as String,
                sceneId = data["sceneId"] as String,
                action = data["action"] as String,
                revisionBase = data["revisionBase"] as Int,
                timestamp = Instant.parse(data["timestamp"] as String)
            )
        }
    }
}