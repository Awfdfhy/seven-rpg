package com.sevenrpg.app.ui

import android.content.Intent
import android.os.Bundle
import android.text.TextUtils
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.sevenrpg.app.databinding.ActivityActionSubmitBinding
import com.sevenrpg.domain.DomainModule
import com.sevenrpg.domain.GameState
import com.sevenrpg.domain.PlayerCommand
import com.sevenrpg.domain.Proposal
import com.sevenrpg.domain.ValidationResult
import com.sevenrpg.domain.DomainReducer

/**
 * Action Submit Screen — Submit player action.
 * Directive: multi-agent-architect — player controls consequential choices.
 * Directive: ui-visual-validator — RTL support, loading states, error handling.
 */
class ActionSubmitActivity : AppCompatActivity() {

    private lateinit var binding: ActivityActionSubmitBinding
    private val aiProvider = DomainModule.createMockProvider()
    private var gameState = GameState.createInitial()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityActionSubmitBinding.inflate(layoutInflater)
        setContentView(binding.root)

        binding.root.layoutDirection = android.view.View.LAYOUT_DIRECTION_RTL

        binding.etAction.addTextChangedListener { validateForm() }

        binding.btnExecute.setOnClickListener {
            executeAction()
        }

        binding.btnCancel.setOnClickListener {
            finish()
        }
    }

    private fun validateForm() {
        val text = binding.etAction.text.toString().trim()
        val len = text.length
        binding.charCounter.text = "$len / 200"
        binding.btnExecute.isEnabled = len.isInRange(1..200)

        if (text.isNotEmpty() && len > 200) {
            binding.etAction.error = "الإجراء طويل جداً (أقصى 200 حرف)"
        } else {
            binding.etAction.error = null
        }
    }

    private fun executeAction() {
        val actionText = binding.etAction.text.toString().trim()
        if (actionText.isBlank()) return

        binding.btnExecute.isEnabled = false
        binding.btnCancel.isEnabled = false
        binding.root.postDelayed({
            binding.loadingOverlay.visibility = android.view.View.VISIBLE
        }, 0)

        // Simulate AI provider call
        binding.root.postDelayed({
            binding.loadingOverlay.visibility = android.view.View.GONE

            // Validate command
            val command = PlayerCommand.create(
                playerId = gameState.player?.playerId ?: "",
                sceneId = gameState.scene?.sceneId ?: "",
                action = actionText,
                revisionBase = gameState.revision
            )

            val validationResult = DomainReducer.validateCommand(command, gameState)
            if (!validationResult.isValid) {
                Toast.makeText(this, validationResult.errors.firstOrNull() ?: "خطأ في التحقق", Toast.LENGTH_LONG).show()
                binding.btnExecute.isEnabled = true
                return
            }

            // Get narrative from mock AI
            val context = mapOf(
                "worldId" to gameState.world?.worldId ?: "",
                "playerId" to gameState.player?.playerId ?: "",
                "sceneId" to gameState.scene?.sceneId ?: ""
            )
            val proposal = aiProvider.generateNarrative(actionText, context, gameState.revision)

            // Validate proposal
            val proposalValidation = DomainReducer.validateProposal(proposal.toMap(), gameState)
            if (!proposalValidation.isValid) {
                Toast.makeText(this, proposalValidation.errors.firstOrNull() ?: "خطأ في التحقق من الاقتراح", Toast.LENGTH_LONG).show()
                binding.btnExecute.isEnabled = true
                return
            }

            // Apply events
            for (eventData in proposal.events) {
                val event = com.sevenrpg.domain.DomainEvent.fromMap(eventData as Map<String, Any>)
                val (newState, success) = DomainReducer.applyEvent(gameState, event)
                if (success) {
                    gameState = newState
                }
            }

            // Show response
            binding.responseText.text = proposal.prose
            binding.responseCard.visibility = android.view.View.VISIBLE
            binding.responseCard.scrollTo(0)

            binding.btnExecute.isEnabled = true
        }, 1500)
    }
}