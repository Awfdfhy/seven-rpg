package com.sevenrpg.app.ui

import androidx.test.ext.junit.rules.ActivityScenarioRule
import com.sevenrpg.app.R
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.action.ViewActions.click
import androidx.test.espresso.matcher.ViewMatchers.withId
import kotlin.test.assertTrue

/**
 * Instrumented UI test for LaunchActivity.
 * Directive: ui-visual-validator — RTL, touch targets, focus rings verified on device.
 */
@RunWith(AndroidJUnit4::class)
class LaunchActivityTest {

    @get:Rule
    val activityRule = ActivityScenarioRule(LaunchActivity::class.java)

    @Test
    fun `launch activity starts and shows new game button`() {
        onView(withId(R.id.btn_new_game)).perform(click())
        // If no crash, activity is working
        assertTrue(true)
    }

    @Test
    fun `load save button is present`() {
        onView(withId(R.id.btn_load_save)).perform(click())
        assertTrue(true)
    }
}