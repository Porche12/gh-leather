'use strict';
document.documentElement.classList.add('js');
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
const reveals = document.querySelectorAll('.reveal');
if ('IntersectionObserver' in window && !reducedMotion.matches) {
  const observer = new IntersectionObserver(entries => entries.forEach(entry => {
    if (entry.isIntersecting) { entry.target.classList.add('visible'); observer.unobserve(entry.target); }
  }), { threshold: .08 });
  reveals.forEach(el => observer.observe(el));
} else reveals.forEach(el => el.classList.add('visible'));
const progress = document.querySelector('.reading-progress');
let scrollPending = false;
function updateProgress() {
  const distance = document.documentElement.scrollHeight - window.innerHeight;
  progress.style.transform = `scaleX(${distance > 0 ? Math.min(1, Math.max(0, window.scrollY / distance)) : 0})`;
  scrollPending = false;
}
window.addEventListener('scroll', () => { if (!scrollPending) {scrollPending = true; requestAnimationFrame(updateProgress);} }, {passive:true});
window.addEventListener('resize', updateProgress);updateProgress();
const menuButton = document.querySelector('.menu-toggle');
const mobileNav = document.querySelector('.mobile-nav');
function closeMenu() { menuButton.setAttribute('aria-expanded','false');menuButton.setAttribute('aria-label','Открыть меню');mobileNav.classList.remove('open');mobileNav.inert = true;document.body.classList.remove('modal-open'); }
menuButton.addEventListener('click', () => {
  if (menuButton.getAttribute('aria-expanded') === 'true') return closeMenu();
  menuButton.setAttribute('aria-expanded','true');menuButton.setAttribute('aria-label','Закрыть меню');mobileNav.inert = false;mobileNav.classList.add('open');document.body.classList.add('modal-open');
});
mobileNav.querySelectorAll('a').forEach(a => a.addEventListener('click', closeMenu));
document.addEventListener('keydown', e => {if(e.key === 'Escape' && mobileNav.classList.contains('open')){closeMenu();menuButton.focus();}});
window.matchMedia('(min-width:801px)').addEventListener('change',e=>{if(e.matches)closeMenu();});
// Every price is a range carried from the atelier's existing source calculator.
const services = {
  jacket:{name:'Реставрация кожаной куртки',price:'3 500–5 500 ₽',time:'3–5 рабочих дней'},
  dye:{name:'Покраска кожаной куртки',price:'4 500–7 500 ₽',time:'4–6 рабочих дней'},
  bag:{name:'Реставрация ручек и уголков сумки',price:'2 800–5 000 ₽',time:'2–4 рабочих дня'},
  shoes:{name:'Покраска обуви',price:'2 200–4 500 ₽',time:'2–3 рабочих дня'},
  fur:{name:'Перекрой шубы',price:'9 000–18 000 ₽',time:'5–10 рабочих дней'},
  tailoring:{name:'Индивидуальный пошив кожаной куртки',price:'18 000–35 000 ₽',time:'7–14 рабочих дней'},
  other:{name:'Индивидуальная задача',price:'После осмотра',time:'Обсудим с мастером'}
};
const dialog = document.getElementById('consult-dialog');
const select = document.getElementById('service-select');
function updateEstimate(){const value=services[select.value];document.getElementById('estimate-price').textContent=value.price;document.getElementById('estimate-time').textContent=value.time;}
function openConsult(service){if(service && services[service])select.value=service;updateEstimate();closeMenu();dialog.showModal();document.body.classList.add('modal-open');}
document.querySelectorAll('[data-consult]').forEach(el=>el.addEventListener('click',()=>openConsult()));
document.querySelectorAll('[data-service]').forEach(el=>el.addEventListener('click',()=>openConsult(el.dataset.service)));
select.addEventListener('change',updateEstimate);
document.querySelector('.dialog-close').addEventListener('click',()=>dialog.close());
dialog.addEventListener('close',()=>document.body.classList.remove('modal-open'));
dialog.addEventListener('click',e=>{if(e.target===dialog){const rect=dialog.getBoundingClientRect();if(e.clientX<rect.left||e.clientX>rect.right||e.clientY<rect.top||e.clientY>rect.bottom)dialog.close();}});
document.getElementById('consult-form').addEventListener('submit',e=>{
  e.preventDefault();
  const note=document.getElementById('request-note').value.trim();
  const message=`Здравствуйте, GH-Leather! Хочу обсудить услугу: ${services[select.value].name}.${note?'\n'+note:''}\nПодскажите, пожалуйста, возможности восстановления, стоимость и сроки. Фото вещи прикреплю в этом чате.`;
  window.open('https://wa.me/79275103299?text='+encodeURIComponent(message),'_blank','noopener,noreferrer');
});
const comparison=document.querySelector('.comparison');
const range=document.getElementById('compare-range');
function updateSplit(){comparison.style.setProperty('--split',range.value+'%');range.setAttribute('aria-valuetext',`Показано ${range.value}% изображения до реставрации`);}
range.addEventListener('input',updateSplit);
const examples={
 jacket:{before:'images/studio_jacket_before.jpg',after:'images/studio_jacket_after.jpg',source:'ReLeather',url:'https://www.releather.com/leather-restoration-jackets-coats',thing:'Кожаная куртка'},
 bag:{before:'images/studio_bag_before.jpg',after:'images/studio_bag_after.jpg',source:'Doria Bag Spa',url:'https://doriabagspa.com/pages/gallery',thing:'Кожаная сумка'}
};
document.querySelectorAll('[data-compare]').forEach(button=>button.addEventListener('click',()=>{
 const value=examples[button.dataset.compare];
 document.querySelectorAll('[data-compare]').forEach(b=>{b.classList.toggle('active',b===button);b.setAttribute('aria-pressed',String(b===button));});
 const before=document.getElementById('before-img'),after=document.getElementById('after-img');
 before.src=value.before;before.alt=value.thing+' до реставрации';after.src=value.after;after.alt=value.thing+' после реставрации мастерской '+value.source;
 const source=document.getElementById('compare-source');source.textContent=value.source+' ↗';source.href=value.url;
 range.value=50;updateSplit();
}));
// Native details retain keyboard support and work without JavaScript.
document.querySelectorAll('.faq details').forEach(detail=>detail.addEventListener('toggle',()=>{if(detail.open)document.querySelectorAll('.faq details').forEach(other=>{if(other!==detail)other.open=false;});}));
document.getElementById('year').textContent=new Date().getFullYear();
