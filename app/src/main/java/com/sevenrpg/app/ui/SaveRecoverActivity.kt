package com.sevenrpg.app.ui

import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.sevenrpg.app.GameStateStore
import com.sevenrpg.app.databinding.ActivitySaveRecoverBinding
import com.sevenrpg.domain.GameState

/** Save screen backed by device-local persistent storage. */
class SaveRecoverActivity : AppCompatActivity() {
    private lateinit var binding: ActivitySaveRecoverBinding
    private var gameState = GameState.createInitial()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivitySaveRecoverBinding.inflate(layoutInflater)
        setContentView(binding.root)
        binding.root.layoutDirection = android.view.View.LAYOUT_DIRECTION_RTL
        gameState = GameStateStore.decode(intent.getStringExtra("gameState"))
            ?: GameStateStore.load(this)
            ?: GameState.createInitial()
        updateSaveInfo()

        binding.btnSaveNow.setOnClickListener { saveNow() }
        binding.btnBackToGame.setOnClickListener { finish() }
    }

    private fun updateSaveInfo() {
        val world = gameState.world?.name ?: "غير متوفر"
        val player = gameState.player?.name ?: "غير متوفر"
        binding.saveInfo.text = "العالم: $world | الشخصية: $player | المراجعة: ${gameState.revision}"
    }

    private fun saveNow() {
        binding.btnSaveNow.isEnabled = false
        binding.statusDot.setBackgroundResource(android.R.color.holo_orange_light)
        binding.statusText.text = "جاري الحفظ…"

        val isPlayable = gameState.world != null && gameState.player != null
        val success = isPlayable && GameStateStore.save(this, gameState)
        if (success) {
            binding.statusDot.setBackgroundResource(android.R.color.holo_green_light)
            binding.statusText.text = "تم الحفظ على الجهاز"
            Toast.makeText(this, "تم تثبيت الحفظ بنجاح.", Toast.LENGTH_LONG).show()
        } else {
            binding.statusDot.setBackgroundResource(android.R.color.holo_red_light)
            binding.statusText.text = "فشل الحفظ"
            Toast.makeText(this, "لا توجد حملة مكتملة لحفظها أو تعذرت الكتابة.", Toast.LENGTH_LONG).show()
        }
        binding.btnSaveNow.isEnabled = true
    }
}
