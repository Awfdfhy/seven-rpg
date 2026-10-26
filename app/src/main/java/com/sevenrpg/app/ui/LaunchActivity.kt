package com.sevenrpg.app.ui

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import com.sevenrpg.app.databinding.ActivityLaunchBinding
import com.sevenrpg.domain.DomainModule
import com.sevenrpg.domain.GameState
import com.sevenrpg.domain.PlayerCommand
import com.sevenrpg.domain.ValidationResult
import com.sevenrpg.domain.DomainReducer

/**
 * Launch Screen — Entry point for Seven RPG MVP-0.
 * Directive: multi-agent-architect — one responsibility: launch screen only.
 * Directive: ui-visual-validator — RTL support, touch targets, focus rings.
 */
class LaunchActivity : AppCompatActivity() {

    private lateinit var binding: ActivityLaunchBinding
    private val aiProvider = DomainModule.createMockProvider()
    private var gameState = GameState.createInitial()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityLaunchBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // RTL support
        binding.root.layoutDirection = android.view.View.LAYOUT_DIRECTION_RTL

        binding.btnNewGame.setOnClickListener {
            startNewGame()
        }

        binding.btnLoadSave.setOnClickListener {
            loadExistingSave()
        }
    }

    private fun startNewGame() {
        binding.btnNewGame.isEnabled = false
        binding.btnLoadSave.isEnabled = false

        // Simulate async action
        binding.root.postDelayed({
            gameState = GameState.createInitial()
            navigateToWorldCreation()
        }, 800)
    }

    private fun loadExistingSave() {
        binding.btnNewGame.isEnabled = false
        binding.btnLoadSave.isEnabled = false

        // Simulate async load
        binding.root.postDelayed({
            // In production: load from DataStore/SQLite
            navigateToWorldCreation()
        }, 800)
    }

    private fun navigateToWorldCreation() {
        val intent = Intent(this, WorldCreationActivity::class.java)
        startActivity(intent)
    }
}