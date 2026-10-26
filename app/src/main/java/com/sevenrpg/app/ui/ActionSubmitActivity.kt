package com.sevenrpg.app.ui

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.widget.addTextChangedListener
import com.sevenrpg.app.AIConnectionStore
import com.sevenrpg.app.GameStateStore
import com.sevenrpg.app.OpenAICompatibleProvider
import com.sevenrpg.app.databinding.ActivityActionSubmitBinding
import com.sevenrpg.domain.DomainEvent
import com.sevenrpg.domain.DomainReducer
import com.sevenrpg.domain.GameState
import com.sevenrpg.domain.PlayerCommand

/** Submits the player's intent to a configured real AI provider; validated domain events remain authoritative. */
class ActionSubmitActivity : AppCompatActivity() {
    private lateinit var binding: ActivityActionSubmitBinding
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

        val player = gameState.player
        val scene = gameState.scene
        val world = gameState.world
        if (player == null || scene == null || world == null) {
            Toast.makeText(this, "لا توجد حملة مكتملة. ابدأ لعبة جديدة.", Toast.LENGTH_LONG).show()
            return
        }

        val config = AIConnectionStore.load(this)
        if (config == null) {
            Toast.makeText(this, "اضبط اتصال AI ومفتاح API قبل تنفيذ الأفعال.", Toast.LENGTH_LONG).show()
            startActivity(Intent(this, AISettingsActivity::class.java))
            return
        }

        val stateSnapshot = gameState
        val command = PlayerCommand.create(
            playerId = player.playerId,
            sceneId = scene.sceneId,
            action = actionText,
            revisionBase = stateSnapshot.revision
        )
        val commandValidation = DomainReducer.validateCommand(command, stateSnapshot)
        if (!commandValidation.isValid) {
            Toast.makeText(this, commandValidation.errors.firstOrNull() ?: "خطأ في التحقق", Toast.LENGTH_LONG).show()
            return
        }

        val context = mapOf<String, Any>(
            "worldId" to world.worldId,
            "worldName" to world.name,
            "worldCanonFacts" to world.canonFacts,
            "playerId" to player.playerId,
            "playerName" to player.name,
            "characterClass" to (player.identitySheet["class"] ?: "unknown"),
            "characterAttributes" to player.attributes,
            "sceneId" to scene.sceneId,
            "gameCanonFacts" to stateSnapshot.canonFacts,
            "characterKnowledge" to stateSnapshot.characterKnowledge,
            "characterBeliefs" to stateSnapshot.characterBeliefs,
            "stateRevision" to stateSnapshot.revision
        )

        binding.btnExecute.isEnabled = false
        binding.btnCancel.isEnabled = false
        binding.responseText.text = "جارٍ الاتصال بنموذج الذكاء الاصطناعي…"
        binding.responseCard.visibility = View.VISIBLE

        Thread {
            val result = runCatching {
                OpenAICompatibleProvider(config).generateNarrative(actionText, context, stateSnapshot.revision)
            }
            runOnUiThread {
                if (isFinishing || isDestroyed) return@runOnUiThread
                result.fold(
                    onSuccess = { proposal ->
                        val proposalValidation = DomainReducer.validateProposal(proposal.toMap(), stateSnapshot)
                        if (!proposalValidation.isValid) {
                            showFailure(proposalValidation.errors.firstOrNull() ?: "رفض مدقق الحالة اقتراح AI.")
                            return@fold
                        }

                        var nextState = stateSnapshot
                        var acceptedEvents = 0
                        for (eventData in proposal.events) {
                            val event = runCatching {
                                @Suppress("UNCHECKED_CAST")
                                DomainEvent.fromMap(eventData as Map<String, Any>)
                            }.getOrElse {
                                showFailure("عاد النموذج بحدث غير صالح؛ لم تُغيّر الحملة.")
                                return@fold
                            }
                            val (candidate, accepted) = DomainReducer.applyEvent(nextState, event)
                            if (!accepted) {
                                showFailure("رفض محرك القواعد الحدث؛ لم تُغيّر الحملة.")
                                return@fold
                            }
                            nextState = candidate
                            acceptedEvents++
                        }

                        if (acceptedEvents == 0) {
                            showFailure("لم ينتج النموذج حدثاً صالحاً؛ لم تُغيّر الحملة.")
                            return@fold
                        }
                        if (!GameStateStore.save(this, nextState)) {
                            showFailure("تعذّر تثبيت نتيجة الفعل في الحفظ الدائم.")
                            return@fold
                        }
                        gameState = nextState
                        binding.responseText.text = proposal.prose
                        binding.responseCard.visibility = View.VISIBLE
                        restoreButtons()
                    },
                    onFailure = { error ->
                        showFailure("فشل اتصال AI: ${error.message?.take(240) ?: "خطأ غير معروف"}. تحقق من الشبكة والرابط والمفتاح ورصيد المزود.")
                    }
                )
            }
        }.start()
    }

    private fun showFailure(message: String) {
        binding.responseText.text = message
        binding.responseCard.visibility = View.VISIBLE
        restoreButtons()
    }

    private fun restoreButtons() {
        binding.btnExecute.isEnabled = binding.etAction.text.toString().trim().length in 1..200
        binding.btnCancel.isEnabled = true
    }
}
