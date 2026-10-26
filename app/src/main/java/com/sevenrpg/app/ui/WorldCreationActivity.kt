package com.sevenrpg.app.ui

import android.content.Intent
import android.os.Bundle
import android.text.TextUtils
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.sevenrpg.app.databinding.ActivityWorldCreationBinding
import com.sevenrpg.domain.DomainModule
import com.sevenrpg.domain.GameState
import com.sevenrpg.domain.PlayerCharacter
import com.sevenrpg.domain.World

/**
 * World Creation Screen — Create new world with name.
 * Directive: ui-visual-validator — RTL support, form validation, error states.
 */
class WorldCreationActivity : AppCompatActivity() {

    private lateinit var binding: ActivityWorldCreationBinding
    private val aiProvider = DomainModule.createMockProvider()
    private var gameState = GameState.createInitial()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityWorldCreationBinding.inflate(layoutInflater)
        setContentView(binding.root)

        binding.root.layoutDirection = android.view.View.LAYOUT_DIRECTION_RTL

        binding.etWorldName.addTextChangedListener { validateForm() }

        binding.btnCreateWorld.setOnClickListener {
            createWorld()
        }

        binding.btnCancel.setOnClickListener {
            finish()
        }
    }

    private fun validateForm() {
        val name = binding.etWorldName.text.toString().trim()
        val isValid = name.isNotEmpty() && name.length <= 30
        binding.btnCreateWorld.isEnabled = isValid

        if (name.isNotEmpty() && name.length > 30) {
            binding.etWorldName.error = "اسم العالم طويل جداً (أقصى 30 حرف)"
        } else {
            binding.etWorldName.error = null
        }
    }

    private fun createWorld() {
        val name = binding.etWorldName.text.toString().trim()
        if (name.isBlank()) return

        binding.btnCreateWorld.isEnabled = false
        binding.btnCancel.isEnabled = false

        // Simulate async save
        binding.root.postDelayed({
            val world = World(
                worldId = "world_${System.currentTimeMillis()}",
                name = name,
                canonFacts = mapOf("magic_system" to "elemental", "time_of_day" to "dawn"),
                version = 1,
                isolated = true
            )
            gameState = gameState.copy(world = world)
            navigateToCharacterCreation()
        }, 1000)
    }

    private fun navigateToCharacterCreation() {
        val intent = Intent(this, CharacterCreationActivity::class.java)
        intent.putExtra("world", worldJson)
        startActivity(intent)
    }

    private val worldJson: String
        get() = gameState.world?.let { world ->
            """{"worldId":"${world.worldId}","name":"${world.name}","canonFacts":${world.canonFacts.toString()},"version":${world.version}}"""
        } ?: "{}"
}