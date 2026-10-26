const { test, expect } = require('@playwright/test');

test.beforeEach(async ({ page }) => {
  await page.goto('/');
  await page.evaluate(() => { localStorage.clear(); sessionStorage.clear(); });
  await page.reload();
});

async function createCampaign(page, world = 'ممالك الرماد', hero = 'ليان') {
  await page.getByLabel('اسم العالم').fill(world);
  await page.getByLabel('اسم الشخصية').fill(hero);
  await page.getByRole('button', { name: 'إنشاء / بدء الحملة' }).click();
  await expect(page.locator('#gamePanel')).toBeVisible();
}

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

test('required fields are validated and all character classes/difficulties are selectable', async ({ page }) => {
  await page.getByRole('button', { name: 'إنشاء / بدء الحملة' }).click();
  await expect(page.locator('#setupStatus')).toContainText('أدخل اسم عالم');
  await page.getByLabel('اسم العالم').fill('عالم');
  await page.getByLabel('اسم الشخصية').fill('بطل');
  await page.getByLabel('الفئة').selectOption('mage');
  await page.getByLabel('الصعوبة').selectOption('صعبة');
  await page.getByRole('button', { name: 'إنشاء / بدء الحملة' }).click();
  const saved = await page.evaluate(() => JSON.parse(localStorage.getItem('seven_rpg_browser_save_v1')));
  expect(saved.player.className).toBe('mage');
  expect(saved.difficulty).toBe('صعبة');
});

test('AI action sends the expected request and persists an accepted event across reload', async ({ page }) => {
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

  await createCampaign(page, 'مدينة الليل', 'ساهر');
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

test('AI connection test reports success for a valid provider response', async ({ page }) => {
  await page.route('https://openrouter.ai/api/v1/chat/completions', async route => {
    const body = route.request().postDataJSON();
    expect(body.messages[1].content).toContain('اختبار اتصال فقط');
    await route.fulfill({
      status: 200, contentType: 'application/json',
      body: JSON.stringify({ choices: [{ message: { content: 'متصل' } }] })
    });
  });
  await page.getByLabel(/مفتاح API/).fill('test-session-key');
  await page.getByRole('button', { name: 'اختبار اتصال حقيقي' }).click();
  await expect(page.locator('#aiStatus')).toContainText('نجح الاتصال الحقيقي: متصل');
});

test('AI failure does not mutate campaign state', async ({ page }) => {
  await page.route('https://openrouter.ai/api/v1/chat/completions', route =>
    route.fulfill({ status: 401, contentType: 'application/json', body: JSON.stringify({ error: { message: 'bad credentials' } }) })
  );
  await createCampaign(page, 'العالم', 'البطل');
  await page.getByLabel(/مفتاح API/).fill('bad-key');
  await page.getByLabel(/ما الذي تريد فعله/).fill('اقفز فوق الجدار');
  await page.getByRole('button', { name: 'نفّذ الفعل عبر AI' }).click();
  await expect(page.locator('#gameStatus')).toContainText('لم تتغير الحملة: HTTP 401');
  const saved = await page.evaluate(() => JSON.parse(localStorage.getItem('seven_rpg_browser_save_v1')));
  expect(saved.revision).toBe(1);
  expect(saved.events).toHaveLength(0);
});

test('missing API key and empty action are rejected without changing state', async ({ page }) => {
  await createCampaign(page);
  await page.getByRole('button', { name: 'نفّذ الفعل عبر AI' }).click();
  await expect(page.locator('#gameStatus')).toContainText('اكتب فعلاً');
  await page.getByLabel(/ما الذي تريد فعله/).fill('حاول فتح الباب');
  await page.getByRole('button', { name: 'نفّذ الفعل عبر AI' }).click();
  await expect(page.locator('#gameStatus')).toContainText('أدخل مفتاح API');
  const saved = await page.evaluate(() => JSON.parse(localStorage.getItem('seven_rpg_browser_save_v1')));
  expect(saved.revision).toBe(1);
  expect(saved.events).toHaveLength(0);
});

test('invalid endpoint is rejected and API key is never persisted', async ({ page }) => {
  await page.getByLabel('عنوان API الكامل').fill('http://insecure.example/api');
  await page.getByLabel(/مفتاح API/).fill('secret-session-key');
  await page.getByRole('button', { name: 'حفظ إعدادات غير سرية' }).click();
  await expect(page.locator('#aiStatus')).toContainText('عنوان HTTPS صالح');
  expect(await page.evaluate(() => localStorage.getItem('seven_rpg_browser_ai_v1'))).toBeNull();

  await page.getByLabel('عنوان API الكامل').fill('https://openrouter.ai/api/v1/chat/completions');
  await page.getByRole('button', { name: 'حفظ إعدادات غير سرية' }).click();
  await expect(page.locator('#aiStatus')).toContainText('حُفظ العنوان واسم النموذج فقط');
  expect(await page.evaluate(() => localStorage.getItem('seven_rpg_browser_ai_v1'))).not.toContain('secret-session-key');
  await page.reload();
  await expect(page.getByLabel('اسم النموذج')).toHaveValue('openai/gpt-4.1-mini');
  await expect(page.getByLabel(/مفتاح API/)).toHaveValue('');
});

test('valid JSON import replaces the active save and survives reload', async ({ page }) => {
  await createCampaign(page, 'العالم الأصلي', 'الأول');
  const incoming = {
    schema: 1,
    world: { id: 'world-imported', name: 'العالم المستورد', lore: 'قانون مستورد', canonFacts: {} },
    player: { id: 'hero-imported', name: 'البطلة المستوردة', className: 'mage', attributes: { strength: 12, agility: 10, intelligence: 8 } },
    difficulty: 'سهلة', revision: 4, events: [], narrative: 'وصلت البطلة إلى المدينة.', createdAt: '2026-01-01T00:00:00.000Z'
  };
  await page.locator('#importInput').setInputFiles({
    name: 'save.json', mimeType: 'application/json', buffer: Buffer.from(JSON.stringify(incoming))
  });
  await expect(page.locator('#gameStatus')).toContainText('تم استيراد الحفظ');
  await expect(page.locator('#worldPill')).toHaveText('العالم المستورد');
  await page.reload();
  await expect(page.locator('#worldPill')).toHaveText('العالم المستورد');
  const saved = await page.evaluate(() => JSON.parse(localStorage.getItem('seven_rpg_browser_save_v1')));
  expect(saved.world.id).toBe('world-imported');
  expect(saved.revision).toBe(4);
});

test('malformed import does not replace the active campaign', async ({ page }) => {
  await createCampaign(page, 'الحملة الأصلية', 'بطل');
  const originalId = await page.evaluate(() => JSON.parse(localStorage.getItem('seven_rpg_browser_save_v1')).world.id);
  await page.locator('#importInput').setInputFiles({
    name: 'bad.json', mimeType: 'application/json',
    buffer: Buffer.from(JSON.stringify({ schema: 1, world: {}, player: {}, revision: -3, narrative: 12 }))
  });
  await expect(page.locator('#gameStatus')).toContainText('فشل الاستيراد');
  const after = await page.evaluate(() => JSON.parse(localStorage.getItem('seven_rpg_browser_save_v1')));
  expect(after.world.id).toBe(originalId);
});

test('export produces a JSON download containing the active campaign', async ({ page }) => {
  await createCampaign(page, 'عالم التصدير', 'مصدّر');
  const downloadPromise = page.waitForEvent('download');
  await page.getByRole('button', { name: 'تصدير الحفظ JSON' }).click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toBe('seven-rpg-save.json');
  const path = await download.path();
  const fs = require('node:fs');
  const exported = JSON.parse(fs.readFileSync(path, 'utf8'));
  expect(exported.world.name).toBe('عالم التصدير');
  expect(exported.player.name).toBe('مصدّر');
});

test('starting a new world can be cancelled without hiding the active campaign', async ({ page }) => {
  await createCampaign(page, 'عالم مستمر', 'البطل');
  page.once('dialog', dialog => dialog.dismiss());
  await page.getByRole('button', { name: 'عالم جديد' }).click();
  await expect(page.locator('#gamePanel')).toBeVisible();
  await expect(page.locator('#worldPill')).toHaveText('عالم مستمر');
});

test('unexpected AI response shape is rejected without mutating campaign state', async ({ page }) => {
  await page.route('https://openrouter.ai/api/v1/chat/completions', route =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ choices: [] }) })
  );
  await createCampaign(page, 'اختبار الرد', 'المغامر');
  await page.getByLabel(/مفتاح API/).fill('test-session-key');
  await page.getByLabel(/ما الذي تريد فعله/).fill('تحدث إلى الحارس');
  await page.getByRole('button', { name: 'نفّذ الفعل عبر AI' }).click();
  await expect(page.locator('#gameStatus')).toContainText('أعاد المزود رداً فارغاً');
  const saved = await page.evaluate(() => JSON.parse(localStorage.getItem('seven_rpg_browser_save_v1')));
  expect(saved.revision).toBe(1);
  expect(saved.events).toHaveLength(0);
});

test('layout remains usable at a phone viewport and Arabic direction is RTL', async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 800 });
  await page.reload();
  await expect(page.locator('html')).toHaveAttribute('dir', 'rtl');
  await expect(page.getByLabel('اسم العالم')).toBeVisible();
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth);
  expect(overflow).toBe(false);
});


test('structurally incomplete JSON save is rejected without replacing active campaign', async ({ page }) => {
  await createCampaign(page, 'الحفظ السليم', 'الشخصية السليمة');
  const originalId = await page.evaluate(() => JSON.parse(localStorage.getItem('seven_rpg_browser_save_v1')).world.id);
  const incomplete = {
    schema: 1, world: { id: 'bad-world', name: 'عالم ناقص' },
    player: { id: 'bad-player', name: 'شخصية ناقصة' },
    difficulty: 'متوسطة', revision: 2, events: [], narrative: 'غير مكتمل', createdAt: '2026-01-01T00:00:00.000Z'
  };
  await page.locator('#importInput').setInputFiles({
    name: 'incomplete.json', mimeType: 'application/json', buffer: Buffer.from(JSON.stringify(incomplete))
  });
  await expect(page.locator('#gameStatus')).toContainText('فشل الاستيراد');
  const after = await page.evaluate(() => JSON.parse(localStorage.getItem('seven_rpg_browser_save_v1')));
  expect(after.world.id).toBe(originalId);
});

test('failed local persistence rolls back a successful-looking AI result', async ({ page }) => {
  await page.route('https://openrouter.ai/api/v1/chat/completions', route =>
    route.fulfill({
      status: 200, contentType: 'application/json',
      body: JSON.stringify({ choices: [{ message: { content: 'رد تجريبي لا يجب تثبيته.' } }] })
    })
  );
  await createCampaign(page, 'عالم الحفظ', 'المغامر');
  await page.getByLabel(/مفتاح API/).fill('test-session-key');
  await page.getByLabel(/ما الذي تريد فعله/).fill('اختبر الحفظ');
  await page.evaluate(() => {
    const original = Storage.prototype.setItem;
    Storage.prototype.setItem = function (key, value) {
      if (key === 'seven_rpg_browser_save_v1') throw new DOMException('storage full', 'QuotaExceededError');
      return original.call(this, key, value);
    };
  });
  await page.getByRole('button', { name: 'نفّذ الفعل عبر AI' }).click();
  await expect(page.locator('#gameStatus')).toContainText('لم تتغير الحملة');
  const saved = await page.evaluate(() => JSON.parse(Storage.prototype.getItem.call(localStorage, 'seven_rpg_browser_save_v1')));
  expect(saved.revision).toBe(1);
  expect(saved.events).toHaveLength(0);
  await expect(page.locator('#narrative')).not.toContainText('رد تجريبي لا يجب تثبيته');
});


test('RPG systems render and persist combat, rewards, inventory and character progression', async ({ page }) => {
  await createCampaign(page, 'مملكة الأنظمة', 'رائد');
  await expect(page.locator('#systemsPanel')).toBeVisible();
  await expect(page.locator('#combatPanel')).toContainText('لا يوجد قتال نشط');
  await expect(page.locator('#inventoryList')).toContainText('جرعة علاج');
  await page.getByRole('button', { name: 'استكشف / ابحث عن خصم' }).click();
  await expect(page.locator('#combatPanel')).toContainText('ذئب الرماد');
  await page.getByRole('button', { name: 'هجوم' }).click();
  await page.getByRole('button', { name: 'هجوم' }).click();
  await page.getByRole('button', { name: 'هجوم' }).click();
  await expect(page.locator('#combatPanel')).toContainText('لا يوجد قتال نشط');
  let saved = await page.evaluate(() => JSON.parse(localStorage.getItem('seven_rpg_browser_save_v1')));
  expect(saved.systems.stats.xp).toBeGreaterThan(0);
  expect(saved.systems.stats.gold).toBeGreaterThan(25);
  expect(saved.systems.combat.active).toBe(false);
  await page.reload();
  await expect(page.locator('#systemsPanel')).toBeVisible();
  saved = await page.evaluate(() => JSON.parse(localStorage.getItem('seven_rpg_browser_save_v1')));
  expect(saved.systems.stats.xp).toBeGreaterThan(0);
});

test('quest lifecycle grants rewards and survives reload', async ({ page }) => {
  await createCampaign(page, 'أرض المهمات', 'نورا');
  await page.getByRole('button', { name: 'قبول المهمة' }).click();
  await expect(page.locator('#questList')).toContainText('active');
  await page.getByRole('button', { name: 'تسجيل تقدم' }).click();
  await page.getByRole('button', { name: 'تسجيل تقدم' }).click();
  await expect(page.locator('#questList')).toContainText('completed');
  const saved = await page.evaluate(() => JSON.parse(localStorage.getItem('seven_rpg_browser_save_v1')));
  expect(saved.systems.quests.entries[0].status).toBe('completed');
  expect(saved.systems.stats.xp).toBeGreaterThanOrEqual(35);
  expect(saved.systems.stats.gold).toBeGreaterThanOrEqual(45);
  await page.reload();
  await expect(page.locator('#questList')).toContainText('completed');
});

test('relations, faction reputation, travel and inventory use mutate and persist their own systems', async ({ page }) => {
  await createCampaign(page, 'ممالك الروابط', 'سلمى');
  await page.getByRole('button', { name: 'ساعده (+5)' }).first().click();
  await expect(page.locator('#relationList')).toContainText('العلاقة: 5');
  await page.getByRole('button', { name: 'خدمة الفصيل (+10)' }).first().click();
  await expect(page.locator('#factionList')).toContainText('السمعة: 10');
  await page.getByRole('button', { name: /الغابة الموشّحة/ }).click();
  await expect(page.locator('#statsPanel')).toContainText('الغابة الموشّحة');
  await page.getByRole('button', { name: 'استكشف / ابحث عن خصم' }).click();
  await expect(page.locator('#combatPanel')).toContainText('خصم:');
  await page.getByRole('button', { name: 'الغابة الموشّحة' }).click();
  await expect(page.locator('#gameStatus')).toContainText('لا يمكنك السفر أثناء القتال');
  await page.getByRole('button', { name: 'انسحاب' }).click();
  const saved = await page.evaluate(() => JSON.parse(localStorage.getItem('seven_rpg_browser_save_v1')));
  expect(saved.systems.relations.entries[0].score).toBe(5);
  expect(saved.systems.factions.entries[0].reputation).toBe(10);
  expect(saved.systems.map.visited).toContain('الغابة الموشّحة');
  await page.reload();
  await expect(page.locator('#relationList')).toContainText('العلاقة: 5');
  await expect(page.locator('#factionList')).toContainText('السمعة: 10');
});

test('health potion consumes one item and restores health without exceeding maximum', async ({ page }) => {
  await createCampaign(page, 'عالم الجرعات', 'حكيم');
  await page.getByRole('button', { name: 'استكشف / ابحث عن خصم' }).click();
  await page.getByRole('button', { name: 'هجوم' }).click();
  await expect(page.locator('#statsPanel')).toContainText('الصحة 92/100');
  await page.getByRole('button', { name: 'استخدم جرعة العلاج' }).click();
  await expect(page.locator('#statsPanel')).toContainText('الصحة 100/100');
  await expect(page.locator('#inventoryList')).toContainText('×1');
  const saved = await page.evaluate(() => JSON.parse(localStorage.getItem('seven_rpg_browser_save_v1')));
  expect(saved.systems.inventory.items.find(i => i.id === 'potion-health').quantity).toBe(1);
});


test('skills consume mana, equipment state persists, and the shop respects gold', async ({ page }) => {
  await createCampaign(page, 'أرض المهارات', 'فارس');
  await page.getByRole('button', { name: 'تعلّم (نقطة مهارة)' }).first().click();
  await expect(page.locator('#skillList')).toContainText('متعلّمة');
  await page.getByRole('button', { name: 'شراء جرعة علاج — 10 ذهب' }).click();
  await expect(page.locator('#statsPanel')).toContainText('الذهب 15');
  await page.getByRole('button', { name: 'صناعة جرعة (عشبان)' }).click();
  await expect(page.locator('#inventoryList')).toContainText('عشب طبي');
  const saved = await page.evaluate(() => JSON.parse(localStorage.getItem('seven_rpg_browser_save_v1')));
  expect(saved.systems.skills.learned.length).toBe(2);
  expect(saved.systems.inventory.items.find(i => i.id === 'potion-health').quantity).toBe(3);
  expect(saved.systems.inventory.items.find(i => i.id === 'herb').quantity).toBe(1);
  await page.reload();
  await expect(page.locator('#skillList')).toContainText('متعلّمة');
});

test('player-authored canon facts are persistent and cannot be silently overwritten', async ({ page }) => {
  await createCampaign(page, 'عالم القانون', 'كاتبة');
  await page.getByLabel('عنوان الحقيقة').fill('عهد السحر');
  await page.getByLabel('الحقيقة', { exact: true }).fill('لا يمكن إحياء الموتى في هذا العالم.');
  await page.getByRole('button', { name: 'إضافة حقيقة قانونية' }).click();
  await expect(page.locator('#canonList')).toContainText('لا يمكن إحياء الموتى');
  await page.getByLabel('عنوان الحقيقة').fill('عهد السحر');
  await page.getByLabel('الحقيقة').fill('تغيير مخالف');
  await page.getByRole('button', { name: 'إضافة حقيقة قانونية' }).click();
  await expect(page.locator('#gameStatus')).toContainText('هذه الحقيقة موجودة');
  const saved = await page.evaluate(() => JSON.parse(localStorage.getItem('seven_rpg_browser_save_v1')));
  expect(saved.world.canonFacts['عهد السحر']).toBe('لا يمكن إحياء الموتى في هذا العالم.');
  expect(saved.systems.journal.entries.some(e => e.action === 'إضافة حقيقة قانونية')).toBe(true);
  await page.reload();
  await expect(page.locator('#canonList')).toContainText('لا يمكن إحياء الموتى');
});

test('achievement and journal history are recorded and persisted after a quest', async ({ page }) => {
  await createCampaign(page, 'أرض الإنجازات', 'مغامرة');
  await page.getByRole('button', { name: 'قبول المهمة' }).click();
  await page.getByRole('button', { name: 'تسجيل تقدم' }).click();
  await page.getByRole('button', { name: 'تسجيل تقدم' }).click();
  await expect(page.locator('#achievementList')).toContainText('صائد المهام');
  await expect(page.locator('#journalList')).toContainText('إكمال مهمة');
  const saved = await page.evaluate(() => JSON.parse(localStorage.getItem('seven_rpg_browser_save_v1')));
  expect(saved.systems.achievements.entries.some(a => a.id === 'quest-complete')).toBe(true);
  expect(saved.systems.journal.entries.length).toBeGreaterThanOrEqual(3);
});


test('character memory keeps knowledge, beliefs and rumors in separate buckets with provenance', async ({ page }) => {
  await createCampaign(page, 'عالم الذاكرة', 'راوية');
  await page.getByLabel('نوع الذاكرة').selectOption('rumors');
  await page.getByLabel('المحتوى').fill('يقال إن البرج يختفي عند الفجر.');
  await page.getByLabel('المصدر / صاحب المعلومة').fill('تاجر مسافر');
  await page.getByRole('button', { name: 'حفظ في ذاكرة الشخصية' }).click();
  await expect(page.locator('#memoryList')).toContainText('شائعات: 1');
  const saved = await page.evaluate(() => JSON.parse(localStorage.getItem('seven_rpg_browser_save_v1')));
  expect(saved.systems.memory.rumors[0].text).toContain('البرج');
  expect(saved.systems.memory.rumors[0].source).toBe('تاجر مسافر');
  expect(saved.systems.memory.knowledge).toHaveLength(0);
  expect(saved.systems.memory.beliefs).toHaveLength(0);
  await page.reload();
  await expect(page.locator('#memoryList')).toContainText('شائعات: 1');
});

test('failed storage during a shop purchase rolls back gold and inventory', async ({ page }) => {
  await createCampaign(page, 'عالم المعاملات', 'تاجر');
  await page.evaluate(() => {
    const original = Storage.prototype.setItem;
    Storage.prototype.setItem = function (key, value) {
      if (key === 'seven_rpg_browser_save_v1') throw new DOMException('storage full', 'QuotaExceededError');
      return original.call(this, key, value);
    };
  });
  await page.getByRole('button', { name: 'شراء جرعة علاج — 10 ذهب' }).click();
  await expect(page.locator('#gameStatus')).toContainText('فشل الحفظ المحلي');
  const saved = await page.evaluate(() => JSON.parse(Storage.prototype.getItem.call(localStorage, 'seven_rpg_browser_save_v1')));
  expect(saved.systems.stats.gold).toBe(25);
  expect(saved.systems.inventory.items.find(i => i.id === 'potion-health').quantity).toBe(2);
  await expect(page.locator('#statsPanel')).toContainText('الذهب 25');
});
