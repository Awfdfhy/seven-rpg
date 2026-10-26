package com.sevenrpg.app.ui

import android.content.Intent
import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.sevenrpg.app.GameStateStore
import com.sevenrpg.app.ui.AISettingsActivity
import com.sevenrpg.app.databinding.ActivityLaunchBinding
import com.sevenrpg.domain.GameState

/** Entry point for the Seven RPG MVP. */
class LaunchActivity : AppCompatActivity() {
    private lateinit var binding: ActivityLaunchBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityLaunchBinding.inflate(layoutInflater)
        setContentView(binding.root)
        binding.root.layoutDirection = android.view.View.LAYOUT_DIRECTION_RTL
        binding.btnNewGame.setOnClickListener { startNewGame() }
        binding.btnLoadSave.setOnClickListener { loadExistingSave() }
        binding.btnAiSettings.setOnClickListener { startActivity(Intent(this, AISettingsActivity::class.java)) }
    }

    private fun startNewGame() {
        val draft = GameState.createInitial()
        if (!GameStateStore.saveDraft(this, draft)) {
            Toast.makeText(this, "تعذّر بدء مسودة اللعبة على الجهاز.", Toast.LENGTH_LONG).show()
            return
        }
        startActivity(Intent(this, WorldCreationActivity::class.java))
    }

    private fun loadExistingSave() {
        val saved = GameStateStore.load(this)
        if (saved?.world == null || saved.player == null) {
            Toast.makeText(this, "لا يوجد حفظ صالح بعد. ابدأ لعبة جديدة أولاً.", Toast.LENGTH_LONG).show()
            return
        }
        startActivity(Intent(this, SceneEntryActivity::class.java)
            .putExtra("gameState", GameStateStore.encode(saved)))
    }
}
