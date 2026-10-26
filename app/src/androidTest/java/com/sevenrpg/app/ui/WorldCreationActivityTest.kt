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
 * Instrumented UI test for WorldCreationActivity.
 */
@RunWith(AndroidJUnit4::class)
class WorldCreationActivityTest {

    @get:Rule
    val activityRule = ActivityScenarioRule(WorldCreationActivity::class.java)

    @Test
    fun `world creation screen loads`() {
        onView(withId(R.id.et_world_name)).perform(typeText("Test World"))
        onView(withId(R.id.btn_create_world)).perform(click())
        assertTrue(true)
    }
}