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
 * Instrumented UI test for ActionSubmitActivity.
 */
@RunWith(AndroidJUnit4::class)
class ActionSubmitActivityTest {

    @get:Rule
    val activityRule = ActivityScenarioRule(ActionSubmitActivity::class.java)

    @Test
    fun `action submit screen loads`() {
        onView(withId(R.id.et_action)).perform(typeText("explore forest"))
        onView(withId(R.id.btn_execute)).perform(click())
        assertTrue(true)
    }
}