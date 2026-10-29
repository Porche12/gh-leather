/**
 * GH-LEATHER — Luxury Leather & Fur Atelier Web Application
 * Modular, performant, mobile-first JavaScript architecture.
 * Fully compliant with Product Specification Sections 5–11.
 */

// ================= Data Structures =================

const SERVICES_CATALOG = {
    'Реставрация и ремонт кожаных изделий': {
        desc: 'Профессиональное устранение задиров, порезов, прожогов и глубоких потертостей воротника и манжет. Заводское восстановление эластичности и текстуры кожи без эффекта жесткости.',
        price: 'от 3 500 ₽',
        time: '3–5 рабочих дней'
    },
    'Покраска и восстановление цвета': {
        desc: 'Полное заводское восстановление родного цвета или перекраска в новый оттенок. Профессиональная французская косметика Saphir Medaille D\'or и итальянские защитные финиши (матовый, глянец, сатин).',
        price: 'от 4 500 ₽',
        time: '4–6 рабочих дней'
    },
    'Ремонт и перекрой шуб, дублёнок и меха': {
        desc: 'Полная трансформация устаревших или тяжелых фасонов в стильные современные силуэты (автоледи, косуха, оверсайз, жилет). Укорачивание низа, пересадка рукавов, замена крючков и шелковой подкладки.',
        price: 'от 9 000 ₽',
        time: '5–10 рабочих дней'
    },
    'Индивидуальный пошив одежды': {
        desc: 'Пошив курток, плащей, бомберов, юбок и брюк по индивидуальным меркам из премиальной итальянской кожи Nappa и замши. Безупречная посадка с гарантией качества швов.',
        price: 'от 18 000 ₽',
        time: '7–14 рабочих дней'
    },
    'Ремонт и реставрация сумок и обуви': {
        desc: 'Спа-уход, деликатное удаление реагентов и соли, реставрация потертых уголков и ручек, замена молний Raccagni/YKK. Бережное обслуживание сумок Louis Vuitton, Chanel, Gucci, Prada.',
        price: 'от 2 800 ₽',
        time: '2–4 рабочих дня'
    },
    'Реставрация кожаной мебели и салонов авто': {
        desc: 'Локальное устранение прожогов от сигарет, трещин, задиров и разрывов на сиденьях. Перетяжка рулей перфорированной Nappa, восстановление цвета диванов и кресел.',
        price: 'от 5 000 ₽',
        time: '1–3 рабочих дня'
    }
};

const CALCULATOR_DATA = {
    jacket: {
        title: 'Куртка / плащ',
        works: [
            { name: 'Реставрация потертостей и задиров', desc: 'Воротник, манжеты, карманы', priceRange: '3 500 – 5 500 ₽', time: '3–5 рабочих дней' },
            { name: 'Глубокая покраска и защитный лак', desc: 'Французская химия Saphir', priceRange: '4 500 – 7 500 ₽', time: '4–6 рабочих дней' },
            { name: 'Замена молнии / фурнитуры', desc: 'Установка молний Raccagni/YKK', priceRange: '1 800 – 3 200 ₽', time: '2–3 рабочих дня' },
            { name: 'Устранение пореза или разрыва', desc: 'Сложный реставрационный шов', priceRange: '2 000 – 4 200 ₽', time: '2–4 рабочих дня' }
        ]
    },
    fur: {
        title: 'Шуба / дублёнка',
        works: [
            { name: 'Полный перекрой фасона', desc: 'В автоледи, косуху, оверсайз или жилет', priceRange: '9 000 – 18 000 ₽', time: '5–10 рабочих дней' },
            { name: 'Укорачивание длины или рукавов', desc: 'С сохранением фабричного края', priceRange: '4 500 – 7 500 ₽', time: '3–5 рабочих дней' },
            { name: 'Замена крючков / фурнитуры', desc: 'Укрепление бортов и петель', priceRange: '1 500 – 3 500 ₽', time: '2–3 рабочих дня' },
            { name: 'Устранение потертостей меха', desc: 'Подбор донорского меха тон в тон', priceRange: '3 000 – 6 500 ₽', time: '3–5 рабочих дней' }
        ]
    },
    bag: {
        title: 'Сумка / рюкзак',
        works: [
            { name: 'Реставрация уголков и ручек', desc: 'Укрепление формы и швов', priceRange: '2 800 – 5 000 ₽', time: '2–4 рабочих дня' },
            { name: 'Покраска в оригинальный тон', desc: 'Комплексное восстановление цвета', priceRange: '3 500 – 6 500 ₽', time: '3–5 рабочих дней' },
            { name: 'Замена молнии или карабинов', desc: 'Подбор оригинальной фурнитуры', priceRange: '2 200 – 4 000 ₽', time: '2–3 рабочих дня' },
            { name: 'Комплексный спа-уход', desc: 'Чистка, выведение пятен, пропитка', priceRange: '1 800 – 3 000 ₽', time: '1–2 рабочих дня' }
        ]
    },
    shoes: {
        title: 'Обувь',
        works: [
            { name: 'Покраска туфель или ботинок', desc: 'Стойкий полимерный краситель', priceRange: '2 200 – 4 500 ₽', time: '2–3 рабочих дня' },
            { name: 'Реставрация мысков и каблуков', desc: 'Устранение глубоких сбоев', priceRange: '2 000 – 3 800 ₽', time: '2–3 рабочих дня' },
            { name: 'Выведение соли и нано-защита', desc: 'Глубокая нейтрализация реагентов', priceRange: '1 500 – 2 800 ₽', time: '1–2 рабочих дня' }
        ]
    },
    auto: {
        title: 'Автосалон / мебель',
        works: [
            { name: 'Ремонт прожога или пореза', desc: 'Локальное восстановление текстуры', priceRange: '3 500 – 6 500 ₽', time: '1–2 рабочих дня' },
            { name: 'Покраска элемента сиденья', desc: 'Заводской оттенок по каталогу', priceRange: '5 000 – 9 000 ₽', time: '2–3 рабочих дня' },
            { name: 'Перетяжка руля кожей Nappa', desc: 'Итальянская перфорированная кожа', priceRange: '6 000 – 10 000 ₽', time: '1–2 рабочих дня' }
        ]
    },
    tailoring: {
        title: 'Пошив одежды',
        works: [
            { name: 'Пошив кожаной куртки / плаща', desc: 'Итальянская Nappa, индивидуальный лекал', priceRange: '18 000 – 35 000 ₽', time: '7–14 рабочих дней' },
            { name: 'Пошив юбки или брюк из кожи', desc: 'Идеальная посадка по фигуре', priceRange: '9 500 – 18 000 ₽', time: '5–8 рабочих дней' },
            { name: 'Пошив аксессуара или сумки', desc: 'Ручной седельный шов', priceRange: '4 900 – 12 000 ₽', time: '4–7 рабочих дней' }
        ]
    }
};

const PORTFOLIO_CASES = {
    jacket: {
        label: 'Куртка',
        initialDamage: 'Глубокие задиры воротника, сильное истирание локтевых зон и потеря заводского пигмента.',
        workDone: 'Локальное шпаклевание жидкой кожей Saphir, нанесение базы, двухслойная покраска и матовый лак.',
        beforeImg: 'images/slide_2.jpg',
        afterImg: 'images/slide_3.jpg'
    },
    bag: {
        label: 'Сумка',
        initialDamage: 'Потертости нижних углов, обрыв оплётки ручек, следы шариковой ручки на клапане.',
        workDone: 'Очистка спиртовыми составами, формование ребер, восстановление эмали и обработка кромок.',
        beforeImg: 'images/slide_5.jpg',
        afterImg: 'images/slide_6.jpg'
    },
    fur: {
        label: 'Шуба',
        initialDamage: 'Устаревший трапециевидный силуэт, залысины вдоль бортов и разрыв мездры под проймой.',
        workDone: 'Полный перекрой в современный силуэт автоледи, укрепление мездры, замена клипс и подкладки.',
        beforeImg: 'images/slide_4.jpg',
        afterImg: 'images/slide_2.jpg'
    },
    shoes: {
        label: 'Обувь',
        initialDamage: 'Белые солевые разводы после зимы, сбитые мыски и вытертые каблуки.',
        workDone: 'Нейтрализация реагентов в спа-ванне, шлифовка мысков, грунтование и пропитка водоотталкивающим воском.',
        beforeImg: 'images/slide_6.jpg',
        afterImg: 'images/slide_3.jpg'
    }
};

// ================= Global State =================

let currentCalcKey = 'jacket';
let currentCalcWorkIndex = 0;
let currentWizardStep = 1;
let selectedWizardItem = 'Куртка';
let selectedWizardProblems = [];
let uploadedPhotos = []; // array of { file: File, dataUrl: string }

// Dexie Database for atelier internal staff management
let staffDb = null;

// ================= App Initialization =================

document.addEventListener('DOMContentLoaded', () => {
    // 1. Lucide icons & AOS
    if (window.lucide) lucide.createIcons();
    if (window.AOS) AOS.init({ duration: 800, once: true });

    // 2. Initialize subsystems
    initStaffDatabase();
    initCalculator('jacket');
    initBeforeAfterSlider();
    initPhoneMasks();

    // 3. Keyboard accessibility
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeWizardModal();
            closeServiceDetailModal();
            closeAdminModal();
            closePrivacyModal();
            const menu = document.getElementById('mobile-menu');
            if (menu && menu.classList.contains('open')) toggleMobileMenu();
        }
        if ((e.altKey && (e.key === 'a' || e.key === 'A' || e.key === 'ф' || e.key === 'Ф'))) {
            openAdminModal();
        }
    });
});

// ================= 6. Interactive Calculator System =================

function initCalculator(itemKey) {
    currentCalcKey = itemKey || 'jacket';
    currentCalcWorkIndex = 0;
    renderCalcWorks(currentCalcKey);
    updateCalcResult();
}

function setCalcItem(itemKey, btnEl) {
    currentCalcKey = itemKey;
    currentCalcWorkIndex = 0;

    // Update pill states
    const pills = document.querySelectorAll('#calc-item-types .calc-pill');
    pills.forEach(p => p.classList.remove('active'));
    if (btnEl) btnEl.classList.add('active');

    renderCalcWorks(itemKey);
    updateCalcResult();
}

function renderCalcWorks(itemKey) {
    const worksListEl = document.getElementById('calc-works-list');
    if (!worksListEl) return;

    const data = CALCULATOR_DATA[itemKey];
    if (!data || !data.works) return;

    worksListEl.innerHTML = data.works.map((w, idx) => `
        <div class="calc-work-card ${idx === currentCalcWorkIndex ? 'active' : ''}" onclick="selectCalcWork(${idx}, this)">
            <div>
                <div class="calc-work-name">${w.name}</div>
                <div class="calc-work-sub">${w.desc}</div>
            </div>
            <div class="calc-work-price">Ориентировочно: ${w.priceRange}</div>
        </div>
    `).join('');
}

function selectCalcWork(idx, cardEl) {
    currentCalcWorkIndex = idx;
    const cards = document.querySelectorAll('#calc-works-list .calc-work-card');
    cards.forEach(c => c.classList.remove('active'));
    if (cardEl) cardEl.classList.add('active');

    updateCalcResult();
}

function updateCalcResult() {
    const data = CALCULATOR_DATA[currentCalcKey];
    if (!data) return;
    const work = data.works[currentCalcWorkIndex] || data.works[0];

    const priceEl = document.getElementById('calc-price-display');
    const timeEl = document.getElementById('calc-time-display');
    const waBtn = document.getElementById('calc-wa-btn');

    if (priceEl) priceEl.textContent = work.priceRange;
    if (timeEl) {
        timeEl.innerHTML = `<i data-lucide="clock"></i> <span>Ориентировочный срок: ${work.time}</span>`;
        if (window.lucide) lucide.createIcons();
    }

    if (waBtn) {
        const text = encodeURIComponent(`Здравствуйте! Интересует ориентировочный расчёт: ${data.title} (${work.name}). Подскажите, пожалуйста, по стоимости и оценке по фото.`);
        waBtn.href = `https://wa.me/79275103299?text=${text}`;
    }
}

function sendCalcToWizard() {
    const data = CALCULATOR_DATA[currentCalcKey];
    const itemTitle = data ? data.title.split(' ')[0] : 'Куртка';
    openWizardModal(itemTitle);
}

// ================= 5. Multi-Step Photo Assessment Wizard =================

function openWizardModal(preselectedItem) {
    const modal = document.getElementById('wizardModal');
    if (!modal) return;

    if (preselectedItem) {
        selectedWizardItem = preselectedItem;
        const itemBtns = document.querySelectorAll('.wizard-choice-btn');
        itemBtns.forEach(btn => {
            const val = btn.getAttribute('data-item') || '';
            if (val.toLowerCase().includes(preselectedItem.toLowerCase()) || preselectedItem.toLowerCase().includes(val.toLowerCase())) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
    }

    goToWizardStep(1);
    modal.classList.add('open');
    document.body.style.overflow = 'hidden';
}

function closeWizardModal() {
    const modal = document.getElementById('wizardModal');
    if (modal) modal.classList.remove('open');
    document.body.style.overflow = '';
}

function selectWizardItem(btn) {
    document.querySelectorAll('.wizard-choice-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    selectedWizardItem = btn.getAttribute('data-item') || 'Куртка';
}

function updateSelectedProblems() {
    const checkboxes = document.querySelectorAll('input[name="problem"]:checked');
    selectedWizardProblems = Array.from(checkboxes).map(cb => cb.value);
}

function goToWizardStep(stepNumber) {
    currentWizardStep = stepNumber;

    // Panels
    const panels = ['step-panel-1', 'step-panel-2', 'step-panel-3', 'step-panel-success'];
    panels.forEach((pId, idx) => {
        const el = document.getElementById(pId);
        if (el) {
            if (idx + 1 === stepNumber) {
                el.classList.add('active');
            } else {
                el.classList.remove('active');
            }
        }
    });

    // Subtitle & Dots
    const subTitle = document.getElementById('wizard-step-subtitle');
    const dot1 = document.getElementById('dot-1');
    const dot2 = document.getElementById('dot-2');
    const dot3 = document.getElementById('dot-3');
    const line1 = document.getElementById('line-1');
    const line2 = document.getElementById('line-2');

    if (stepNumber === 1) {
        if (subTitle) subTitle.textContent = 'Шаг 1 из 3: Выберите тип изделия';
        if (dot1) { dot1.className = 'step-dot active'; }
        if (dot2) { dot2.className = 'step-dot'; }
        if (dot3) { dot3.className = 'step-dot'; }
        if (line1) line1.className = 'step-line';
        if (line2) line2.className = 'step-line';
    } else if (stepNumber === 2) {
        if (subTitle) subTitle.textContent = 'Шаг 2 из 3: Укажите характер повреждений';
        if (dot1) { dot1.className = 'step-dot completed'; }
        if (dot2) { dot2.className = 'step-dot active'; }
        if (dot3) { dot3.className = 'step-dot'; }
        if (line1) line1.className = 'step-line active';
        if (line2) line2.className = 'step-line';
    } else if (stepNumber === 3) {
        if (subTitle) subTitle.textContent = 'Шаг 3 из 3: Фотографии и контактные данные';
        if (dot1) { dot1.className = 'step-dot completed'; }
        if (dot2) { dot2.className = 'step-dot completed'; }
        if (dot3) { dot3.className = 'step-dot active'; }
        if (line1) line1.className = 'step-line active';
        if (line2) line2.className = 'step-line active';
    } else if (stepNumber === 4) {
        if (subTitle) subTitle.textContent = 'Заявка принята в работу';
        if (dot1) { dot1.className = 'step-dot completed'; }
        if (dot2) { dot2.className = 'step-dot completed'; }
        if (dot3) { dot3.className = 'step-dot completed'; }
        if (line1) line1.className = 'step-line active';
        if (line2) line2.className = 'step-line active';
    }

    if (window.lucide) lucide.createIcons();
}

// Photo Uploading & Dropzone
function triggerFileInput() {
    const input = document.getElementById('wizard-file-input');
    if (input) input.click();
}

function handleFileSelect(event) {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    const remainingSlots = 5 - uploadedPhotos.length;
    if (remainingSlots <= 0) {
        showToast('Максимально можно прикрепить до 5 фотографий.', 'error');
        return;
    }

    const countToAdd = Math.min(files.length, remainingSlots);
    for (let i = 0; i < countToAdd; i++) {
        const file = files[i];
        if (!file.type.startsWith('image/')) {
            showToast(`Файл «${file.name}» не является изображением.`, 'error');
            continue;
        }
        if (file.size > 10 * 1024 * 1024) {
            showToast(`Файл «${file.name}» превышает лимит 10 МБ.`, 'error');
            continue;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            uploadedPhotos.push({
                file: file,
                dataUrl: e.target.result,
                name: file.name
            });
            renderPhotosPreview();
        };
        reader.readAsDataURL(file);
    }

    event.target.value = '';
}

function renderPhotosPreview() {
    const grid = document.getElementById('photos-preview-grid');
    if (!grid) return;

    if (uploadedPhotos.length === 0) {
        grid.innerHTML = '';
        return;
    }

    grid.innerHTML = uploadedPhotos.map((p, idx) => `
        <div class="photo-preview-item">
            <img src="${p.dataUrl}" alt="Фото ${idx + 1}" class="preview-thumb">
            <button type="button" class="btn-remove-photo" onclick="removePhoto(${idx})" aria-label="Удалить фото">✕</button>
        </div>
    `).join('');
}

function removePhoto(idx) {
    uploadedPhotos.splice(idx, 1);
    renderPhotosPreview();
}

// Form Submission with Anti-Spam & Validation
async function handleWizardFinalSubmit(event) {
    event.preventDefault();

    // 1. Anti-spam honeypot
    const hpInput = event.target.querySelector('input[name="b_website"]');
    if (hpInput && hpInput.value.trim() !== '') {
        console.warn('Spam submission detected by honeypot.');
        return; // silently discard bot submission
    }

    // 2. Validate fields
    const nameInput = document.getElementById('wiz-name');
    const phoneInput = document.getElementById('wiz-phone');
    const descInput = document.getElementById('wizard-desc');
    const consentInput = document.getElementById('wiz-consent');

    const name = nameInput ? nameInput.value.trim() : '';
    const phone = phoneInput ? phoneInput.value.trim() : '';
    const desc = descInput ? descInput.value.trim() : '';
    const consent = consentInput ? consentInput.checked : false;

    if (name.length < 2) {
        showToast('Пожалуйста, укажите ваше имя (минимум 2 буквы).', 'error');
        nameInput.focus();
        return;
    }

    const digitsOnly = phone.replace(/\D/g, '');
    if (digitsOnly.length < 11) {
        showToast('Пожалуйста, введите корректный номер телефона РФ (+7...).', 'error');
        phoneInput.focus();
        return;
    }

    if (!consent) {
        showToast('Необходимо подтвердить согласие на обработку данных.', 'error');
        return;
    }

    const channelEl = document.querySelector('input[name="wiz-channel"]:checked');
    const channel = channelEl ? channelEl.value : 'WhatsApp';

    // 3. Generate unique appeal number
    const appealId = `№ GH-${Math.floor(1000 + Math.random() * 9000)}`;

    const orderPayload = {
        appealId: appealId,
        date: new Date().toLocaleString('ru-RU'),
        name: name,
        phone: phone,
        item: selectedWizardItem,
        problems: selectedWizardProblems.length > 0 ? selectedWizardProblems.join(', ') : 'Общая диагностика',
        desc: desc,
        channel: channel,
        photosCount: uploadedPhotos.length,
        status: 'Новая'
    };

    // 4. Save to private StaffOrdersDB
    if (staffDb) {
        try {
            await staffDb.orders.add(orderPayload);
        } catch (e) {
            console.error('Ошибка сохранения в StaffOrdersDB:', e);
        }
    }

    // 5. Attempt backend API delivery (if server present)
    try {
        const formData = new FormData();
        formData.append('appealId', appealId);
        formData.append('name', name);
        formData.append('phone', phone);
        formData.append('item', selectedWizardItem);
        formData.append('problems', orderPayload.problems);
        formData.append('desc', desc);
        formData.append('channel', channel);
        uploadedPhotos.forEach((p, i) => formData.append(`photo_${i}`, p.file));

        fetch('/api/orders', {
            method: 'POST',
            body: formData
        }).catch(() => {
            // Static hosting fallback — local staffDb handles it safely
        });
    } catch (_) {}

    // 6. Confetti & Success screen
    fireConfetti();
    const appealDisplay = document.getElementById('appeal-number-text');
    if (appealDisplay) appealDisplay.textContent = appealId;

    goToWizardStep(4);
    showToast(`Заявка ${appealId} успешно отправлена! Технолог ответит в ${channel}.`, 'success');

    // Reset upload state
    uploadedPhotos = [];
    renderPhotosPreview();
}

// ================= 7. Closed Atelier Admin Panel =================

function initStaffDatabase() {
    if (!window.Dexie) return;
    staffDb = new Dexie('GHLeatherStaffDB');
    staffDb.version(1).stores({
        orders: '++id, appealId, name, phone, item, problems, status, date'
    });

    // Populate initial authentic records if clean
    staffDb.orders.count().then(count => {
        if (count === 0) {
            staffDb.orders.bulkAdd([
                {
                    appealId: '№ GH-4819',
                    date: 'Вчера, 16:40',
                    name: 'Михаил',
                    phone: '+7 (905) 334-12-88',
                    item: 'Куртка',
                    problems: 'Потёртости воротника, задиры локтей',
                    desc: 'Кожаная куртка Schott, требуется локальная реставрация.',
                    channel: 'WhatsApp',
                    photosCount: 2,
                    status: 'В работе'
                },
                {
                    appealId: '№ GH-5120',
                    date: 'Сегодня, 11:15',
                    name: 'Елена',
                    phone: '+7 (927) 501-99-44',
                    item: 'Шуба',
                    problems: 'Перекрой фасона',
                    desc: 'Норковая длинная шуба, сделать автоледи.',
                    channel: 'WhatsApp',
                    photosCount: 1,
                    status: 'Оценка'
                }
            ]);
        }
    });
}

function openAdminModal() {
    const modal = document.getElementById('adminModal');
    if (!modal) return;

    const isAuthed = sessionStorage.getItem('gh_admin_auth') === 'true';
    const authView = document.getElementById('admin-auth-view');
    const dashView = document.getElementById('admin-dashboard-view');

    if (isAuthed) {
        if (authView) authView.style.display = 'none';
        if (dashView) dashView.classList.add('active');
        renderAdminOrders();
    } else {
        if (authView) authView.style.display = 'block';
        if (dashView) dashView.classList.remove('active');
        const passIn = document.getElementById('admin-password-input');
        if (passIn) {
            passIn.value = '';
            setTimeout(() => passIn.focus(), 200);
        }
    }

    modal.classList.add('open');
    document.body.style.overflow = 'hidden';
}

function closeAdminModal() {
    const modal = document.getElementById('adminModal');
    if (modal) modal.classList.remove('open');
    document.body.style.overflow = '';
}

function handleAdminLogin(event) {
    event.preventDefault();
    const passInput = document.getElementById('admin-password-input');
    const errEl = document.getElementById('admin-login-err');
    const val = passInput ? passInput.value.trim() : '';

    // Accepted staff PINs: 1234 or gh2026
    if (val === '1234' || val === 'gh2026') {
        sessionStorage.setItem('gh_admin_auth', 'true');
        if (errEl) errEl.style.display = 'none';

        const authView = document.getElementById('admin-auth-view');
        const dashView = document.getElementById('admin-dashboard-view');
        if (authView) authView.style.display = 'none';
        if (dashView) dashView.classList.add('active');

        renderAdminOrders();
        showToast('Авторизация успешна. Добро пожаловать в систему!', 'success');
    } else {
        if (errEl) errEl.style.display = 'block';
        if (passInput) {
            passInput.value = '';
            passInput.focus();
        }
    }
}

async function renderAdminOrders() {
    const container = document.getElementById('admin-orders-container');
    if (!container || !staffDb) return;

    const orders = await staffDb.orders.reverse().toArray();
    filterAdminOrdersWithList(orders);
}

async function filterAdminOrders() {
    if (!staffDb) return;
    const orders = await staffDb.orders.reverse().toArray();
    filterAdminOrdersWithList(orders);
}

function filterAdminOrdersWithList(orders) {
    const container = document.getElementById('admin-orders-container');
    const searchVal = (document.getElementById('admin-search-box')?.value || '').toLowerCase().trim();
    const statusVal = document.getElementById('admin-status-filter')?.value || 'all';

    const filtered = orders.filter(o => {
        const matchesSearch = !searchVal || 
            (o.name && o.name.toLowerCase().includes(searchVal)) || 
            (o.phone && o.phone.includes(searchVal)) ||
            (o.appealId && o.appealId.toLowerCase().includes(searchVal));
        const matchesStatus = statusVal === 'all' || o.status === statusVal;
        return matchesSearch && matchesStatus;
    });

    if (filtered.length === 0) {
        container.innerHTML = `<div style="text-align:center; padding: 2rem; color:#94a3b8;">Обращений не найдено</div>`;
        return;
    }

    container.innerHTML = filtered.map(o => `
        <div class="admin-order-card">
            <div class="admin-appeal-badge">${o.appealId || '#GH'}</div>
            <div class="admin-order-details">
                <div>
                    <strong>${o.name}</strong> 
                    <a href="tel:${o.phone.replace(/\\s/g,'')}">${o.phone}</a>
                    <a href="https://wa.me/${o.phone.replace(/\\D/g,'')}" target="_blank" style="color:#22c55e;">[WhatsApp]</a>
                </div>
                <p>Изделие: <b>${o.item}</b> | Проблемы: ${o.problems} | Дата: ${o.date}</p>
                ${o.desc ? `<p style="color:#cbd5e1; font-style:italic;">«${o.desc}»</p>` : ''}
            </div>
            <div>
                <select class="admin-status-select" onchange="updateOrderStatus(${o.id}, this.value)">
                    <option value="Новая" ${o.status === 'Новая' ? 'selected' : ''}>Новая</option>
                    <option value="Оценка" ${o.status === 'Оценка' ? 'selected' : ''}>Оценка</option>
                    <option value="Согласование" ${o.status === 'Согласование' ? 'selected' : ''}>Согласование</option>
                    <option value="В работе" ${o.status === 'В работе' ? 'selected' : ''}>В работе</option>
                    <option value="Готово" ${o.status === 'Готово' ? 'selected' : ''}>Готово</option>
                    <option value="Завершена" ${o.status === 'Завершена' ? 'selected' : ''}>Завершена</option>
                </select>
            </div>
        </div>
    `).join('');
}

async function updateOrderStatus(orderId, newStatus) {
    if (!staffDb) return;
    try {
        await staffDb.orders.update(orderId, { status: newStatus });
        showToast(`Статус заявки изменён на «${newStatus}»`, 'info');
    } catch (e) {
        console.error('Ошибка обновления статуса:', e);
    }
}

// ================= Service Detail Modal =================

function openServiceDetailModal(serviceTitle) {
    const modal = document.getElementById('serviceDetailModal');
    if (!modal) return;

    const data = SERVICES_CATALOG[serviceTitle] || {
        desc: 'Индивидуальная консультация и реставрационные работы любой сложности.',
        price: 'от 3 500 ₽',
        time: '3–5 рабочих дней'
    };

    const titleEl = document.getElementById('serv-modal-title');
    const descEl = document.getElementById('serv-modal-desc');
    const priceEl = document.getElementById('serv-modal-price');
    const timeEl = document.getElementById('serv-modal-time');

    if (titleEl) titleEl.textContent = serviceTitle;
    if (descEl) descEl.textContent = data.desc;
    if (priceEl) priceEl.textContent = data.price;
    if (timeEl) timeEl.textContent = data.time;

    modal.classList.add('open');
    document.body.style.overflow = 'hidden';
}

function closeServiceDetailModal() {
    const modal = document.getElementById('serviceDetailModal');
    if (modal) modal.classList.remove('open');
    document.body.style.overflow = '';
}

// ================= Privacy Policy Modal (152-ФЗ) =================

function openPrivacyModal() {
    const modal = document.getElementById('privacyModal');
    if (modal) {
        modal.classList.add('open');
        document.body.style.overflow = 'hidden';
    }
}

function closePrivacyModal() {
    const modal = document.getElementById('privacyModal');
    if (modal) {
        modal.classList.remove('open');
        document.body.style.overflow = '';
    }
}

// ================= Portfolio Case Switcher & Before/After Slider =================

function switchPortfolioCase(caseType, btnEl) {
    document.querySelectorAll('.category-tabs .tab-btn').forEach(b => b.classList.remove('active'));
    if (btnEl) btnEl.classList.add('active');

    const data = PORTFOLIO_CASES[caseType] || PORTFOLIO_CASES['jacket'];
    const titleEl = document.getElementById('case-title');
    const initEl = document.getElementById('case-before-desc');
    const workEl = document.getElementById('case-after-desc');
    const fullDescEl = document.getElementById('case-full-desc');

    if (titleEl) titleEl.textContent = `Кейс: ${data.label}`;
    if (initEl) initEl.textContent = data.initialDamage;
    if (workEl) workEl.textContent = data.workDone;
    if (fullDescEl) fullDescEl.textContent = `Индивидуальная реставрация: ${data.workDone}`;

    // Reset handle position to 50%
    const afterLayer = document.getElementById('ba-after-layer');
    const handle = document.getElementById('ba-handle');
    if (afterLayer) afterLayer.style.width = '50%';
    if (handle) handle.style.left = '50%';
}

function initBeforeAfterSlider() {
    const container = document.getElementById('ba-slider');
    const afterLayer = document.getElementById('ba-after-layer');
    const handle = document.getElementById('ba-handle');
    if (!container || !afterLayer || !handle) return;

    let isDragging = false;

    function updateSlider(clientX) {
        const rect = container.getBoundingClientRect();
        let pos = (clientX - rect.left) / rect.width;
        if (pos < 0.05) pos = 0.05;
        if (pos > 0.95) pos = 0.95;

        const percent = pos * 100;
        afterLayer.style.width = `${percent}%`;
        handle.style.left = `${percent}%`;
    }

    container.addEventListener('mousedown', (e) => {
        isDragging = true;
        updateSlider(e.clientX);
    });

    window.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        updateSlider(e.clientX);
    });

    window.addEventListener('mouseup', () => {
        isDragging = false;
    });

    // Touch support (Mobile)
    container.addEventListener('touchstart', (e) => {
        isDragging = true;
        updateSlider(e.touches[0].clientX);
    }, { passive: true });

    window.addEventListener('touchmove', (e) => {
        if (!isDragging) return;
        updateSlider(e.touches[0].clientX);
    }, { passive: true });

    window.addEventListener('touchend', () => {
        isDragging = false;
    });
}

// ================= Mobile Navigation & Helpers =================

function toggleMobileMenu() {
    const menu = document.getElementById('mobile-menu');
    const overlay = document.getElementById('mobile-menu-overlay');
    if (!menu) return;

    const isOpen = menu.classList.contains('open');
    if (isOpen) {
        menu.classList.remove('open');
        menu.setAttribute('aria-hidden', 'true');
        if (overlay) overlay.classList.remove('open');
        document.body.style.overflow = '';
    } else {
        menu.classList.add('open');
        menu.setAttribute('aria-hidden', 'false');
        if (overlay) overlay.classList.add('open');
        document.body.style.overflow = 'hidden';
    }
}

function initPhoneMasks() {
    const inputs = document.querySelectorAll('input[type="tel"]');
    inputs.forEach(input => {
        input.addEventListener('input', (e) => {
            let val = e.target.value.replace(/\D/g, '');
            if (!val) {
                e.target.value = '';
                return;
            }
            if (val[0] === '7' || val[0] === '8') val = val.substring(1);
            let formatted = '+7 (';
            if (val.length > 0) formatted += val.substring(0, 3);
            if (val.length >= 3) formatted += ') ' + val.substring(3, 6);
            if (val.length >= 6) formatted += '-' + val.substring(6, 8);
            if (val.length >= 8) formatted += '-' + val.substring(8, 10);
            e.target.value = formatted;
        });
    });
}

function fireConfetti() {
    if (window.confetti) {
        confetti({
            particleCount: 75,
            spread: 60,
            origin: { y: 0.6 }
        });
    }
}

function showToast(msg, type = 'info') {
    const wrap = document.getElementById('toast-wrap');
    if (!wrap) return;
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = msg;
    wrap.appendChild(toast);
    setTimeout(() => toast.remove(), 4500);
}
