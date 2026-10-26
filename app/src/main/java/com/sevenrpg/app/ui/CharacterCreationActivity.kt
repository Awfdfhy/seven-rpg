package com.sevenrpg.app.ui

import android.content.Intent
import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.widget.addTextChangedListener
import com.sevenrpg.app.GameStateStore
import com.sevenrpg.app.databinding.ActivityCharacterCreationBinding
import com.sevenrpg.domain.GameState
import com.sevenrpg.domain.PlayerCharacter
import com.sevenrpg.domain.Scene

/** Create a player character, then commit the first complete campaign save. */
class CharacterCreationActivity : AppCompatActivity() {
    private lateinit var binding: ActivityCharacterCreationBinding
    private var gameState = GameState.createInitial()
    private var selectedClass = "warrior"

    private val classIcons = mapOf(
        "warrior" to "محارب",
        "mage" to "ساحر",
        "rogue" to "لص"
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityCharacterCreationBinding.inflate(layoutInflater)
        setContentView(binding.root)
        binding.root.layoutDirection = android.view.View.LAYOUT_DIRECTION_RTL
        gameState = GameStateStore.decode(intent.getStringExtra("gameState"))
            ?: GameStateStore.loadDraft(this)
            ?: GameState.createInitial()

        binding.warriorOption.setOnClickListener { selectClass("warrior") }
        binding.mageOption.setOnClickListener { selectClass("mage") }
        binding.rogueOption.setOnClickListener { selectClass("rogue") }
        binding.etCharacterName.addTextChangedListener { validateForm() }
        binding.btnCreateCharacter.setOnClickListener { createCharacter() }
        binding.btnCancel.setOnClickListener { finish() }
        selectClass("warrior")
    }

    private fun selectClass(className: String) {
        selectedClass = className
        binding.avatarPreview.text = classIcons[className] ?: "شخصية"
        binding.warriorOption.isSelected = className == "warrior"
        binding.mageOption.isSelected = className == "mage"
        binding.rogueOption.isSelected = className == "rogue"
        validateForm()
    }

    private fun validateForm() {
        val name = binding.etCharacterName.text.toString().trim()
        binding.btnCreateCharacter.isEnabled =
            name.isNotEmpty() && name.length <= 20 && selectedClass.isNotEmpty()
        binding.etCharacterName.error =
            if (name.length > 20) "اسم الشخصية طويل جداً (أقصى 20 حرف)" else null
    }

    private fun createCharacter() {
        val name = binding.etCharacterName.text.toString().trim()
        if (name.isBlank() || name.length > 20) return
        val world = gameState.world
        if (world == null) {
            Toast.makeText(this, "أنشئ العالم أولاً.", Toast.LENGTH_LONG).show()
            return
        }

        binding.btnCreateCharacter.isEnabled = false
        binding.btnCancel.isEnabled = false
        val player = PlayerCharacter(
            playerId = "player_${System.currentTimeMillis()}",
            name = name,
            identitySheet = mapOf("class" to selectedClass, "background" to "wanderer"),
            attributes = mapOf("strength" to 12, "agility" to 10, "intelligence" to 8),
            worldId = world.worldId
        )
        val scene = Scene(
            sceneId = "scene_${System.currentTimeMillis()}",
            worldId = world.worldId,
            playerId = player.playerId,
            canonFactsLoaded = true
        )
        gameState = gameState.copy(player = player, scene = scene)
        if (!GameStateStore.save(this, gameState)) {
            Toast.makeText(this, "تعذّر تثبيت الحفظ على الجهاز.", Toast.LENGTH_LONG).show()
            binding.btnCreateCharacter.isEnabled = true
            binding.btnCancel.isEnabled = true
            return
        }
        GameStateStore.clearDraft(this)
        startActivity(Intent(this, SceneEntryActivity::class.java)
            .putExtra("gameState", GameStateStore.encode(gameState)))
        finish()
    }
}
