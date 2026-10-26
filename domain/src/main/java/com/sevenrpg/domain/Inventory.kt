package com.sevenrpg.domain

/**
 * Inventory item — equipment, consumables, quest items.
 */
data class InventoryItem(
    val itemId: String,
    val name: String,
    val itemType: String, // weapon, armor, consumable, quest, material
    val weight: Double = 0.0,
    val value: Int = 0,
    val quantity: Int = 1,
    val equipped: Boolean = false
) {
    fun toMap(): Map<String, Any> = mapOf(
        "itemId" to itemId,
        "name" to name,
        "itemType" to itemType,
        "weight" to weight,
        "value" to value,
        "quantity" to quantity,
        "equipped" to equipped
    )

    companion object {
        fun fromMap(data: Map<String, Any>): InventoryItem = InventoryItem(
            itemId = data["itemId"] as String,
            name = data["name"] as String,
            itemType = data["itemType"] as String,
            weight = data["weight"] as? Double ?: 0.0,
            value = data["value"] as? Int ?: 0,
            quantity = data["quantity"] as? Int ?: 1,
            equipped = data["equipped"] as? Boolean ?: false
        )
    }
}

/**
 * Inventory — collection of items with weight/value tracking.
 */
data class Inventory(
    val items: List<InventoryItem> = emptyList(),
    val maxWeight: Double = 50.0,
    val maxSlots: Int = 100
) {
    val totalWeight: Double get() = items.sumOf { it.weight * it.quantity }
    val totalValue: Int get() = items.sumOf { it.value * it.quantity }
    val itemCount: Int get() = items.sumOf { it.quantity }
    val equippedItems: List<InventoryItem> get() = items.filter { it.equipped }

    fun canAdd(item: InventoryItem): Boolean = totalWeight + item.weight <= maxWeight && itemCount < maxSlots

    fun addItem(item: InventoryItem): Inventory =
        copy(items = items + item)

    fun removeItem(itemId: String): Inventory =
        copy(items = items.filter { it.itemId != itemId })

    fun equipItem(itemId: String): Inventory =
        copy(items = items.map { if (it.itemId == itemId) it.copy(equipped = true) else it })

    fun unequipItem(itemId: String): Inventory =
        copy(items = items.map { if (it.itemId == itemId) it.copy(equipped = false) else it })

    fun toMap(): Map<String, Any> = mapOf(
        "items" to items.map { it.toMap() },
        "maxWeight" to maxWeight,
        "maxSlots" to maxSlots
    )

    companion object {
        fun fromMap(data: Map<String, Any>): Inventory = Inventory(
            items = (data["items"] as? List<*>)
                ?.map { InventoryItem.fromMap(it as Map<String, Any>) }
                ?: emptyList(),
            maxWeight = data["maxWeight"] as? Double ?: 50.0,
            maxSlots = data["maxSlots"] as? Int ?: 100
        )
    }
}