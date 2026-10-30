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
        initialDamage: "Следы износа и выцветание кожи на фотографии до реставрации.",
        workDone: "Фотография восстановленной куртки той же мастерской.",
        beforeImg: "images/studio_jacket_before.jpg",
        afterImg: "images/studio_jacket_after.jpg"
    },
    bag: {
        label: "Кожаная сумка",
        initialDamage: "Состояние сумки до восстановления на фотографии мастерской.",
        workDone: "Сумка после профессиональной обработки той же мастерской.",
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
        <button type="button" class="calc-work-card ${idx === currentCalcWorkIndex ? 'active' : ''}" aria-pressed="${idx === currentCalcWorkIndex}" onclick="selectCalcWork(${idx}, this)">
            <div>
                <div class="calc-work-name">${w.name}</div>
                <div class="calc-work-sub">${w.desc}</div>
            </div>
            <div class="calc-work-price">Ориентировочно: ${w.priceRange}</div>
        </button>
    `).join('');
}

function selectCalcWork(idx, cardEl) {
    currentCalcWorkIndex = idx;
    const cards = document.querySelectorAll('#calc-works-list .calc-work-card');
    cards.forEach(c => { c.classList.remove('active'); c.setAttribute('aria-pressed','false'); });
    if (cardEl) { cardEl.classList.add('active'); cardEl.setAttribute('aria-pressed','true'); }

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

// ================= Smooth accessible Before/After comparison =================
// Drag updates are batched into a single repaint per frame. The two photos
// stay fixed and only the reveal mask/divider move, avoiding image re-layout.
let comparisonAnimFrame = null;
let comparisonPointerFrame = null;
let comparisonPosition = 50;
let comparisonQueuedPosition = 50;
let comparisonHasInteracted = false;
let comparisonSwitchId = 0;

function clampComparisonPosition(value) {
    const number = Number(value);
    return Number.isFinite(number) ? Math.min(95, Math.max(5, number)) : 50;
}

function applyComparisonPosition(value) {
    const slider = document.getElementById('ba-slider');
    const handle = document.getElementById('ba-handle');
    if (!slider || !handle) return;
    const position = clampComparisonPosition(value);
    comparisonPosition = position;
    comparisonQueuedPosition = position;
    slider.style.setProperty('--clip-pos', position.toFixed(2) + '%');
    const rounded = String(Math.round(position));
    if (handle.getAttribute('aria-valuenow') !== rounded) {
        handle.setAttribute('aria-valuenow', rounded);
        handle.setAttribute('aria-valuetext', rounded + ' процентов');
    }
}

function queueComparisonPosition(value) {
    comparisonQueuedPosition = clampComparisonPosition(value);
    if (comparisonPointerFrame !== null) return;
    comparisonPointerFrame = requestAnimationFrame(() => {
        comparisonPointerFrame = null;
        applyComparisonPosition(comparisonQueuedPosition);
    });
}

function flushComparisonPosition() {
    if (comparisonPointerFrame !== null) {
        cancelAnimationFrame(comparisonPointerFrame);
        comparisonPointerFrame = null;
        applyComparisonPosition(comparisonQueuedPosition);
    }
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

function animateComparison() {
    stopComparisonIntro();
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        applyComparisonPosition(50);
        return;
    }
    flushComparisonPosition();
    const points = [[0, 50], [550, 23], [1600, 77], [2400, 50]];
    const ease = t => t * t * (3 - 2 * t);
    let origin = null;
    function frame(timestamp) {
        if (origin === null) origin = timestamp;
        const time = Math.min(2400, timestamp - origin);
        let position = 50;
        for (let index = 1; index < points.length; index++) {
            if (time <= points[index][0]) {
                const [previousTime, previousPosition] = points[index - 1];
                const [nextTime, nextPosition] = points[index];
                const progress = (time - previousTime) / (nextTime - previousTime);
                position = previousPosition + (nextPosition - previousPosition) * ease(progress);
                break;
            }
        }
        applyComparisonPosition(position);
        if (time < 2400) {
            comparisonAnimFrame = requestAnimationFrame(frame);
        } else {
            comparisonAnimFrame = null;
            applyComparisonPosition(50);
        }
    }
    comparisonAnimFrame = requestAnimationFrame(frame);
}

// Switch only after both photos are decoded. No automatic animation competes
// with touches; the "Сравнить снова" control starts animation on demand.
function switchPortfolioCase(caseType, button) {
    const data = PORTFOLIO_CASES[caseType];
    if (!data) return;
    const version = ++comparisonSwitchId;
    const before = document.getElementById('ba-img-before');
    const after = document.getElementById('ba-img-after');
    const slider = document.getElementById('ba-slider');
    if (!before || !after || !slider) return;
    stopComparisonIntro();
    const load = source => {
        const photo = new Image();
        photo.decoding = 'async';
        photo.src = source;
        if (typeof photo.decode === 'function') {
            return photo.decode().then(() => true).catch(() => false);
        }
        return new Promise(resolve => {
            if (photo.complete) { resolve(photo.naturalWidth > 0); return; }
            photo.onload = () => resolve(true);
            photo.onerror = () => resolve(false);
        });
    };
    Promise.all([load(data.beforeImg), load(data.afterImg)]).then(([beforeOK, afterOK]) => {
        if (version !== comparisonSwitchId || !beforeOK || !afterOK) return;
        before.src = data.beforeImg;
        after.src = data.afterImg;
        before.alt = 'Изделие до реставрации: ' + data.label.toLowerCase();
        after.alt = 'Изделие после реставрации: ' + data.label.toLowerCase();
        slider.style.setProperty('--ba-preview-image', 'url("' + data.afterImg + '")');
        document.querySelectorAll('#portfolio-tabs .tab-btn').forEach(tab => {
            const selected = tab === button || tab.dataset.case === caseType;
            tab.classList.toggle('active', selected);
            tab.setAttribute('aria-pressed', String(selected));
        });
        applyComparisonPosition(50);
    });
}

function initBeforeAfterSlider() {
    const slider = document.getElementById('ba-slider');
    const handle = document.getElementById('ba-handle');
    if (!slider || !handle) return;
    let activePointerId = null;
    let dragBounds = null;

    function positionFrom(event) {
        if (!dragBounds || dragBounds.width <= 0) return;
        // Coalesced events provide the freshest touch/mouse coordinate.
        const coalesced = event.getCoalescedEvents?.();
        const last = coalesced && coalesced.length ? coalesced[coalesced.length - 1] : event;
        queueComparisonPosition((last.clientX - dragBounds.left) / dragBounds.width * 100);
    }
    slider.addEventListener('pointerdown', event => {
        if (activePointerId !== null || (event.pointerType === 'mouse' && event.button !== 0)) return;
        stopComparisonIntro();
        flushComparisonPosition();
        dragBounds = slider.getBoundingClientRect(); // layout read only once
        activePointerId = event.pointerId;
        slider.classList.add('is-dragging');
        try { slider.setPointerCapture(event.pointerId); } catch (_) {}
        positionFrom(event);
    });
    slider.addEventListener('pointermove', event => {
        if (activePointerId !== event.pointerId) return;
        positionFrom(event); // one DOM write at most per animation frame
    }, { passive: true });

    function endPointer(event) {
        if (activePointerId !== event.pointerId) return;
        if (event.type === 'pointerup') positionFrom(event);
        flushComparisonPosition();
        activePointerId = null;
        dragBounds = null;
        slider.classList.remove('is-dragging');
        if (slider.hasPointerCapture?.(event.pointerId)) {
            try { slider.releasePointerCapture(event.pointerId); } catch (_) {}
        }
    }
    slider.addEventListener('pointerup', endPointer);
    slider.addEventListener('pointercancel', endPointer);
    slider.addEventListener('lostpointercapture', event => {
        if (activePointerId === event.pointerId) {
            flushComparisonPosition();
            activePointerId = null;
            dragBounds = null;
            slider.classList.remove('is-dragging');
        }
    });

    handle.addEventListener('keydown', event => {
        const next = event.key === 'ArrowLeft' ? comparisonPosition - 5
            : event.key === 'ArrowRight' ? comparisonPosition + 5
            : event.key === 'Home' ? 5
            : event.key === 'End' ? 95 : null;
        if (next === null) return;
        event.preventDefault();
        stopComparisonIntro();
        flushComparisonPosition();
        applyComparisonPosition(next);
    });
    document.getElementById('ba-animate-button')?.addEventListener('click', animateComparison);
    const before = document.getElementById('ba-img-before');
    const after = document.getElementById('ba-img-after');
    if (before && after) {
        before.addEventListener('error', () => {
            if (before.src !== after.src) before.src = after.src;
        });
    }
    applyComparisonPosition(50);
}

function toggleMobileMenu() {
    const menu = document.getElementById('mobile-menu');
    const overlay = document.getElementById('mobile-menu-overlay');
    const toggleButton = document.getElementById('menu-toggle-btn');
    if (!menu) return;

    const isOpen = menu.classList.contains('open');
    if (isOpen) {
        menu.classList.remove('open');
        menu.setAttribute('aria-hidden', 'true');
        toggleButton?.setAttribute('aria-expanded','false');
        if (overlay) overlay.classList.remove('open');
        document.body.style.overflow = '';
    } else {
        menu.classList.add('open');
        menu.setAttribute('aria-hidden', 'false');
        toggleButton?.setAttribute('aria-expanded','true');
        if (overlay) overlay.classList.add('open');
        document.body.style.overflow = 'hidden';
    }
}