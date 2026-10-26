package com.sevenrpg.app.ui

import android.content.Intent
import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.widget.addTextChangedListener
import com.sevenrpg.app.GameStateStore
import com.sevenrpg.app.databinding.ActivityWorldCreationBinding
import com.sevenrpg.domain.GameState
import com.sevenrpg.domain.World

/** Create an isolated world and preserve it as a draft before character setup. */
class WorldCreationActivity : AppCompatActivity() {
    private lateinit var binding: ActivityWorldCreationBinding
    private var gameState = GameState.createInitial()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityWorldCreationBinding.inflate(layoutInflater)
        setContentView(binding.root)
        binding.root.layoutDirection = android.view.View.LAYOUT_DIRECTION_RTL
        gameState = GameStateStore.loadDraft(this) ?: GameState.createInitial()

        binding.etWorldName.addTextChangedListener { validateForm() }
        binding.btnCreateWorld.setOnClickListener { createWorld() }
        binding.btnCancel.setOnClickListener { finish() }
        validateForm()
    }

    private fun validateForm() {
        val name = binding.etWorldName.text.toString().trim()
        binding.btnCreateWorld.isEnabled = name.isNotEmpty() && name.length <= 30
        binding.etWorldName.error =
            if (name.length > 30) "اسم العالم طويل جداً (أقصى 30 حرف)" else null
    }

    private fun createWorld() {
        val name = binding.etWorldName.text.toString().trim()
        if (name.isBlank() || name.length > 30) return

        binding.btnCreateWorld.isEnabled = false
        binding.btnCancel.isEnabled = false
        val world = World(
            worldId = "world_${System.currentTimeMillis()}",
            name = name,
            canonFacts = mapOf("magic_system" to "elemental", "time_of_day" to "dawn"),
            version = 1,
            isolated = true
        )
        gameState = gameState.copy(world = world)
        if (!GameStateStore.saveDraft(this, gameState)) {
            Toast.makeText(this, "تعذّر حفظ مسودة العالم. حاول مجدداً.", Toast.LENGTH_LONG).show()
            binding.btnCreateWorld.isEnabled = true
            binding.btnCancel.isEnabled = true
            return
        }
        startActivity(Intent(this, CharacterCreationActivity::class.java)
            .putExtra("gameState", GameStateStore.encode(gameState)))
    }
}
