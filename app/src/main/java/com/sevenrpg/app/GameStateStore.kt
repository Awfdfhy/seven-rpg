package com.sevenrpg.app

import android.content.Context
import com.sevenrpg.domain.GameState
import org.json.JSONArray
import org.json.JSONObject

/**
 * Device-local persistence for the current campaign and an isolated in-progress draft.
 * Saves are committed synchronously so the UI only reports success after storage confirms it.
 */
object GameStateStore {
    private const val PREFS = "seven_rpg_local_state"
    private const val SAVED_STATE = "saved_game_state_json"
    private const val DRAFT_STATE = "draft_game_state_json"

    fun encode(state: GameState): String = JSONObject(state.toMap()).toString()

    fun decode(json: String?): GameState? {
        if (json.isNullOrBlank()) return null
        return runCatching { GameState.fromMap(toMap(JSONObject(json))) }.getOrNull()
    }

    fun save(context: Context, state: GameState): Boolean =
        prefs(context).edit().putString(SAVED_STATE, encode(state)).commit()

    fun load(context: Context): GameState? = decode(prefs(context).getString(SAVED_STATE, null))

    fun saveDraft(context: Context, state: GameState): Boolean =
        prefs(context).edit().putString(DRAFT_STATE, encode(state)).commit()

    fun loadDraft(context: Context): GameState? = decode(prefs(context).getString(DRAFT_STATE, null))

    fun clearDraft(context: Context): Boolean = prefs(context).edit().remove(DRAFT_STATE).commit()

    private fun prefs(context: Context) =
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)

    private fun toMap(json: JSONObject): Map<String, Any> {
        val result = linkedMapOf<String, Any>()
        val keys = json.keys()
        while (keys.hasNext()) {
            val key = keys.next()
            convert(json.opt(key))?.let { result[key] = it }
        }
        return result
    }

    private fun convert(value: Any?): Any? = when (value) {
        null, JSONObject.NULL -> null
        is JSONObject -> toMap(value)
        is JSONArray -> {
            val items = ArrayList<Any>()
            for (i in 0 until value.length()) {
                convert(value.opt(i))?.let(items::add)
            }
            items
        }
        else -> value
    }
}
