package com.sevenrpg.app.ui

import androidx.test.ext.junit.rules.ActivityScenarioRule
import com.sevenrpg.app.R
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.action.ViewActions.click
import androidx.test.espresso.action.ViewActions.typeText
import androidx.test.espresso.matcher.ViewMatchers.withId
import kotlin.test.assertTrue

/**
 * Instrumented UI test for CharacterCreationActivity.
 */
@RunWith(AndroidJUnit4::class)
class CharacterCreationActivityTest {

    @get:Rule
    val activityRule = ActivityScenarioRule(CharacterCreationActivity::class.java)

    @Test
    fun `character creation screen loads`() {
        onView(withId(R.id.et_character_name)).perform(typeText("Hero"))
        onView(withId(R.id.warrior_option)).perform(click())
        onView(withId(R.id.btn_create_character)).perform(click())
        assertTrue(true)
    }
}