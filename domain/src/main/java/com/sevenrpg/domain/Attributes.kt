package com.sevenrpg.domain

/**
 * Character attributes — Strength, Agility, Intelligence, etc.
 * Directive: deterministic rules for attributes and checks.
 */
data class Attributes(
    val strength: Int = 10,
    val agility: Int = 10,
    val intelligence: Int = 10,
    val vitality: Int = 10,
    val willpower: Int = 10,
    val perception: Int = 10
) {
    fun toMap(): Map<String, Any> = mapOf(
        "strength" to strength,
        "agility" to agility,
        "intelligence" to intelligence,
        "vitality" to vitality,
        "willpower" to willpower,
        "perception" to perception
    )

    companion object {
        fun fromMap(data: Map<String, Any>): Attributes = Attributes(
            strength = data["strength"] as? Int ?: 10,
            agility = data["agility"] as? Int ?: 10,
            intelligence = data["intelligence"] as? Int ?: 10,
            vitality = data["vitality"] as? Int ?: 10,
            willpower = data["willpower"] as? Int ?: 10,
            perception = data["perception"] as? Int ?: 10
        )
    }
}

/**
 * Attribute check result — deterministic success/failure based on attribute + dice roll.
 */
data class AttributeCheckResult(
    val attribute: String,
    val attributeValue: Int,
    val difficultyClass: Int,
    val roll: Int,
    val total: Int,
    val success: Boolean
) {
    fun toMap(): Map<String, Any> = mapOf(
        "attribute" to attribute,
        "attributeValue" to attributeValue,
        "difficultyClass" to difficultyClass,
        "roll" to roll,
        "total" to total,
        "success" to success
    )
}

/**
 * Perform a deterministic attribute check.
 */
fun checkAttribute(attributeValue: Int, difficultyClass: Int, roll: Int, attribute: String = "unknown"): AttributeCheckResult {
    val total = attributeValue + roll
    return AttributeCheckResult(
        attribute = attribute,
        attributeValue = attributeValue,
        difficultyClass = difficultyClass,
        roll = roll,
        total = total,
        success = total >= difficultyClass
    )
}