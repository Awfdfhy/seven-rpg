package com.sevenrpg.domain

/**
 * World location — scene or area within a world.
 */
data class WorldLocation(
    val locationId: String,
    val name: String,
    val description: String,
    val region: String, // region name
    val connections: List<String> = emptyList(), // connected location IDs
    val discovered: Boolean = false,
    val visited: Boolean = false,
    val dangerLevel: Int = 1, // 1-10
    val availableScenes: List<String> = emptyList() // scene IDs available here
) {
    fun toMap(): Map<String, Any> = mapOf(
        "locationId" to locationId,
        "name" to name,
        "description" to description,
        "region" to region,
        "connections" to connections,
        "discovered" to discovered,
        "visited" to visited,
        "dangerLevel" to dangerLevel,
        "availableScenes" to availableScenes
    )

    companion object {
        fun fromMap(data: Map<String, Any>): WorldLocation = WorldLocation(
            locationId = data["locationId"] as String,
            name = data["name"] as String,
            description = data["description"] as String,
            region = data["region"] as String,
            connections = data["connections"] as? List<String> ?: emptyList(),
            discovered = data["discovered"] as? Boolean ?: false,
            visited = data["visited"] as? Boolean ?: false,
            dangerLevel = data["dangerLevel"] as? Int ?: 1,
            availableScenes = data["availableScenes"] as? List<String> ?: emptyList()
        )
    }
}

/**
 * World map — all locations and travel network.
 */
data class WorldMap(
    val locations: Map<String, WorldLocation> = emptyMap(),
    val currentLocationId: String? = null
) {
    val currentLocation: WorldLocation? get() = currentLocationId?.let { locations[it] }
    val availableConnections: List<WorldLocation> get() =
        currentLocation?.connections?.mapNotNull { locations[it] } ?: emptyList()

    fun moveTo(locationId: String): WorldMap =
        copy(currentLocationId = locationId).copy(
            locations = locations.mapValues { if (it.key == locationId) it.value.copy(visited = true) else it.value }
        )

    fun discoverLocation(locationId: String): WorldMap =
        copy(locations = locations.mapValues { if (it.key == locationId) it.value.copy(discovered = true) else it.value })

    fun getLocation(locationId: String): WorldLocation? = locations[locationId]

    fun toMap(): Map<String, Any> = mapOf(
        "locations" to locations.mapValues { it.value.toMap() },
        "currentLocationId" to currentLocationId
    )

    companion object {
        fun fromMap(data: Map<String, Any>): WorldMap = WorldMap(
            locations = (data["locations"] as? Map<*, *>)
                ?.mapValues { it.value as Map<String, Any> }
                ?.mapValues { WorldLocation.fromMap(it) }
                ?: emptyMap(),
            currentLocationId = data["currentLocationId"] as? String
        )
    }
}