package com.sevenrpg.app.ui

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import com.sevenrpg.app.databinding.ActivitySaveRecoverBinding
import com.sevenrpg.domain.DomainModule
import com.sevenrpg.domain.GameState

/**
 * Save Recover Screen — Atomic save with recovery.
 * Directive: ui-visual-validator — RTL support, save status, error states.
 */
class SaveRecoverActivity : AppCompatActivity() {

    private lateinit var binding: ActivitySaveRecoverBinding
    private val aiProvider = DomainModule.createMockProvider()
    private var gameState = GameState.createInitial()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivitySaveRecoverBinding.inflate(layoutInflater)
        setContentView(binding.root)

        binding.root.layoutDirection = android.view.View.LAYOUT_DIRECTION_RTL

        binding.btnSaveNow.setOnClickListener {
            saveNow()
        }

        binding.btnBackToGame.setOnClickListener {
            finish()
        }
    }

    private fun saveNow() {
        binding.btnSaveNow.isEnabled = false
        binding.statusDot.setBackgroundResource(android.R.color.holo_orange_light)
        binding.statusText.text = "جاري الحفظ…"

        // Simulate atomic save
        binding.root.postDelayed({
            val success = Math.random() < 0.7
            if (success) {
                binding.statusDot.setBackgroundResource(android.R.color.holo_green_light)
                binding.statusText.text = "تم الحفظ"
                binding.toastSuccess.visibility = android.view.View.VISIBLE
                binding.root.postDelayed({ binding.toastSuccess.visibility = android.view.View.GONE }, 3000)
            } else {
                binding.statusDot.setBackgroundResource(android.R.color.holo_red_light)
                binding.statusText.text = "فشل الحفظ"
                binding.toastError.visibility = android.view.View.VISIBLE
                binding.root.postDelayed({ binding.toastError.visibility = android.view.View.GONE }, 3000)
            }
            binding.btnSaveNow.isEnabled = true
        }, 1000)
    }
}