package com.sevenrpg.app.ui

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import com.sevenrpg.app.GameStateStore
import com.sevenrpg.app.databinding.ActivitySceneEntryBinding
import com.sevenrpg.domain.GameState
import com.sevenrpg.domain.Scene

/** Main play scene. The persisted campaign is the source of truth across Activity transitions. */
class SceneEntryActivity : AppCompatActivity() {
    private lateinit var binding: ActivitySceneEntryBinding
    private var gameState = GameState.createInitial()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivitySceneEntryBinding.inflate(layoutInflater)
        setContentView(binding.root)
        binding.root.layoutDirection = android.view.View.LAYOUT_DIRECTION_RTL

        gameState = GameStateStore.decode(intent.getStringExtra("gameState"))
            ?: GameStateStore.load(this)
            ?: GameState.createInitial()
        ensureScene()
        renderNarrative()

        binding.btnSubmitAction.setOnClickListener {
            startActivity(Intent(this, ActionSubmitActivity::class.java)
                .putExtra("gameState", GameStateStore.encode(gameState)))
        }
        binding.btnSaveGame.setOnClickListener {
            startActivity(Intent(this, SaveRecoverActivity::class.java)
                .putExtra("gameState", GameStateStore.encode(gameState)))
        }
        binding.btnBackToWorld.setOnClickListener { finish() }
    }

    override fun onResume() {
        super.onResume()
        val latest = GameStateStore.load(this)
        if (latest != null && latest.revision >= gameState.revision) {
            gameState = latest
            renderNarrative()
        }
    }

    private fun ensureScene() {
        val world = gameState.world ?: return
        val player = gameState.player ?: return
        if (gameState.scene == null) {
            gameState = gameState.copy(scene = Scene(
                sceneId = "scene_${System.currentTimeMillis()}",
                worldId = world.worldId,
                playerId = player.playerId,
                canonFactsLoaded = true
            ))
            GameStateStore.save(this, gameState)
        }
    }

    private fun renderNarrative() {
        val worldName = gameState.world?.name ?: "العالم المجهول"
        val playerName = gameState.player?.name ?: "المسافر"
        binding.narrativeText.text =
            "أنت ${playerName} في عالم «${worldName}». تستيقظ عند أطراف غابة قديمة، " +
            "وتتشعب أمامك طرق تؤدي إلى مدينة مضاءة وكهف غامض ونهر هادئ. " +
            "اختر فعلك التالي لتتابع المغامرة.\n\nتقدم الحملة: ${gameState.revision}"
    }
}
