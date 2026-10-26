# Seven RPG — Domain Entities (Stack-Agnostic)
# Directive: multi-agent-architect — typed domain entities independent of UI/provider.

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid


@dataclass
class World:
    """Versioned world entity — isolated per campaign."""
    world_id: str
    name: str
    canon_facts: Dict[str, Any] = field(default_factory=dict)
    version: int = 1
    isolated: bool = True
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "world_id": self.world_id,
            "name": self.name,
            "canon_facts": self.canon_facts,
            "version": self.version,
            "isolated": self.isolated,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "World":
        return cls(
            world_id=data["world_id"],
            name=data["name"],
            canon_facts=data.get("canon_facts", {}),
            version=data.get("version", 1),
            isolated=data.get("isolated", True),
            created_at=data.get("created_at", datetime.now(timezone.utc).isoformat()),
            updated_at=data.get("updated_at", datetime.now(timezone.utc).isoformat()),
        )


@dataclass
class PlayerCharacter:
    """Player character entity — unique within a world."""
    player_id: str
    name: str
    identity_sheet: Dict[str, Any] = field(default_factory=dict)
    attributes: Dict[str, Any] = field(default_factory=dict)
    progression: Dict[str, Any] = field(default_factory=dict)
    version: int = 1
    world_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "player_id": self.player_id,
            "name": self.name,
            "identity_sheet": self.identity_sheet,
            "attributes": self.attributes,
            "progression": self.progression,
            "version": self.version,
            "world_id": self.world_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PlayerCharacter":
        return cls(
            player_id=data["player_id"],
            name=data["name"],
            identity_sheet=data.get("identity_sheet", {}),
            attributes=data.get("attributes", {}),
            progression=data.get("progression", {}),
            version=data.get("version", 1),
            world_id=data.get("world_id", ""),
        )


@dataclass
class Scene:
    """Scene entity — player enters a scene to play."""
    scene_id: str
    world_id: str
    player_id: str
    canon_facts_loaded: bool = True
    character_knowledge: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scene_id": self.scene_id,
            "world_id": self.world_id,
            "player_id": self.player_id,
            "canon_facts_loaded": self.canon_facts_loaded,
            "character_knowledge": self.character_knowledge,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Scene":
        return cls(
            scene_id=data["scene_id"],
            world_id=data["world_id"],
            player_id=data["player_id"],
            canon_facts_loaded=data.get("canon_facts_loaded", True),
            character_knowledge=data.get("character_knowledge", {}),
        )


@dataclass
class DomainEvent:
    """Immutable domain event — applied to mutate state."""
    event_id: str
    type: str
    revision_base: int
    authorized: bool = True
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "type": self.type,
            "revision_base": self.revision_base,
            "authorized": self.authorized,
            "payload": self.payload,
            "timestamp": self.timestamp,
        }

    @classmethod
    def create(cls, event_type: str, revision_base: int, payload: Dict[str, Any] | None = None, authorized: bool = True) -> "DomainEvent":
        """Factory to create a new event with unique ID."""
        return cls(
            event_id=f"evt_{revision_base}_{uuid.uuid4().hex[:8]}",
            type=event_type,
            revision_base=revision_base,
            authorized=authorized,
            payload=payload or {},
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DomainEvent":
        return cls(
            event_id=data["event_id"],
            type=data["type"],
            revision_base=data["revision_base"],
            authorized=data.get("authorized", True),
            payload=data.get("payload", {}),
            timestamp=data.get("timestamp", datetime.now(timezone.utc).isoformat()),
        )


# --- RPG-09-02: Interactive World Map Entities ---

@dataclass
class Location:
    """A discoverable place on the world map."""
    location_id: str
    name: str
    region_id: str
    world_id: str
    coordinates: Dict[str, float] = field(default_factory=dict)  # {"x": 0.0, "y": 0.0}
    description: str = ""
    discovered: bool = False
    discovery_revision: int = 0
    npcs_present: List[str] = field(default_factory=list)  # NPC IDs currently at this location
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "location_id": self.location_id,
            "name": self.name,
            "region_id": self.region_id,
            "world_id": self.world_id,
            "coordinates": self.coordinates,
            "description": self.description,
            "discovered": self.discovered,
            "discovery_revision": self.discovery_revision,
            "npcs_present": self.npcs_present,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Location":
        return cls(
            location_id=data["location_id"],
            name=data["name"],
            region_id=data["region_id"],
            world_id=data["world_id"],
            coordinates=data.get("coordinates", {}),
            description=data.get("description", ""),
            discovered=data.get("discovered", False),
            discovery_revision=data.get("discovery_revision", 0),
            npcs_present=data.get("npcs_present", []),
            tags=data.get("tags", []),
        )


@dataclass
class Region:
    """A geographic region containing locations and travel connections."""
    region_id: str
    name: str
    world_id: str
    locations: List[str] = field(default_factory=list)  # location_ids
    travel_connections: List[Dict[str, Any]] = field(default_factory=list)  # {"to": loc_id, "cost": 1, "requires": []}
    discovered: bool = False
    discovery_revision: int = 0
    time_events: List[Dict[str, Any]] = field(default_factory=list)  # scheduled NPC/location events

    def to_dict(self) -> Dict[str, Any]:
        return {
            "region_id": self.region_id,
            "name": self.name,
            "world_id": self.world_id,
            "locations": self.locations,
            "travel_connections": self.travel_connections,
            "discovered": self.discovered,
            "discovery_revision": self.discovery_revision,
            "time_events": self.time_events,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Region":
        return cls(
            region_id=data["region_id"],
            name=data["name"],
            world_id=data["world_id"],
            locations=data.get("locations", []),
            travel_connections=data.get("travel_connections", []),
            discovered=data.get("discovered", False),
            discovery_revision=data.get("discovery_revision", 0),
            time_events=data.get("time_events", []),
        )


@dataclass
class MapState:
    """Tracks player progress on the world map."""
    current_location_id: str = ""
    discovered_locations: List[str] = field(default_factory=list)
    discovered_regions: List[str] = field(default_factory=list)
    travel_history: List[Dict[str, Any]] = field(default_factory=list)  # {"from": loc, "to": loc, "revision": N}
    active_quest_markers: List[str] = field(default_factory=list)  # location_ids

    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_location_id": self.current_location_id,
            "discovered_locations": self.discovered_locations,
            "discovered_regions": self.discovered_regions,
            "travel_history": self.travel_history,
            "active_quest_markers": self.active_quest_markers,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MapState":
        return cls(
            current_location_id=data.get("current_location_id", ""),
            discovered_locations=data.get("discovered_locations", []),
            discovered_regions=data.get("discovered_regions", []),
            travel_history=data.get("travel_history", []),
            active_quest_markers=data.get("active_quest_markers", []),
        )


from domain.campaign_settings import CampaignSettings


@dataclass
class GameState:
    """Aggregate root — current authoritative game state."""
    world: Optional[World] = None
    player: Optional[PlayerCharacter] = None
    scene: Optional[Scene] = None
    events: List[DomainEvent] = field(default_factory=list)
    revision: int = 1
    canon_facts: Dict[str, Any] = field(default_factory=dict)
    confirmed_event_log: List[DomainEvent] = field(default_factory=list)
    character_knowledge: Dict[str, Any] = field(default_factory=dict)
    character_beliefs: Dict[str, Any] = field(default_factory=dict)
    rumors: List[Dict[str, Any]] = field(default_factory=list)
    summaries: List[Dict[str, Any]] = field(default_factory=list)
    campaign_settings: Optional[CampaignSettings] = None
    # RPG-08-04: Skill check & combat state
    active_combat: Dict[str, Any] = field(default_factory=dict)
    skill_cooldowns: Dict[str, int] = field(default_factory=dict)
    combat_log: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "world": self.world.to_dict() if self.world else None,
            "player": self.player.to_dict() if self.player else None,
            "scene": self.scene.to_dict() if self.scene else None,
            "events": [e.to_dict() for e in self.events],
            "revision": self.revision,
            "canon_facts": self.canon_facts,
            "campaign_settings": self.campaign_settings.to_dict() if self.campaign_settings else None,
            "active_combat": self.active_combat,
            "skill_cooldowns": self.skill_cooldowns,
            "combat_log": self.combat_log,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GameState":
        return cls(
            world=World.from_dict(data["world"]) if data.get("world") else None,
            player=PlayerCharacter.from_dict(data["player"]) if data.get("player") else None,
            scene=Scene.from_dict(data["scene"]) if data.get("scene") else None,
            events=[DomainEvent.from_dict(e) for e in data.get("events", [])],
            revision=data.get("revision", 1),
            canon_facts=data.get("canon_facts", {}),
            campaign_settings=CampaignSettings.from_dict(data["campaign_settings"]) if data.get("campaign_settings") else None,
            active_combat=data.get("active_combat", {}),
            skill_cooldowns=data.get("skill_cooldowns", {}),
            combat_log=data.get("combat_log", []),
        )


def create_initial_state(user_goal: str = "") -> GameState:
    """Create initial empty game state for a new session."""
    return GameState(
        revision=1,
        events=[],
        confirmed_event_log=[],
    )