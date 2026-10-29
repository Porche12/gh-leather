/**
 * GH-LEATHER — Luxury Atelier Interactive Application
 * Optimized for Mobile & Desktop Performance
 */

// Services Data Catalog
const SERVICES_DATA = [
    {
        id: 'rest-jacket',
        category: 'restoration',
        title: 'Реставрация кожаных курток',
        desc: 'Устранение задиров, порезов, глубоких потертостей воротника и манжет. Восстановление эластичности и заводского слоя кожи.',
        priceFrom: 'от 3 500 ₽',
        time: '3–5 дней',
        badge: 'Хит сезона',
        icon: 'sparkles'
    },
    {
        id: 'rest-bag',
        category: 'restoration',
        title: 'Реставрация сумок и чемоданов',
        desc: 'Восстановление ручек, уголков, замена молний Raccagni/YKK, реставрация формы и подкладки брендовых сумок (Louis Vuitton, Gucci, Prada).',
        priceFrom: 'от 2 800 ₽',
        time: '2–4 дня',
        badge: 'Брендовый уход',
        icon: 'briefcase'
    },
    {
        id: 'color-jacket',
        category: 'coloring',
        title: 'Глубокая покраска кожаных курток',
        desc: 'Полное заводское восстановление цвета или перекраска в новый оттенок. Защитный матовый или глянцевый топ-лак Saphir (Франция).',
        priceFrom: 'от 4 500 ₽',
        time: '4–6 дней',
        badge: 'Палитра 500+ цветов',
        icon: 'paint-brush'
    },
    {
        id: 'color-shoes',
        category: 'coloring',
        title: 'Покраска и спа-уход для обуви',
        desc: 'Чистка от реагентов, выведение пятен, локальная и полная покраска туфель, ботинок и сапог с защитной нано-пропиткой.',
        priceFrom: 'от 2 200 ₽',
        time: '2–3 дня',
        badge: 'Saphir Medaille',
        icon: 'footprints'
    },
    {
        id: 'tailor-jacket',
        category: 'tailoring',
        title: 'Индивидуальный пошив курток',
        desc: 'Пошив мужских и женских курток, косух, бомберов и плащей по вашим меркам из премиальной итальянской кожи Nappa и замши.',
        priceFrom: 'от 18 000 ₽',
        time: '7–14 дней',
        badge: 'Эксклюзивный покрой',
        icon: 'scissors'
    },
    {
        id: 'tailor-bag',
        category: 'tailoring',
        title: 'Пошив сумок и аксессуаров',
        desc: 'Ручной пошив портмоне, ремней, сумок и рюкзаков седельным швом вощеной нитью. Пожизненная гарантия на разрыв нити.',
        priceFrom: 'от 4 900 ₽',
        time: '3–7 дней',
        badge: '100% Ручная работа',
        icon: 'shopping-bag'
    },
    {
        id: 'fur-remodel',
        category: 'fur',
        title: 'Полный перекрой шуб и дубленок',
        desc: 'Перешив устаревших длинных шуб в стильные полушубки, парки, жилеты или косухи. Укорачивание, изменение проймы, капюшона.',
        priceFrom: 'от 9 500 ₽',
        time: '5–10 дней',
        badge: 'Трендовый силуэт',
        icon: 'feather'
    },
    {
        id: 'auto-interior',
        category: 'auto',
        title: 'Реставрация салонов авто и мебели',
        desc: 'Локальный ремонт прожогов, трещин и разрывов на сиденьях, перетяжка рулей премиальной перфорированной Nappa, реставрация диванов.',
        priceFrom: 'от 5 000 ₽',
        time: '1–4 дня',
        badge: 'Стойкость к износу',
        icon: 'car'
    }
];

// Initialize on DOM Ready
document.addEventListener('DOMContentLoaded', () => {
    // Icons & AOS
    if (window.lucide) lucide.createIcons();
    if (window.AOS) AOS.init({ duration: 800, once: true });

    renderServices('all');
    initBeforeAfterSlider();
    initCalculatorControls();
    initOrdersDatabase();
    initPhoneMasks();
});

// ================= Services Renderer & Filter =================
function renderServices(filter = 'all') {
    const grid = document.getElementById('services-grid');
    if (!grid) return;

    const filtered = filter === 'all' 
        ? SERVICES_DATA 
        : SERVICES_DATA.filter(s => s.category === filter);

    grid.innerHTML = filtered.map(item => `
        <div class="service-card" data-aos="fade-up">
            <div class="service-header">
                <div class="service-icon"><i data-lucide="${item.icon}"></i></div>
                <span class="service-badge">${item.badge}</span>
            </div>
            <h3 class="service-title">${item.title}</h3>
            <p class="service-desc">${item.desc}</p>
            <div class="service-meta">
                <div class="service-price">
                    <span class="price-from">Стоимость:</span>
                    <span class="price-amount">${item.priceFrom}</span>
                </div>
                <button class="btn btn-luxury" onclick="openModal('${item.title}')">
                    Заказать
                </button>
            </div>
        </div>
    `).join('');

    if (window.lucide) lucide.createIcons();
}

function filterServices(category, btnElement) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    if (btnElement) {
        btnElement.classList.add('active');
    }
    renderServices(category);
}

// ================= Interactive Before / After Drag Slider =================
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

// ================= Interactive Calculator =================
let currentBasePrice = 3500;
let currentMaterialMult = 1.0;
let currentDuration = '3–5 дней';

function initCalculatorControls() {
    const typeOpts = document.querySelectorAll('#type-selector .calc-option');
    typeOpts.forEach(opt => {
        opt.addEventListener('click', () => {
            typeOpts.forEach(o => o.classList.remove('active'));
            opt.classList.add('active');
            currentBasePrice = parseInt(opt.getAttribute('data-base')) || 3500;
            
            const type = opt.getAttribute('data-type');
            if (type === 'tailoring') currentDuration = '7–14 дней';
            else if (type === 'fur') currentDuration = '5–10 дней';
            else if (type === 'coloring') currentDuration = '4–6 дней';
            else currentDuration = '3–5 дней';

            calculateTotal();
        });
    });

    calculateTotal();
}

function setMaterial(btn) {
    document.querySelectorAll('#material-selector .pill-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    currentMaterialMult = parseFloat(btn.getAttribute('data-mat')) || 1.0;
    calculateTotal();
}

function calculateTotal() {
    const itemSelect = document.getElementById('item-selector');
    const itemMult = itemSelect ? parseFloat(itemSelect.value) : 1.0;

    let total = currentBasePrice * itemMult * currentMaterialMult;

    // Checkboxes
    const optWater = document.getElementById('opt-waterproof');
    const optHard = document.getElementById('opt-hardware');
    const optExp = document.getElementById('opt-express');

    if (optWater && optWater.checked) total += parseFloat(optWater.value);
    if (optHard && optHard.checked) total += parseFloat(optHard.value);
    if (optExp && optExp.checked) {
        total += parseFloat(optExp.value);
        currentDuration = '48 часов (Экспресс)';
    }

    const priceEl = document.getElementById('calc-final-price');
    const timeEl = document.getElementById('calc-final-time');
    if (priceEl) priceEl.textContent = `${Math.round(total).toLocaleString('ru-RU')} ₽`;
    if (timeEl) timeEl.innerHTML = `<i data-lucide="clock"></i> Срок: ${currentDuration}`;

    if (window.lucide) lucide.createIcons();
}

function bookCalculatedOrder() {
    const price = document.getElementById('calc-final-price').textContent;
    const itemSelect = document.getElementById('item-selector');
    const itemText = itemSelect.options[itemSelect.selectedIndex].text;
    openModal(`Расчёт: ${itemText} (${price})`);
}

// ================= Dexie Client Orders Database =================
let ordersDb;
function initOrdersDatabase() {
    if (!window.Dexie) return;
    ordersDb = new Dexie('GHLeatherOrdersDB');
    ordersDb.version(1).stores({
        orders: '++id, item, material, price, date, status'
    });

    loadOrdersTable();
}

async function loadOrdersTable() {
    if (!ordersDb) return;
    const orders = await ordersDb.orders.reverse().limit(6).toArray();
    const tbody = document.getElementById('orders-tbody');
    if (!tbody) return;

    if (orders.length === 0) {
        // Initial sample orders
        await ordersDb.orders.bulkAdd([
            { item: 'Куртка Brioni (покраска и реставрация)', material: 'Кожа Nappa', price: '7 800 ₽', date: 'Сегодня', status: 'В работе' },
            { item: 'Норковая шуба (перекрой в автоледи)', material: 'Мех норки', price: '14 500 ₽', date: 'Вчера', status: 'Примерка' },
            { item: 'Сумка Chanel Boy (восстановление цвета)', material: 'Телячья кожа', price: '6 200 ₽', date: '28 окт', status: 'Готово к выдаче' }
        ]);
        return loadOrdersTable();
    }

    tbody.innerHTML = orders.map(o => `
        <tr>
            <td><strong>#${o.id + 1040}</strong></td>
            <td>${o.item}</td>
            <td><span style="color: #cbd5e1;">${o.material}</span></td>
            <td><strong style="color: #f5e6b3;">${o.price}</strong></td>
            <td><span class="order-badge">${o.status}</span></td>
        </tr>
    `).join('');
}

// ================= Modal & Mobile Navigation =================
function openModal(serviceTitle = 'Запись на консультацию') {
    const modal = document.getElementById('bookingModal');
    const heading = document.getElementById('modal-heading');
    const sName = document.getElementById('modal-service-name');
    if (heading) heading.textContent = serviceTitle;
    if (sName) sName.value = serviceTitle;
    if (modal) modal.classList.add('open');
}

function closeModal() {
    const modal = document.getElementById('bookingModal');
    if (modal) modal.classList.remove('open');
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

function scrollToElement(id) {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth' });
}

function initPhoneMasks() {
    const inputs = document.querySelectorAll('input[type="tel"]');
    inputs.forEach(input => {
        input.addEventListener('input', (e) => {
            let val = e.target.value.replace(/\\D/g, '');
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

// ================= Form Submissions =================
async function handleModalSubmit(e) {
    e.preventDefault();
    const name = document.getElementById('m-name').value;
    const phone = document.getElementById('m-phone').value;
    const service = document.getElementById('modal-service-name').value;

    closeModal();
    fireConfetti();

    if (ordersDb) {
        await ordersDb.orders.add({
            item: service,
            material: 'Индивидуально',
            price: 'Уточняется',
            date: 'Только что',
            status: 'Новая заявка'
        });
        loadOrdersTable();
    }

    showToast(`Спасибо, ${name}! Заявка на «${service}» принята. Мастер свяжется с вами по номеру ${phone}`, 'success');
}

async function handleContactSubmit(e) {
    e.preventDefault();
    const name = document.getElementById('form-name').value;
    const phone = document.getElementById('form-phone').value;
    const details = document.getElementById('form-details').value;

    fireConfetti();

    if (ordersDb) {
        await ordersDb.orders.add({
            item: details ? details.substring(0, 35) + '...' : 'Оценка по фото',
            material: 'Натуральная кожа',
            price: 'Скидка 10%',
            date: 'Только что',
            status: 'Оценка технолога'
        });
        loadOrdersTable();
    }

    document.getElementById('contact-form').reset();
    showToast(`Заявка принята, ${name}! Мастер готовит расчет со скидкой 10% и перезвонит на ${phone}`, 'success');
}

function fireConfetti() {
    if (window.confetti) {
        confetti({
            particleCount: 85,
            spread: 70,
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
