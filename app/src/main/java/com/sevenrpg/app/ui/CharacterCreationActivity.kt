package com.sevenrpg.app.ui

import android.content.Intent
import android.os.Bundle
import android.text.TextUtils
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.sevenrpg.app.databinding.ActivityCharacterCreationBinding
import com.sevenrpg.domain.DomainModule
import com.sevenrpg.domain.GameState
import com.sevenrpg.domain.PlayerCharacter

/**
 * Character Creation Screen — Create player character.
 * Directive: ui-visual-validator — RTL support, avatar preview, class selection.
 */
class CharacterCreationActivity : AppCompatActivity() {

    private lateinit var binding: ActivityCharacterCreationBinding
    private val aiProvider = DomainModule.createMockProvider()
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

        // Restore world from intent
        val worldJson = intent.getStringExtra("world") ?: "{}"
        gameState = gameState.copy()

        // Class selection
        binding.warriorOption.setOnClickListener { selectClass("warrior") }
        binding.mageOption.setOnClickListener { selectClass("mage") }
        binding.rogueOption.setOnClickListener { selectClass("rogue") }

        binding.etCharacterName.addTextChangedListener { validateForm() }

        binding.btnCreateCharacter.setOnClickListener {
            createCharacter()
        }

        binding.btnCancel.setOnClickListener {
            finish()
        }

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
        val isValid = name.isNotEmpty() && name.length <= 20 && selectedClass.isNotEmpty()
        binding.btnCreateCharacter.isEnabled = isValid

        if (name.isNotEmpty() && name.length > 20) {
            binding.etCharacterName.error = "اسم الشخصية طويل جداً (أقصى 20 حرف)"
        } else {
            binding.etCharacterName.error = null
        }
    }

    private fun createCharacter() {
        val name = binding.etCharacterName.text.toString().trim()
        if (name.isBlank()) return

        binding.btnCreateCharacter.isEnabled = false
        binding.btnCancel.isEnabled = false

        val player = PlayerCharacter(
            playerId = "player_${System.currentTimeMillis()}",
            name = name,
            identitySheet = mapOf("class" to selectedClass, "background" to "wanderer"),
            attributes = mapOf("strength" to 12, "agility" to 10, "intelligence" to 8),
            worldId = gameState.world?.worldId ?: ""
        )
        gameState = gameState.copy(player = player)

        // Simulate async save
        binding.root.postDelayed({
            navigateToSceneEntry()
        }, 800)
    }

    private fun navigateToSceneEntry() {
        val intent = Intent(this, SceneEntryActivity::class.java)
        intent.putExtra("gameState", gameState.toMap().toString())
        startActivity(intent)
    }
}