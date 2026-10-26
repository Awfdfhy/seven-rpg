const { test, expect } = require('@playwright/test');

test.beforeEach(async ({ page }) => {
  await page.goto('/');
  await page.evaluate(() => { localStorage.clear(); sessionStorage.clear(); });
  await page.reload();
});

test('campaign creation persists after reload and restores the same world and hero', async ({ page }) => {
  await page.getByLabel('اسم العالم').fill('ممالك الرماد');
  await page.getByLabel('قانون العالم / خلفيته').fill('السحر نادر، ولا يمكن إعادة الموتى.');
  await page.getByLabel('اسم الشخصية').fill('ليان');
  await page.getByRole('button', { name: 'إنشاء / بدء الحملة' }).click();

  await expect(page.getByText('ممالك الرماد', { exact: true })).toBeVisible();
  await expect(page.getByText(/ليان · warrior/)).toBeVisible();
  const before = await page.evaluate(() => JSON.parse(localStorage.getItem('seven_rpg_browser_save_v1')));
  expect(before.world.lore).toContain('السحر نادر');
  expect(before.revision).toBe(1);

  await page.reload();
  await expect(page.getByText('ممالك الرماد', { exact: true })).toBeVisible();
  await expect(page.getByText(/ليان · warrior/)).toBeVisible();
  const after = await page.evaluate(() => JSON.parse(localStorage.getItem('seven_rpg_browser_save_v1')));
  expect(after.world.id).toBe(before.world.id);
  expect(after.player.id).toBe(before.player.id);
});

test('AI action uses a real API-shaped request, validates result, and persists accepted event', async ({ page }) => {
  await page.route('https://openrouter.ai/api/v1/chat/completions', async route => {
    const request = route.request();
    const body = request.postDataJSON();
    expect(request.method()).toBe('POST');
    expect(request.headers()['authorization']).toBe('Bearer test-session-key');
    expect(body.model).toBe('openai/gpt-4.1-mini');
    expect(body.messages[1].content).toContain('افتح البوابة');
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ choices: [{ message: { content: 'تدور البوابة ببطء، وينكشف ممر حجري مضاء بمشاعل زرقاء.' } }] })
    });
  });

  await page.getByLabel('اسم العالم').fill('مدينة الليل');
  await page.getByLabel('اسم الشخصية').fill('ساهر');
  await page.getByRole('button', { name: 'إنشاء / بدء الحملة' }).click();
  await page.getByLabel(/مفتاح API/).fill('test-session-key');
  await page.getByLabel(/ما الذي تريد فعله/).fill('افتح البوابة');
  await page.getByRole('button', { name: 'نفّذ الفعل عبر AI' }).click();

  await expect(page.getByText(/تدور البوابة ببطء/)).toBeVisible();
  const saved = await page.evaluate(() => JSON.parse(localStorage.getItem('seven_rpg_browser_save_v1')));
  expect(saved.revision).toBe(2);
  expect(saved.events).toHaveLength(1);
  expect(saved.events[0].action).toBe('افتح البوابة');
  await page.reload();
  await expect(page.getByText(/تدور البوابة ببطء/)).toBeVisible();
});

test('AI failure does not mutate campaign state', async ({ page }) => {
  await page.route('https://openrouter.ai/api/v1/chat/completions', route =>
    route.fulfill({ status: 401, contentType: 'application/json', body: JSON.stringify({ error: { message: 'bad credentials' } }) })
  );
  await page.getByLabel('اسم العالم').fill('العالم');
  await page.getByLabel('اسم الشخصية').fill('البطل');
  await page.getByRole('button', { name: 'إنشاء / بدء الحملة' }).click();
  await page.getByLabel(/مفتاح API/).fill('bad-key');
  await page.getByLabel(/ما الذي تريد فعله/).fill('اقفز فوق الجدار');
  await page.getByRole('button', { name: 'نفّذ الفعل عبر AI' }).click();
  await expect(page.getByRole('status').filter({ hasText: /لم تتغير الحملة: HTTP 401/ })).toBeVisible();
  const saved = await page.evaluate(() => JSON.parse(localStorage.getItem('seven_rpg_browser_save_v1')));
  expect(saved.revision).toBe(1);
  expect(saved.events).toHaveLength(0);
});

test('import rejects malformed saves without replacing the active campaign', async ({ page }) => {
  await page.getByLabel('اسم العالم').fill('الحملة الأصلية');
  await page.getByLabel('اسم الشخصية').fill('بطل');
  await page.getByRole('button', { name: 'إنشاء / بدء الحملة' }).click();
  const originalId = await page.evaluate(() => JSON.parse(localStorage.getItem('seven_rpg_browser_save_v1')).world.id);
  await page.locator('#importInput').setInputFiles({
    name: 'bad.json', mimeType: 'application/json',
    buffer: Buffer.from(JSON.stringify({ schema: 1, world: {}, player: {}, revision: -3, narrative: 12 }))
  });
  await expect(page.getByRole('status').filter({ hasText: /فشل الاستيراد/ })).toBeVisible();
  const after = await page.evaluate(() => JSON.parse(localStorage.getItem('seven_rpg_browser_save_v1')));
  expect(after.world.id).toBe(originalId);
});
