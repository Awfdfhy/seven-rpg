package com.sevenrpg.app.ui

import android.graphics.Color
import android.os.Bundle
import android.text.InputType
import android.view.ViewGroup
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.sevenrpg.app.AIConnectionStore
import com.sevenrpg.app.OpenAICompatibleProvider

/** In-app provider configuration; the API key is kept encrypted in Android Keystore-backed storage. */
class AISettingsActivity : AppCompatActivity() {
    private lateinit var endpointInput: EditText
    private lateinit var modelInput: EditText
    private lateinit var keyInput: EditText
    private lateinit var statusText: TextView
    private lateinit var saveButton: Button
    private lateinit var testButton: Button

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val config = AIConnectionStore.load(this)
        val density = resources.displayMetrics.density
        fun dp(value: Int) = (value * density).toInt()

        val scroll = ScrollView(this).apply {
            setBackgroundColor(Color.rgb(17, 20, 28))
            isFillViewport = true
        }
        val content = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(20), dp(24), dp(20), dp(24))
            layoutDirection = android.view.View.LAYOUT_DIRECTION_RTL
        }
        scroll.addView(content)
        setContentView(scroll)

        content.addView(label("اتصال الذكاء الاصطناعي"))
        content.addView(label("يستخدم Seven RPG واجهة OpenAI-compatible. أدخل رابط Chat Completions، واسم النموذج، ومفتاح API الخاص بك."))
        endpointInput = field(
            "رابط API",
            config?.endpoint ?: AIConnectionStore.DEFAULT_ENDPOINT,
            InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_VARIATION_URI
        )
        modelInput = field(
            "اسم النموذج",
            config?.model ?: AIConnectionStore.DEFAULT_MODEL,
            InputType.TYPE_CLASS_TEXT
        )
        keyInput = field(
            "مفتاح API",
            config?.apiKey.orEmpty(),
            InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_VARIATION_PASSWORD
        )
        content.addView(endpointInput)
        content.addView(modelInput)
        content.addView(keyInput)

        statusText = label("المفتاح لا يظهر في السجلات ويُخزَّن مشفراً على هذا الجهاز.")
        content.addView(statusText)
        saveButton = button("حفظ الإعدادات")
        testButton = button("حفظ واختبار الاتصال الحقيقي")
        content.addView(saveButton)
        content.addView(testButton)
        content.addView(button("مسح بيانات الاتصال").apply {
            setOnClickListener {
                AIConnectionStore.clear(this@AISettingsActivity)
                endpointInput.setText(AIConnectionStore.DEFAULT_ENDPOINT)
                modelInput.setText(AIConnectionStore.DEFAULT_MODEL)
                keyInput.setText("")
                statusText.text = "تم مسح إعدادات الاتصال من هذا الجهاز."
            }
        })
        content.addView(button("رجوع").apply { setOnClickListener { finish() } })

        saveButton.setOnClickListener { saveSettings(showConfirmation = true) }
        testButton.setOnClickListener { testConnection() }
    }

    private fun label(text: String) = TextView(this).apply {
        this.text = text
        setTextColor(Color.rgb(240, 240, 245))
        textSize = 16f
        setPadding(0, 0, 0, 12)
    }

    private fun field(hintText: String, value: String, inputTypeValue: Int) = EditText(this).apply {
        hint = hintText
        setText(value)
        inputType = inputTypeValue
        setTextColor(Color.WHITE)
        setHintTextColor(Color.LTGRAY)
        setPadding(20, 16, 20, 16)
        setBackgroundColor(Color.rgb(37, 42, 55))
        layoutParams = LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            ViewGroup.LayoutParams.WRAP_CONTENT
        ).apply { bottomMargin = (12 * resources.displayMetrics.density).toInt() }
        if (hintText == "مفتاح API") {
            setSingleLine(true)
        }
    }

    private fun button(text: String) = Button(this).apply {
        this.text = text
        layoutParams = LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            ViewGroup.LayoutParams.WRAP_CONTENT
        ).apply { bottomMargin = (10 * resources.displayMetrics.density).toInt() }
    }

    private fun saveSettings(showConfirmation: Boolean): Boolean {
        val ok = AIConnectionStore.save(
            this,
            endpointInput.text.toString(),
            modelInput.text.toString(),
            keyInput.text.toString()
        )
        statusText.text = if (ok) {
            "حُفظت الإعدادات، وتم تشفير المفتاح محلياً."
        } else {
            "تعذّر الحفظ. تحقق من رابط HTTPS واسم النموذج ومفتاح API."
        }
        if (ok && showConfirmation) {
            android.widget.Toast.makeText(this, "تم حفظ إعدادات AI.", android.widget.Toast.LENGTH_SHORT).show()
        }
        return ok
    }

    private fun testConnection() {
        if (!saveSettings(showConfirmation = false)) return
        val config = AIConnectionStore.load(this) ?: run {
            statusText.text = "تعذّر قراءة إعدادات الاتصال بعد الحفظ."
            return
        }
        testButton.isEnabled = false
        saveButton.isEnabled = false
        statusText.text = "جارٍ اختبار الاتصال بالخدمة…"
        Thread {
            val result = runCatching {
                OpenAICompatibleProvider(config).generateNarrative(
                    goal = "هذا اختبار اتصال فقط. أجب بجملة قصيرة تؤكد أن الاتصال يعمل.",
                    context = mapOf("connection_test" to true),
                    revision = 1
                )
            }
            runOnUiThread {
                testButton.isEnabled = true
                saveButton.isEnabled = true
                statusText.text = result.fold(
                    onSuccess = { "نجح الاتصال الحقيقي بالنموذج. الرد: ${it.prose.take(180)}" },
                    onFailure = { "فشل الاختبار: ${it.message?.take(240) ?: "خطأ اتصال غير معروف"}" }
                )
            }
        }.start()
    }
}
