package com.sevenrpg.domain

/**
 * Extended reducer — handles all RPG system events.
 * Directive: deterministic reducer — invalid events rejected without mutation.
 */
object ExtendedReducer {

    /**
     * Apply an extended domain event to the extended game state.
     */
    fun applyExtendedEvent(state: ExtendedGameState, event: DomainEvent): Pair<ExtendedGameState, Boolean> {
        return when (event.type) {
            "experience_gained" -> applyExperienceGained(state, event)
            "attribute_increased" -> applyAttributeIncreased(state, event)
            "skill_learned" -> applySkillLearned(state, event)
            "skill_upgraded" -> applySkillUpgraded(state, event)
            "item_acquired" -> applyItemAcquired(state, event)
            "item_equipped" -> applyItemEquipped(state, event)
            "item_unequipped" -> applyItemUnequipped(state, event)
            "quest_started" -> applyQuestStarted(state, event)
            "quest_completed" -> applyQuestCompleted(state, event)
            "quest_objective_updated" -> applyQuestObjectiveUpdated(state, event)
            "faction_standing_changed" -> applyFactionStandingChanged(state, event)
            "relationship_changed" -> applyRelationshipChanged(state, event)
            "location_discovered" -> applyLocationDiscovered(state, event)
            "location_visited" -> applyLocationVisited(state, event)
            "combat_started" -> applyCombatStarted(state, event)
            "combat_attack" -> applyCombatAttack(state, event)
            "combat_ended" -> applyCombatEnded(state, event)
            else -> Pair(state, false)
        }
    }

    private fun applyExperienceGained(state: ExtendedGameState, event: DomainEvent): Pair<ExtendedGameState, Boolean> {
        val amount = (event.payload["amount"] as? Int) ?: 0
        val newProgression = state.playerProgression.progression.addExperience(amount)
        return Pair(
            state.copy(playerProgression = state.playerProgression.copy(progression = newProgression)),
            true
        )
    }

    private fun applyAttributeIncreased(state: ExtendedGameState, event: DomainEvent): Pair<ExtendedGameState, Boolean> {
        val attribute = (event.payload["attribute"] as? String) ?: return Pair(state, false)
        val current = state.playerProgression.attributes
        val newAttributes = when (attribute) {
            "strength" -> current.copy(strength = current.strength + 1)
            "agility" -> current.copy(agility = current.agility + 1)
            "intelligence" -> current.copy(intelligence = current.intelligence + 1)
            "vitality" -> current.copy(vitality = current.vitality + 1)
            "willpower" -> current.copy(willpower = current.willpower + 1)
            "perception" -> current.copy(perception = current.perception + 1)
            else -> current
        }
        return Pair(state.copy(playerProgression = state.playerProgression.copy(attributes = newAttributes)), true)
    }

    private fun applySkillLearned(state: ExtendedGameState, event: DomainEvent): Pair<ExtendedGameState, Boolean> {
        val skillId = (event.payload["skillId"] as? String) ?: return Pair(state, false)
        val skillName = (event.payload["name"] as? String) ?: skillId
        val skillType = (event.payload["skillType"] as? String) ?: "active"
        val skill = Skill(skillId = skillId, name = skillName, description = "", skillType = skillType)
        return Pair(state.copy(playerProgression = state.playerProgression.copy(skills = state.playerProgression.skills.learnSkill(skill))), true)
    }

    private fun applySkillUpgraded(state: ExtendedGameState, event: DomainEvent): Pair<ExtendedGameState, Boolean> {
        val skillId = (event.payload["skillId"] as? String) ?: return Pair(state, false)
        return Pair(state.copy(playerProgression = state.playerProgression.copy(skills = state.playerProgression.skills.upgradeSkill(skillId))), true)
    }

    private fun applyItemAcquired(state: ExtendedGameState, event: DomainEvent): Pair<ExtendedGameState, Boolean> {
        val itemId = (event.payload["itemId"] as? String) ?: return Pair(state, false)
        val name = (event.payload["name"] as? String) ?: itemId
        val itemType = (event.payload["itemType"] as? String) ?: "misc"
        val weight = (event.payload["weight"] as? Double) ?: 0.0
        val value = (event.payload["value"] as? Int) ?: 0
        val quantity = (event.payload["quantity"] as? Int) ?: 1
        val item = InventoryItem(itemId = itemId, name = name, itemType = itemType, weight = weight, value = value, quantity = quantity)
        return Pair(state.copy(playerProgression = state.playerProgression.copy(inventory = state.playerProgression.inventory.addItem(item))), true)
    }

    private fun applyItemEquipped(state: ExtendedGameState, event: DomainEvent): Pair<ExtendedGameState, Boolean> {
        val itemId = (event.payload["itemId"] as? String) ?: return Pair(state, false)
        return Pair(state.copy(playerProgression = state.playerProgression.copy(inventory = state.playerProgression.inventory.equipItem(itemId))), true)
    }

    private fun applyItemUnequipped(state: ExtendedGameState, event: DomainEvent): Pair<ExtendedGameState, Boolean> {
        val itemId = (event.payload["itemId"] as? String) ?: return Pair(state, false)
        return Pair(state.copy(playerProgression = state.playerProgression.copy(inventory = state.playerProgression.inventory.unequipItem(itemId))), true)
    }

    private fun applyQuestStarted(state: ExtendedGameState, event: DomainEvent): Pair<ExtendedGameState, Boolean> {
        val questId = (event.payload["questId"] as? String) ?: return Pair(state, false)
        val title = (event.payload["title"] as? String) ?: questId
        val description = (event.payload["description"] as? String) ?: ""
        val quest = Quest(questId = questId, title = title, description = description, status = "active")
        return Pair(state.copy(playerProgression = state.playerProgression.copy(quests = state.playerProgression.quests.addQuest(quest))), true)
    }

    private fun applyQuestCompleted(state: ExtendedGameState, event: DomainEvent): Pair<ExtendedGameState, Boolean> {
        val questId = (event.payload["questId"] as? String) ?: return Pair(state, false)
        return Pair(state.copy(playerProgression = state.playerProgression.copy(quests = state.playerProgression.quests.completeQuest(questId))), true)
    }

    private fun applyQuestObjectiveUpdated(state: ExtendedGameState, event: DomainEvent): Pair<ExtendedGameState, Boolean> {
        val questId = (event.payload["questId"] as? String) ?: return Pair(state, false)
        val objectiveId = (event.payload["objectiveId"] as? String) ?: return Pair(state, false)
        val currentCount = (event.payload["currentCount"] as? Int) ?: 0
        val quests = state.playerProgression.quests.quests.map { q ->
            if (q.questId == questId) {
                q.copy(objectives = q.objectives.map { o ->
                    if (o.objectiveId == objectiveId) o.copy(currentCount = currentCount) else o
                })
            } else q
        }
        return Pair(state.copy(playerProgression = state.playerProgression.copy(quests = state.playerProgression.quests.copy(quests = quests))), true)
    }

    private fun applyFactionStandingChanged(state: ExtendedGameState, event: DomainEvent): Pair<ExtendedGameState, Boolean> {
        val factionId = (event.payload["factionId"] as? String) ?: return Pair(state, false)
        val change = (event.payload["change"] as? Int) ?: 0
        return Pair(state.copy(playerProgression = state.playerProgression.copy(factions = state.playerProgression.factions.modifyStanding(factionId, change))), true)
    }

    private fun applyRelationshipChanged(state: ExtendedGameState, event: DomainEvent): Pair<ExtendedGameState, Boolean> {
        val targetId = (event.payload["targetId"] as? String) ?: return Pair(state, false)
        val change = (event.payload["change"] as? Int) ?: 0
        val current = state.playerProgression.relationships.getRelationship(targetId)?.standing ?: 0
        val newStanding = (current + change).coerceIn(-100, 100)
        val updated = state.playerProgression.relationships.getRelationship(targetId)?.copy(standing = newStanding) ?: CharacterRelationship(
            targetId = targetId,
            targetName = targetId,
            relationshipType = "unknown",
            standing = newStanding
        )
        return Pair(state.copy(playerProgression = state.playerProgression.copy(relationships = state.playerProgression.relationships.addOrUpdate(updated))), true)
    }

    private fun applyLocationDiscovered(state: ExtendedGameState, event: DomainEvent): Pair<ExtendedGameState, Boolean> {
        val locationId = (event.payload["locationId"] as? String) ?: return Pair(state, false)
        return Pair(state.copy(worldMap = state.worldMap.discoverLocation(locationId)), true)
    }

    private fun applyLocationVisited(state: ExtendedGameState, event: DomainEvent): Pair<ExtendedGameState, Boolean> {
        val locationId = (event.payload["locationId"] as? String) ?: return Pair(state, false)
        return Pair(state.copy(worldMap = state.worldMap.moveTo(locationId)), true)
    }

    private fun applyCombatStarted(state: ExtendedGameState, event: DomainEvent): Pair<ExtendedGameState, Boolean> {
        val combatId = (event.payload["combatId"] as? String) ?: return Pair(state, false)
        val participants = (event.payload["participants"] as? List<Map<String, Any>>)
            ?.map { CombatParticipant.fromMap(it) }
            ?: emptyList()
        val combat = CombatState(combatId = combatId, participants = participants)
        return Pair(state.copy(combatState = combat), true)
    }

    private fun applyCombatAttack(state: ExtendedGameState, event: DomainEvent): Pair<ExtendedGameState, Boolean> {
        val combat = state.combatState ?: return Pair(state, false)
        val attackerId = (event.payload["attackerId"] as? String) ?: return Pair(state, false)
        val targetId = (event.payload["targetId"] as? String) ?: return Pair(state, false)
        val attacker = combat.participants.find { it.participantId == attackerId } ?: return Pair(state, false)
        val target = combat.participants.find { it.participantId == targetId } ?: return Pair(state, false)
        val result = processCombatAttack(attacker, target, attackPower = 1)
        val newParticipants = combat.participants.map { p ->
            if (p.participantId == targetId) p.copy(currentHP = (p.currentHP - result.damage).coerceAtLeast(0)) else p
        }
        val newCombat = combat.copy(participants = newParticipants)
        return Pair(state.copy(combatState = newCombat), true)
    }

    private fun applyCombatEnded(state: ExtendedGameState, event: DomainEvent): Pair<ExtendedGameState, Boolean> {
        return Pair(state.copy(combatState = state.combatState?.copy(status = "ended")), true)
    }
}