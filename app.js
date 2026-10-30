/** GH-Leather: local calculator + comparison + navigation. No data collection. */

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
        label: "Кожаная куртка",
        initialDamage: "Потёртости плеч, рукавов и манжет, потускневшая поверхность кожи.",
        workDone: "Та же куртка, но с восстановленным цветом и аккуратной поверхностью.",
        beforeImg: "images/studio_jacket_before.jpg",
        afterImg: "images/studio_jacket_after.jpg"
    },
    bag: {
        label: "Кожаная сумка",
        initialDamage: "Потёртые уголки, ручки и швы, выцветший цвет кожи.",
        workDone: "Та же сумка, но с обновлённым цветом и ровной поверхностью.",
        beforeImg: "images/studio_bag_before.jpg",
        afterImg: "images/studio_bag_after.jpg"
    }
};


let currentCalcKey = "jacket";
let currentCalcWorkIndex = 0;

document.addEventListener("DOMContentLoaded", () => {
    window.lucide?.createIcons();
    // The old insecure request journal and admin session must not be retained.
    try { window.indexedDB?.deleteDatabase("GHLeatherStaffDB"); } catch (_) {}
    try { window.sessionStorage?.removeItem("gh_admin_auth"); } catch (_) {}
    initCalculator("jacket");
    initBeforeAfterSlider();
    document.addEventListener("keydown", event => {
        if (event.key === "Escape") {
            const menu = document.getElementById("mobile-menu");
            if (menu?.classList.contains("open")) toggleMobileMenu();
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

// Quick access selects the SAME calculator data used by the existing site.
function goToService(itemKey) {
    const allowed = ['jacket', 'bag', 'shoes', 'fur', 'auto', 'tailoring'];
    if (!allowed.includes(itemKey)) return;
    const pill = document.querySelector('#calc-item-types .calc-pill[data-item="' + itemKey + '"]');
    setCalcItem(itemKey, pill);
    const pricing = document.getElementById('prices');
    if (pricing) pricing.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
}

// ================= Portfolio Case Switcher & Accessible Before/After Slider =================

// Stores the last interaction so automated animation never fights user input.
let comparisonAnimFrame = null;
let comparisonHasInteracted = false;
let comparisonSwitchId = 0;

function setComparisonPosition(position) {
    const container = document.getElementById('ba-slider');
    const handle = document.getElementById('ba-handle');
    if (!container || !handle) return;
    const p = Math.max(3, Math.min(97, Number(position) || 50));
    const percent = p.toFixed(2) + '%';
    container.style.setProperty('--clip-pos', percent);
    handle.style.left = percent;
    handle.setAttribute('aria-valuenow', Math.round(p));
    handle.setAttribute('aria-valuetext', Math.round(p) + ' процентов');
}

function stopComparisonIntro() {
    comparisonHasInteracted = true;
    if (comparisonAnimFrame !== null) {
        cancelAnimationFrame(comparisonAnimFrame);
        comparisonAnimFrame = null;
    }
    const hint = document.getElementById('ba-swipe-hint');
    if (hint) hint.classList.add('hidden');
}

function animateComparison(force) {
    const container = document.getElementById('ba-slider');
    if (!container) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    if (comparisonHasInteracted && !force) return;
    if (comparisonAnimFrame !== null) cancelAnimationFrame(comparisonAnimFrame);
    if (force) comparisonHasInteracted = false;
    // A slow left-right reveal makes the difference clear without endless motion.
    const points = [[0,50],[500,24],[1450,78],[2250,50]];
    let start = null;
    const ease = t => t < .5 ? 4*t*t*t : 1-Math.pow(-2*t+2,3)/2;
    function step(time) {
        if (comparisonHasInteracted) { comparisonAnimFrame = null; return; }
        if (start === null) start = time;
        const elapsed = Math.min(2250, time - start);
        let position = 50;
        for (let i = 1; i < points.length; i++) {
            if (elapsed <= points[i][0]) {
                const [t0, x0] = points[i-1], [t1,x1] = points[i];
                position = x0 + (x1-x0)*ease((elapsed-t0)/(t1-t0));
                break;
            }
        }
        setComparisonPosition(position);
        if (elapsed < 2250) comparisonAnimFrame = requestAnimationFrame(step);
        else { comparisonAnimFrame = null; setComparisonPosition(50); }
    }
    comparisonAnimFrame = requestAnimationFrame(step);
}

function switchPortfolioCase(caseType, btnEl) {
    const data = PORTFOLIO_CASES[caseType] || PORTFOLIO_CASES.jacket;
    document.querySelectorAll('#portfolio-tabs .tab-btn').forEach(b => {
        const selected = b === btnEl;
        b.classList.toggle('active', selected);
        b.setAttribute('aria-pressed', String(selected));
    });
    const container = document.getElementById('ba-slider');
    const titleEl = document.getElementById('case-title');
    const initEl = document.getElementById('case-before-desc');
    const workEl = document.getElementById('case-after-desc');
    const fullDescEl = document.getElementById('case-full-desc');
    const imgBefore = document.getElementById('ba-img-before');
    const imgAfter = document.getElementById('ba-img-after');

    // The images are generated from the exact same source. Do not switch
    // to independent stock photography, which breaks alignment.
    const switching = ++comparisonSwitchId;
    const newBefore = new Image();
    const newAfter = new Image();
    const load = (img, src) => new Promise(resolve => {
        img.onload = () => resolve(true);
        img.onerror = () => resolve(false);
        img.src = src;
    });
    Promise.all([load(newBefore, data.beforeImg), load(newAfter, data.afterImg)]).then(([beforeReady, afterReady]) => {
        if (switching !== comparisonSwitchId || !afterReady) return;
        if (imgAfter) imgAfter.src = data.afterImg;
        if (imgBefore) imgBefore.src = beforeReady ? data.beforeImg : data.afterImg;
        if (container) container.style.setProperty('--ba-preview-image', "url('" + data.afterImg + "')");
        if (titleEl) titleEl.textContent = "Пример: " + data.label;
        if (initEl) initEl.textContent = data.initialDamage;
        if (workEl) workEl.textContent = data.workDone;
        if (fullDescEl) fullDescEl.textContent = 'Демонстрационная визуализация, не фотография выполненного заказа. ' + data.workDone;
        setComparisonPosition(50);
        animateComparison(true);
    });
}

function initBeforeAfterSlider() {
    const container = document.getElementById('ba-slider');
    const handle = document.getElementById('ba-handle');
    if (!container || !handle) return;
    let activePointerId = null;

    function updateFromPointer(event) {
        const rect = container.getBoundingClientRect();
        if (!rect.width) return;
        setComparisonPosition((event.clientX-rect.left)/rect.width*100);
    }

    container.addEventListener('pointerdown', event => {
        if (event.pointerType === 'mouse' && event.button !== 0) return;
        stopComparisonIntro();
        activePointerId = event.pointerId;
        if (container.setPointerCapture) container.setPointerCapture(event.pointerId);
        updateFromPointer(event);
    });
    container.addEventListener('pointermove', event => {
        if (activePointerId !== event.pointerId) return;
        updateFromPointer(event);
    });
    const release = event => {
        if (activePointerId === event.pointerId) activePointerId = null;
    };
    container.addEventListener('pointerup', release);
    container.addEventListener('pointercancel', release);
    container.addEventListener('lostpointercapture', () => { activePointerId = null; });
    handle.addEventListener('keydown', event => {
        const p = Number(handle.getAttribute('aria-valuenow') || 50);
        const next = event.key === 'ArrowLeft' ? p-5
            : event.key === 'ArrowRight' ? p+5
            : event.key === 'Home' ? 3
            : event.key === 'End' ? 97 : null;
        if (next === null) return;
        event.preventDefault();
        stopComparisonIntro();
        setComparisonPosition(next);
    });
    document.getElementById('ba-animate-button')?.addEventListener('click', () => {
        const hint = document.getElementById('ba-swipe-hint');
        if (hint) hint.classList.remove('hidden');
        animateComparison(true);
    });

    // Keep a graceful fallback if a generated image is temporarily missing.
    const before = document.getElementById('ba-img-before');
    const after = document.getElementById('ba-img-after');
    if (before && after) before.addEventListener('error', () => {
        if (before.src !== after.src) before.src = after.src;
    });

    setComparisonPosition(50);
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver(entries => {
            if (entries.some(entry => entry.isIntersecting)) {
                observer.disconnect();
                animateComparison(false);
            }
        }, { threshold: 0.35 });
        observer.observe(container);
    }
}

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