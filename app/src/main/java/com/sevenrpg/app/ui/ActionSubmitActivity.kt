package com.sevenrpg.app.ui

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.widget.addTextChangedListener
import com.sevenrpg.app.GameStateStore
import com.sevenrpg.app.databinding.ActivityActionSubmitBinding
import com.sevenrpg.domain.DomainModule
import com.sevenrpg.domain.DomainEvent
import com.sevenrpg.domain.DomainReducer
import com.sevenrpg.domain.GameState
import com.sevenrpg.domain.PlayerCommand

/** Submit a player-controlled action and persist only reducer-accepted state changes. */
class ActionSubmitActivity : AppCompatActivity() {
    private lateinit var binding: ActivityActionSubmitBinding
    private val aiProvider = DomainModule.createMockProvider()
    private var gameState = GameState.createInitial()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityActionSubmitBinding.inflate(layoutInflater)
        setContentView(binding.root)
        binding.root.layoutDirection = View.LAYOUT_DIRECTION_RTL
        gameState = GameStateStore.decode(intent.getStringExtra("gameState"))
            ?: GameStateStore.load(this)
            ?: GameState.createInitial()

        binding.etAction.addTextChangedListener { validateForm() }
        binding.btnExecute.setOnClickListener { executeAction() }
        binding.btnCancel.setOnClickListener { finish() }
        validateForm()
    }

    private fun validateForm() {
        val length = binding.etAction.text.toString().trim().length
        binding.charCounter.text = "$length / 200"
        binding.btnExecute.isEnabled = length in 1..200
        binding.etAction.error =
            if (length > 200) "الإجراء طويل جداً (أقصى 200 حرف)" else null
    }

    private fun executeAction() {
        val actionText = binding.etAction.text.toString().trim()
        if (actionText.isBlank() || actionText.length > 200) return
        if (gameState.player == null || gameState.scene == null || gameState.world == null) {
            Toast.makeText(this, "لا توجد حملة مكتملة. ابدأ لعبة جديدة.", Toast.LENGTH_LONG).show()
            return
        }

        binding.btnExecute.isEnabled = false
        binding.btnCancel.isEnabled = false
        binding.loadingOverlay.visibility = View.VISIBLE
        binding.root.postDelayed({
            binding.loadingOverlay.visibility = View.GONE
            val command = PlayerCommand.create(
                playerId = gameState.player.playerId,
                sceneId = gameState.scene.sceneId,
                action = actionText,
                revisionBase = gameState.revision
            )
            val commandValidation = DomainReducer.validateCommand(command, gameState)
            if (!commandValidation.isValid) {
                Toast.makeText(this, commandValidation.errors.firstOrNull() ?: "خطأ في التحقق", Toast.LENGTH_LONG).show()
                restoreButtons()
                return@postDelayed
            }

            val context = mapOf(
                "worldId" to gameState.world.worldId,
                "playerId" to gameState.player.playerId,
                "sceneId" to gameState.scene.sceneId
            )
            val proposal = aiProvider.generateNarrative(actionText, context, gameState.revision)
            val proposalValidation = DomainReducer.validateProposal(proposal.toMap(), gameState)
            if (!proposalValidation.isValid) {
                Toast.makeText(this, proposalValidation.errors.firstOrNull() ?: "خطأ في التحقق من الاقتراح", Toast.LENGTH_LONG).show()
                restoreButtons()
                return@postDelayed
            }

            for (eventData in proposal.events) {
                @Suppress("UNCHECKED_CAST")
                val event = DomainEvent.fromMap(eventData as Map<String, Any>)
                val (newState, accepted) = DomainReducer.applyEvent(gameState, event)
                if (accepted) gameState = newState
            }

            if (!GameStateStore.save(this, gameState)) {
                Toast.makeText(this, "تعذّر تثبيت الحالة الجديدة على الجهاز.", Toast.LENGTH_LONG).show()
            }
            binding.responseText.text = proposal.prose
            binding.responseCard.visibility = View.VISIBLE
            binding.responseCard.scrollTo(0)
            restoreButtons()
        }, 250)
    }

    private fun restoreButtons() {
        binding.btnExecute.isEnabled = true
        binding.btnCancel.isEnabled = true
    }
}
