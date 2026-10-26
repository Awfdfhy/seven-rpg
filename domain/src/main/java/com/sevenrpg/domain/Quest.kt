package com.sevenrpg.domain

/**
 * Quest — player-tracked objectives with states.
 */
data class Quest(
    val questId: String,
    val title: String,
    val description: String,
    val status: String, // active, completed, failed, abandoned
    val objectives: List<QuestObjective> = emptyList(),
    val rewards: Map<String, Any> = emptyMap(),
    val startTime: Long = System.currentTimeMillis(),
    val endTime: Long? = null
) {
    fun toMap(): Map<String, Any> {
        val result = linkedMapOf<String, Any>(
            "questId" to questId,
            "title" to title,
            "description" to description,
            "status" to status,
            "objectives" to objectives.map { it.toMap() },
            "rewards" to rewards,
            "startTime" to startTime
        )
        endTime?.let { result["endTime"] = it }
        return result
    }

    companion object {
        fun fromMap(data: Map<String, Any>): Quest = Quest(
            questId = data["questId"] as String,
            title = data["title"] as String,
            description = data["description"] as String,
            status = data["status"] as String,
            objectives = (data["objectives"] as? List<*>)
                ?.map { QuestObjective.fromMap(it as Map<String, Any>) }
                ?: emptyList(),
            rewards = data["rewards"] as? Map<String, Any> ?: emptyMap(),
            startTime = data["startTime"] as? Long ?: System.currentTimeMillis(),
            endTime = data["endTime"] as? Long
        )
    }
}

/**
 * Quest objective — individual steps within a quest.
 */
data class QuestObjective(
    val objectiveId: String,
    val description: String,
    val completed: Boolean = false,
    val currentCount: Int = 0,
    val targetCount: Int = 1
) {
    fun toMap(): Map<String, Any> = mapOf(
        "objectiveId" to objectiveId,
        "description" to description,
        "completed" to completed,
        "currentCount" to currentCount,
        "targetCount" to targetCount
    )

    companion object {
        fun fromMap(data: Map<String, Any>): QuestObjective = QuestObjective(
            objectiveId = data["objectiveId"] as String,
            description = data["description"] as String,
            completed = data["completed"] as? Boolean ?: false,
            currentCount = data["currentCount"] as? Int ?: 0,
            targetCount = data["targetCount"] as? Int ?: 1
        )
    }
}

/**
 * Quest log — collection of player quests.
 */
data class QuestLog(
    val quests: List<Quest> = emptyList()
) {
    val activeQuests: List<Quest> get() = quests.filter { it.status == "active" }
    val completedQuests: List<Quest> get() = quests.filter { it.status == "completed" }

    fun addQuest(quest: Quest): QuestLog = copy(quests = quests + quest)

    fun completeQuest(questId: String): QuestLog =
        copy(quests = quests.map { if (it.questId == questId) it.copy(status = "completed", endTime = System.currentTimeMillis()) else it })

    fun toMap(): Map<String, Any> = mapOf(
        "quests" to quests.map { it.toMap() }
    )

    companion object {
        fun fromMap(data: Map<String, Any>): QuestLog = QuestLog(
            quests = (data["quests"] as? List<*>)
                ?.map { Quest.fromMap(it as Map<String, Any>) }
                ?: emptyList()
        )
    }
}