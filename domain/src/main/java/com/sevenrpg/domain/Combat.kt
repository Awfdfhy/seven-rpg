package com.sevenrpg.domain

/**
 * Combat state — active combat encounter.
 */
data class CombatState(
    val combatId: String,
    val participants: List<CombatParticipant> = emptyList(),
    val currentTurnIndex: Int = 0,
    val status: String = "active", // active, ended, fled
    val rounds: Int = 0
) {
    val currentParticipant: CombatParticipant? get() =
        participants.indices.takeIf { it.contains(currentTurnIndex) }?.let { participants[currentTurnIndex] }

    fun toMap(): Map<String, Any> = mapOf(
        "combatId" to combatId,
        "participants" to participants.map { it.toMap() },
        "currentTurnIndex" to currentTurnIndex,
        "status" to status,
        "rounds" to rounds
    )

    companion object {
        fun fromMap(data: Map<String, Any>): CombatState = CombatState(
            combatId = data["combatId"] as String,
            participants = (data["participants"] as? List<*>)
                ?.map { CombatParticipant.fromMap(it as Map<String, Any>) }
                ?: emptyList(),
            currentTurnIndex = data["currentTurnIndex"] as? Int ?: 0,
            status = data["status"] as? String ?: "active",
            rounds = data["rounds"] as? Int ?: 0
        )
    }
}

/**
 * Combat participant — player or NPC in combat.
 */
data class CombatParticipant(
    val participantId: String,
    val name: String,
    val type: String, // player, npc, enemy
    val currentHP: Int,
    val maxHP: Int,
    val currentMP: Int,
    val maxMP: Int,
    val attributes: Attributes = Attributes(),
    val isAlive: Boolean = true,
    val isPlayerControlled: Boolean = false
) {
    fun toMap(): Map<String, Any> = mapOf(
        "participantId" to participantId,
        "name" to name,
        "type" to type,
        "currentHP" to currentHP,
        "maxHP" to maxHP,
        "currentMP" to currentMP,
        "maxMP" to maxMP,
        "attributes" to attributes.toMap(),
        "isAlive" to isAlive,
        "isPlayerControlled" to isPlayerControlled
    )

    companion object {
        fun fromMap(data: Map<String, Any>): CombatParticipant = CombatParticipant(
            participantId = data["participantId"] as String,
            name = data["name"] as String,
            type = data["type"] as String,
            currentHP = data["currentHP"] as? Int ?: 0,
            maxHP = data["maxHP"] as? Int ?: 0,
            currentMP = data["currentMP"] as? Int ?: 0,
            maxMP = data["maxMP"] as? Int ?: 0,
            attributes = Attributes.fromMap(data["attributes"] as? Map<String, Any> ?: emptyMap()),
            isAlive = data["isAlive"] as? Boolean ?: true,
            isPlayerControlled = data["isPlayerControlled"] as? Boolean ?: false
        )
    }
}

/**
 * Combat result — outcome of a single combat action.
 */
data class CombatResult(
    val attackerId: String,
    val targetId: String,
    val action: String, // attack, skill, item, flee
    val damage: Int,
    val healed: Int,
    val success: Boolean,
    val message: String
) {
    fun toMap(): Map<String, Any> = mapOf(
        "attackerId" to attackerId,
        "targetId" to targetId,
        "action" to action,
        "damage" to damage,
        "healed" to healed,
        "success" to success,
        "message" to message
    )
}

/**
 * Process a combat turn — deterministic attack resolution.
 */
fun processCombatAttack(
    attacker: CombatParticipant,
    target: CombatParticipant,
    attackPower: Int
): CombatResult {
    val attackerStr = attacker.attributes.strength
    val targetVit = target.attributes.vitality
    val baseDamage = (attackerStr * attackPower / 10.0).toInt().coerceAtLeast(1)
    val damageReduction = (targetVit / 2.0).toInt().coerceAtLeast(0)
    val finalDamage = (baseDamage - damageReduction).coerceAtLeast(0)
    val newTargetHP = (target.currentHP - finalDamage).coerceAtLeast(0)
    val isAlive = newTargetHP > 0

    return CombatResult(
        attackerId = attacker.participantId,
        targetId = target.participantId,
        action = "attack",
        damage = finalDamage,
        healed = 0,
        success = true,
        message = "$attacker.name attacked ${target.name} for $finalDamage damage"
    )
}