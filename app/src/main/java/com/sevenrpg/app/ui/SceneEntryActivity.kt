package com.sevenrpg.app.ui

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import com.sevenrpg.app.databinding.ActivitySceneEntryBinding
import com.sevenrpg.domain.DomainModule
import com.sevenrpg.domain.GameState
import com.sevenrpg.domain.PlayerCommand
import com.sevenrpg.domain.ValidationResult
import com.sevenrpg.domain.DomainReducer

/**
 * Scene Entry Screen — Enter game scene.
 * Directive: ui-visual-validator — RTL support, narrative display, async states.
 */
class SceneEntryActivity : AppCompatActivity() {

    private lateinit var binding: ActivitySceneEntryBinding
    private val aiProvider = DomainModule.createMockProvider()
    private var gameState = GameState.createInitial()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivitySceneEntryBinding.inflate(layoutInflater)
        setContentView(binding.root)

        binding.root.layoutDirection = android.view.View.LAYOUT_DIRECTION_RTL

        binding.btnSubmitAction.setOnClickListener {
            navigateToActionSubmit()
        }

        binding.btnBackToWorld.setOnClickListener {
            finish()
        }
    }

    private fun navigateToActionSubmit() {
        val intent = Intent(this, ActionSubmitActivity::class.java)
        intent.putExtra("gameState", gameState.toMap().toString())
        startActivity(intent)
    }
}