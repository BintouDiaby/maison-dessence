/* =========================
   Maison dâessence â app.js
   ========================= */

/* ---------- Config ---------- */
const BACKEND_URL = window.BACKEND_URL || 'http://127.0.0.1:8000';
const CART_KEY = 'md_cart_v1';

// Endpoints centralisÃ©s
const API = {
  // Produits publics
  products:        BACKEND_URL + '/api/products/',
  productDetail:   (id) => BACKEND_URL + `/api/products/${id}/`,

  // Auth & profil
  token:           BACKEND_URL + '/api/auth/token/',
  register:        BACKEND_URL + '/api/auth/register/',
  profile:         BACKEND_URL + '/api/auth/profile/',
  impersonate:     BACKEND_URL + '/api/auth/impersonate/',

  // Vendeur
  meVendor:        BACKEND_URL + '/api/vendors/me/',
  myProducts:      BACKEND_URL + '/api/products/?mine=1',
  createProduct:   BACKEND_URL + '/api/products/create/',
  updateProduct:   (id) => BACKEND_URL + `/api/products/${id}/update/`,
  deleteProduct:   (id) => BACKEND_URL + `/api/products/${id}/delete/`,
  uploadImage:     (id) => BACKEND_URL + `/api/products/${id}/upload-image/`,

  // Commandes / Paiement (optionnel Stripe + mock)
  stripeConfig:    BACKEND_URL + '/api/orders/stripe/config/',
  stripeIntent:    BACKEND_URL + '/api/orders/stripe/create-payment-intent/',
  payMock:         BACKEND_URL + '/api/orders/pay/mock/',
  cinetpayCreate:  BACKEND_URL + '/api/orders/cinetpay/create/',
};

/* ---------- Helpers DOM/Utils ---------- */
function qs(s){ return document.querySelector(s); }
function qsa(s){ return Array.from(document.querySelectorAll(s)); }
function getQueryParam(name){ try{ const p = new URLSearchParams(location.search); return p.get(name); }catch(_){ return null; } }
function escapeHtml(s){ return (s+'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }

function showToast(msg, timeout=2200){
  let el = qs('#md-toast');
  if(!el){
    el = document.createElement('div');
    el.id='md-toast';
    Object.assign(el.style, {
      position:'fixed', right:'18px', bottom:'18px',
      background:'#0f172a', color:'#fff', padding:'12px 16px',
      borderRadius:'8px', boxShadow:'0 8px 24px rgba(2,6,23,.4)',
      zIndex:9999, fontSize:'14px', transition:'opacity .25s, transform .25s'
    });
    document.body.appendChild(el);
  }
  el.textContent = msg;
  el.style.opacity = '1';
  el.style.transform = 'translateY(0)';
  clearTimeout(el._hideTimer);
  el._hideTimer = setTimeout(()=>{
    el.style.opacity='0';
    el.style.transform='translateY(8px)';
  }, timeout);
}

/* ---------- Panier (localStorage) ---------- */
function loadCart(){ try{ return JSON.parse(localStorage.getItem(CART_KEY)||'[]'); }catch(_){ return []; } }
function saveCart(c){ localStorage.setItem(CART_KEY, JSON.stringify(c)); renderCartCount(); renderDrawerItems(); }
function addToCart(product, qty=1){
  // Bloquer l'ajout au panier pour les visiteurs non connectÃ©s
  const token = localStorage.getItem('md_access_token');
  if(!token){
    showToast('Connectez-vous pour ajouter au panier');
    setTimeout(()=> window.location.href = '/login.html', 600);
    return;
  }

  const cart = loadCart();
  const i = cart.findIndex(x=>x.id===product.id);
  if(i>=0) cart[i].qty += qty; else cart.push({id:product.id, name:product.name, price:product.price, qty});
  saveCart(cart);
  showToast(`${product.name} ajoutÃ© au panier`);
}
function clearCart(){ saveCart([]); }
function cartTotal(){ return loadCart().reduce((s,i)=> s + (Number(i.price)||0)*i.qty, 0); }
function renderCartCount(){ const el = qs('#cart-count'); if(!el) return; el.textContent = loadCart().reduce((s,i)=>s+i.qty,0); }
function renderDrawerItems(){
  const root=qs('#drawer-items'); if(!root) return;
  const cart=loadCart();
  root.innerHTML='';
  if(!cart.length){
    root.innerHTML='<div style="padding:18px;color:#666">Votre panier est vide.</div>';
    const t=qs('#drawer-total'); if(t) t.textContent='â¬0.00';
    return;
  }
  cart.forEach(it=>{
    const row=document.createElement('div');
    row.style.display='flex'; row.style.justifyContent='space-between'; row.style.padding='8px 12px';
    row.innerHTML = `<div>${escapeHtml(it.name)} x${it.qty}</div><div>â¬${(Number(it.price||0)*it.qty).toFixed(2)}</div>`;
    root.appendChild(row);
  });
  const t=qs('#drawer-total'); if(t) t.textContent='â¬'+cartTotal().toFixed(2);
}
function bindCartDrawer(){
  const open=qs('#open-cart'), close=qs('#close-drawer'), drawer=qs('#cart-drawer');
  if(open) open.addEventListener('click', ()=>{
    const p = (location.pathname||'').split('/').pop();
    if(p==='cart.html' || p==='checkout.html'){ drawer?.classList.add('open'); }
    else window.location.href='/cart.html';
  });
  if(close) close.addEventListener('click', ()=> drawer?.classList.remove('open'));
}

/* ---------- Auth helpers ---------- */
function getAuthToken(){ return localStorage.getItem('md_access_token'); }
function authHeaders(){ const t = getAuthToken(); return t ? { 'Authorization': 'Bearer ' + t, 'Content-Type': 'application/json' } : { 'Content-Type': 'application/json' }; }

/* ---------- Likes & Wishlist (frontend) ---------- */
async function toggleLike(productId, onSuccess){
  const token = getAuthToken();
  if(!token){ showToast('Connectez-vous pour liker'); setTimeout(()=> window.location.href='/login.html',600); return; }
  try{
    const res = await fetch(BACKEND_URL + `/api/products/${productId}/like/`, { method:'POST', headers: authHeaders() });
    if(!res.ok){ showToast('Erreur'); return; }
    const j = await res.json();
    if(onSuccess) onSuccess(j);
  }catch(e){ showToast('Erreur rÃ©seau'); }
}

async function toggleWishlist(productId, onSuccess){
  const token = getAuthToken();
  if(!token){ showToast('Connectez-vous pour ajouter Ã  la wishlist'); setTimeout(()=> window.location.href='/login.html',600); return; }
  try{
    const res = await fetch(BACKEND_URL + `/api/products/${productId}/wishlist/`, { method:'POST', headers: authHeaders() });
    if(!res.ok){ showToast('Erreur'); return; }
    const j = await res.json();
    if(onSuccess) onSuccess(j);
    showToast(j.in_wishlist ? 'AjoutÃ© Ã  la wishlist' : 'RetirÃ© de la wishlist');
  }catch(e){ showToast('Erreur rÃ©seau'); }
}

function enhanceCardWithActions(cardEl, product){
  // Add small like/wishlist buttons to a product card (if not already present)
  if(!cardEl) return;
  if(cardEl.querySelector('.md-actions')) return; // already added
  const actions = document.createElement('div');
  actions.className = 'md-actions';
  actions.style.display = 'flex'; actions.style.gap='8px'; actions.style.marginTop='8px';
  const likeBtn = document.createElement('button');
  likeBtn.className='btn-like'; likeBtn.title='J\'aime';
  likeBtn.innerHTML = `<span class="like-icon">${product.is_liked? 'â¥':'â¡'}</span> <span class="like-count">${product.likes_count||0}</span>`;
  likeBtn.addEventListener('click', async (e)=>{ e.stopPropagation(); await toggleLike(product.id, (res)=>{ likeBtn.querySelector('.like-icon').textContent = res.liked? 'â¥':'â¡'; likeBtn.querySelector('.like-count').textContent = res.likes_count; showToast(res.liked ? 'Vous aimez ce produit' : 'Like retirÃ©'); }); });

  const wishBtn = document.createElement('button');
  wishBtn.className='btn-wish'; wishBtn.title='Wishlist';
  wishBtn.innerHTML = `<span class="wish-icon">${product.is_in_wishlist? 'â':'â'}</span> <span class="wish-count">${product.wishlist_count||0}</span>`;
  wishBtn.addEventListener('click', async (e)=>{ e.stopPropagation(); await toggleWishlist(product.id, (res)=>{ wishBtn.querySelector('.wish-icon').textContent = res.in_wishlist? 'â':'â'; wishBtn.querySelector('.wish-count').textContent = res.wishlist_count; }); });

  actions.appendChild(likeBtn); actions.appendChild(wishBtn);
  const body = cardEl.querySelector('.body');
  if(body) body.appendChild(actions);
}

/* ---------- Data produits (public) ---------- */
async function fetchProducts(){
  try{
    const res = await fetch(API.products);
    if(!res.ok) throw 0;
    return await res.json();
  }catch(_){ return []; }
}

async function renderIndex(){
  const grid = qs('#products-grid'); if(!grid) return;
  const list = await fetchProducts();
  grid.innerHTML = '';
  list.slice(0,9).forEach((p, idx)=>{
    const card = document.createElement('div');
    card.className='card fade-in'; card.style.animationDelay=(idx*80)+'ms';
    card.innerHTML = `
      <img src="${p.image_url || 'https://images.unsplash.com/photo-1519741490371-66a3fb4f3f4b?q=80&w=1200&auto=format&fit=crop'}"/>
      <div class="body">
        <div class="title">${escapeHtml(p.name)}</div>
        <div class="meta">${escapeHtml(p.family||'')}</div>
        <div class="row">
          <div class="price">â¬${p.price}</div>
          <div>
            <a class="btn" href="/product.html?id=${p.id}">Voir</a>
            <button class="btn btn-primary" data-add="${p.id}">Ajouter</button>
          </div>
        </div>
      </div>`;
    grid.appendChild(card);
    enhanceCardWithActions(card, p);
  });
  // bind add
  qsa('[data-add]').forEach(b=> b.addEventListener('click', async ()=>{
    const id = +b.dataset.add;
    const list = await fetchProducts();
    const p = list.find(x=>x.id===id);
    if(p) addToCart(p,1);
  }));
}

async function renderProducts(q){
  const grid = qs('#products-grid'); if(!grid) return;
  const list = await fetchProducts();
  grid.innerHTML='';
  const filt = (q||'').toLowerCase().trim();
  const items = filt ? list.filter(p=>{
    return (p.name||'').toLowerCase().includes(filt)
      || (p.description||'').toLowerCase().includes(filt)
      || (p.family||'').toLowerCase().includes(filt)
      || (Array.isArray(p.tags)? p.tags.join(' ').toLowerCase().includes(filt): false);
  }): list;
  items.forEach((p, idx)=>{
    const card=document.createElement('div');
    card.className='card fade-in'; card.style.animationDelay=(idx*40)+'ms';
    card.innerHTML = `
      <img src="${p.image_url || 'https://images.unsplash.com/photo-1519741490371-66a3fb4f3f4b?q=80&w=1200&auto=format&fit=crop'}"/>
      <div class="body">
        <div class="title">${escapeHtml(p.name)}</div>
        <div class="meta">${escapeHtml(p.family||'')}</div>
        <div class="row">
          <div class="price">â¬${p.price}</div>
          <div>
            <a class="btn" href="/product.html?id=${p.id}">Voir</a>
            <button class="btn btn-primary" data-add="${p.id}">Ajouter</button>
          </div>
        </div>
      </div>`;
    grid.appendChild(card);
    enhanceCardWithActions(card, p);
  });
  qsa('[data-add]').forEach(b=> b.addEventListener('click', async ()=>{
    const id = +b.dataset.add;
    const list = await fetchProducts();
    const p = list.find(x=>x.id===id);
    if(p) addToCart(p,1);
  }));
}

async function renderProductPage(){
  const root = qs('#product-detail'); if(!root) return;
  const id = +(getQueryParam('id')||0); if(!id) return;
  const r = await fetch(API.productDetail(id));
  if(!r.ok) return;
  const p = await r.json();

  const nameEl = qs('#p-name');
  // afficher en premier le nom du produit, puis afficher le vendeur/boutique sÃ©parÃ©ment
  if(nameEl) nameEl.textContent = p.name || '';
  const sellerEl = qs('#p-seller'); if(sellerEl) sellerEl.textContent = p.owner || '';
  const shopEl = qs('#p-shop'); if(shopEl) shopEl.textContent = p.owner_shop || '';
  const priceEl = qs('#p-price'); if(priceEl) priceEl.textContent = 'â¬'+p.price;
  const descEl = qs('#p-desc'); if(descEl) descEl.textContent = p.description || '';
  const imgEl = qs('#p-img'); if(imgEl) imgEl.src = p.image_url || '/static/images/placeholder_900x600.svg';
  const fam = qs('#p-family'); if(fam) fam.textContent = p.family || '';
  // afficher vendeur / boutique si fournis par l'API (dÃ©jÃ  assignÃ©s plus haut)

  const addBtn = qs('#add-single'); if(addBtn) addBtn.addEventListener('click', ()=> addToCart(p,1));

  // Like / Wishlist buttons on product page
  const likeIcon = qs('#p-like-icon'); const likeCount = qs('#p-like-count');
  const wishIcon = qs('#p-wishlist-icon'); const wishCount = qs('#p-wishlist-count');
  if(likeIcon) likeIcon.textContent = p.is_liked ? 'â¥' : 'â¡';
  if(likeCount) likeCount.textContent = (p.likes_count || 0);
  if(wishIcon) wishIcon.textContent = p.is_in_wishlist ? 'â' : 'â';
  if(wishCount) wishCount.textContent = (p.wishlist_count || 0);

  const likeBtn = qs('#p-like-btn'); if(likeBtn) likeBtn.addEventListener('click', async ()=>{
    await toggleLike(p.id, (res)=>{
      if(likeIcon) likeIcon.textContent = res.liked ? 'â¥' : 'â¡';
      if(likeCount) likeCount.textContent = res.likes_count;
      // update local p
      p.is_liked = res.liked; p.likes_count = res.likes_count;
    });
  });

  const wishBtn = qs('#p-wishlist-btn'); if(wishBtn) wishBtn.addEventListener('click', async ()=>{
    await toggleWishlist(p.id, (res)=>{
      if(wishIcon) wishIcon.textContent = res.in_wishlist ? 'â' : 'â';
      if(wishCount) wishCount.textContent = res.wishlist_count;
      p.is_in_wishlist = res.in_wishlist; p.wishlist_count = res.wishlist_count;
    });
  });

  // Charger produits similaires via le recommender (fallback: liste publique)
  (async ()=>{
    const similarRoot = qs('#similar-list'); if(!similarRoot) return;
    similarRoot.innerHTML = '';
    let similar = [];
    try{
      const resp = await fetch((window.BACKEND_URL || BACKEND_URL) + `/recommender/products/${id}/?k=4`);
      if(resp.ok) similar = await resp.json();
    }catch(_){ similar = []; }

    if(!similar || !similar.length){
      // fallback: charger quelques produits publics et filtrer
      try{
        const all = await fetchProducts();
        similar = all.filter(x=> x.id !== p.id).slice(0,4);
      }catch(_){ similar = []; }
    }

    similar.forEach((s, idx)=>{
      const card = document.createElement('div');
      card.className = 'card';
      card.innerHTML = `
        <img src="${s.image_url || 'https://images.unsplash.com/photo-1519741490371-66a3fb4f3f4b?q=80&w=1200&auto=format&fit=crop'}" />
        <div class="body">
          <div class="title">${escapeHtml(s.name)}</div>
          <div class="meta">${escapeHtml(s.family||'')}</div>
          <div class="row">
            <div class="price">â¬${s.price}</div>
            <div>
              <a class="btn" href="/product.html?id=${s.id}">Voir</a>
              <button class="btn btn-primary" data-add="${s.id}">Ajouter</button>
            </div>
          </div>
        </div>`;
      similarRoot.appendChild(card);
      enhanceCardWithActions(card, s);
    });

    // bind add buttons
    qsa('#similar-list [data-add]').forEach(b=> b.addEventListener('click', async ()=>{
      const id = +b.dataset.add;
      const list = await fetchProducts();
      const prod = list.find(x=>x.id===id);
      if(prod) addToCart(prod,1);
    }));
  })();
}

/* ---------- Auth (login/signup/profile) ---------- */
async function updateAuthLink(){
  const nav = document.querySelector('header nav');
  if(!nav) return;

  const navLinks = Array.from(nav.querySelectorAll('a'));
  const loginLink = navLinks.find(a => a.getAttribute('href') === '/login.html');
  if(!loginLink) return;

  // clean anciens liens
  nav.querySelectorAll('a[data-account-link]').forEach(a => a.remove());

  const token = localStorage.getItem('md_access_token');
  if(!token){
    const newLink = loginLink.cloneNode(true);
    newLink.textContent = 'Se connecter';
    newLink.setAttribute('href', '/login.html');
    loginLink.parentNode.replaceChild(newLink, loginLink);
    return;
  }

  // Tente profile (optionnel) + vendor status (obligatoire)
  let profile = null;
  try{
    const pres = await fetch('/api/auth/profile/', { headers: { 'Authorization': 'Bearer ' + token } });
    if(pres.ok) profile = await pres.json();
  }catch(_){} // on ignore l'erreur â le profil est optionnel pour lâUI

  let vendor = { is_vendor: false };
  try{
    const vres = await fetch('/api/vendors/me/', { headers: { 'Authorization': 'Bearer ' + token } });
    if(vres.ok) vendor = await vres.json();
  }catch(e){
    // Si on ne peut pas lire vendors/me, on rÃ©initialise (token sÃ»rement invalide)
    localStorage.removeItem('md_access_token');
    localStorage.removeItem('md_refresh_token');
    const newLink = loginLink.cloneNode(true);
    newLink.textContent = 'Se connecter';
    newLink.setAttribute('href', '/login.html');
    loginLink.parentNode.replaceChild(newLink, loginLink);
    return;
  }

  // Masquer le lien "Devenir vendeur" si l'utilisateur est dÃ©jÃ  vendeur
  try{
    const becomeLink = nav.querySelector('a[href="/signup.html?role=vendor"]');
    if(becomeLink){
      if(vendor && vendor.is_vendor) becomeLink.style.display = 'none';
      else becomeLink.style.display = '';
    }
  }catch(_){ }

  // Remplacer par "Se dÃ©connecter"
  const logoutLink = loginLink.cloneNode(true);
  logoutLink.textContent = 'Se dÃ©connecter';
  logoutLink.setAttribute('href', '#');
  logoutLink.setAttribute('data-account-link', 'true');
  logoutLink.addEventListener('click', (ev)=>{
    ev.preventDefault();
    localStorage.removeItem('md_access_token');
    localStorage.removeItem('md_refresh_token');
    if(typeof showToast === 'function') showToast('DÃ©connectÃ©');
    setTimeout(()=> window.location.href = '/', 300);
  });
  loginLink.parentNode.replaceChild(logoutLink, loginLink);

  // Lien Profil
  const profileLink = document.createElement('a');
  profileLink.href = '/profile.html';
  profileLink.textContent = 'Profil';
  profileLink.setAttribute('data-account-link', 'true');
  profileLink.style.marginLeft = '8px';
  logoutLink.parentNode.insertBefore(profileLink, logoutLink.nextSibling);

  // Lien Dashboard vendeur si is_vendor
  if(vendor && vendor.is_vendor){
    const dashLink = document.createElement('a');
    dashLink.href = '/vendor_dashboard.html';
    dashLink.textContent = 'Dashboard vendeur';
    dashLink.setAttribute('data-account-link', 'true');
    dashLink.style.marginLeft = '8px';
    logoutLink.parentNode.insertBefore(dashLink, profileLink);
  }

  // Lien Admin si superuser
  if(profile && profile.is_superuser){
    const adminLink = document.createElement('a');
    adminLink.href = '/admin/';
    adminLink.textContent = 'Admin';
    adminLink.setAttribute('data-account-link', 'true');
    adminLink.style.marginLeft = '8px';
    logoutLink.parentNode.insertBefore(adminLink, profileLink.nextSibling);
  }
}


function bindLogin(){
  const f = qs('#login-form'); if(!f) return;
  f.addEventListener('submit', async (e)=>{
    e.preventDefault();
    const idField = f.querySelector('input[name=email]') || f.querySelector('input[name=username]');
    const password = f.querySelector('input[name=password]').value;
    const idValue = (idField?.value || '').trim();
    const payload = idValue.includes('@') ? { email:idValue, password } : { username:idValue, password };

    try{
      const res = await fetch(API.token, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload) });
      if(!res.ok){ alert('Ãchec connexion'); return; }
      const data = await res.json();
      localStorage.setItem('md_access_token', data.access);
      localStorage.setItem('md_refresh_token', data.refresh);

      await updateAuthLink();
  // Si une intention de devenir vendeur Ã©tait en attente (signup), tenter l'upgrade
  try{ await upgradeToVendorIfPending(data.access); }catch(e){}

      // si vendeur â rediriger dashboard
      try{
        const vm = await fetch(API.meVendor, { headers:{ Authorization:'Bearer '+data.access }});
        if(vm.ok){ const j = await vm.json(); if(j.is_vendor){ showToast('ConnectÃ© (vendeur)'); location.href='/vendor_dashboard.html'; return; } }
      }catch(_){}

      showToast('ConnectÃ©');
      location.href = '/';
    }catch(_){ alert('Erreur rÃ©seau'); }
  });
}


async function upgradeToVendorIfPending(token) {
  // essaie de rÃ©cupÃ©rer lâintention vendeur
  let pending = null;
  try { pending = JSON.parse(sessionStorage.getItem('pending_vendor') || 'null'); } catch(_) {}
  if (!pending) return;

  // vÃ©rifie que la personne connectÃ©e correspond au mÃªme email
  try {
    const pres = await fetch('/api/auth/profile/', { headers: { 'Authorization': 'Bearer ' + token } });
    if (!pres.ok) return;
    const profile = await pres.json();
    const sameUser = (profile && (profile.email || '').toLowerCase() === (pending.email || '').toLowerCase());
    if (!sameUser) return;
  } catch(_) { return; }

  // tente lâendpoint officiel si prÃ©sent
  let ok = false;
  try {
    console.log('upgradeToVendorIfPending: calling /api/vendors/upgrade/ with', pending);
    const r1 = await fetch('/api/vendors/upgrade/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
      body: JSON.stringify({ shop_name: pending.shop_name || '', phone: pending.phone || '' })
    });
    console.log('upgradeToVendorIfPending: /api/vendors/upgrade/ status', r1.status);
    try{ const j = await r1.clone().json().catch(()=>null); console.log('upgradeToVendorIfPending: /api/vendors/upgrade/ body', j); }catch(_){}
    ok = r1.ok;
  } catch(_) {}

  // fallback si upgrade/ nâexiste pas chez toi : on tente /vendors/me/ en POST
  if (!ok) {
    try {
      console.log('upgradeToVendorIfPending: fallback calling POST /api/vendors/me/');
      const r2 = await fetch('/api/vendors/me/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
        body: JSON.stringify({ shop_name: pending.shop_name || '', phone: pending.phone || '' })
      });
      console.log('upgradeToVendorIfPending: /api/vendors/me/ POST status', r2.status);
      try{ const j2 = await r2.clone().json().catch(()=>null); console.log('upgradeToVendorIfPending: /api/vendors/me/ POST body', j2); }catch(_){}
      ok = r2.ok;
    } catch(_) {}
  }

  if (ok) {
    try { sessionStorage.removeItem('pending_vendor'); } catch(_) {}
    // envoie vers le dashboard vendeur
    window.location.href = '/vendor_dashboard.html';
  }
}



function bindSignup(){
  const f = qs('#signup-form'); if(!f) return;
  f.addEventListener('submit', async (e)=>{
    e.preventDefault();
    const data = {
      username: f.querySelector('input[name=username]').value,
      email: f.querySelector('input[name=email]').value,
      password: f.querySelector('input[name=password]').value,
      first_name: f.querySelector('input[name=first_name]')?.value || '',
      last_name: f.querySelector('input[name=last_name]')?.value || '',
    };
    const feedback = qs('#signup-feedback');
    try{
      const res = await fetch(API.register, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(data) });
      if(res.ok){
        showToast('Compte crÃ©Ã© â connexion en cours...');
        try{
          const lr = await fetch(API.token, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ email:data.email, password:data.password }) });
          if(lr.ok){
            const d = await lr.json();
            localStorage.setItem('md_access_token', d.access);
            localStorage.setItem('md_refresh_token', d.refresh);
            await updateAuthLink();
            showToast('ConnectÃ©');
            setTimeout(()=> location.href='/profile.html', 600);
            return;
          }
        }catch(_){}
        if(feedback) feedback.innerHTML = `Compte crÃ©Ã©. Si la connexion auto Ã©choue, utilisez <a href="/login.html">Se connecter</a>`;
        return;
      }
      const j = await res.json().catch(()=>null);
      const msg = j?.detail || (j? JSON.stringify(j): 'Erreur crÃ©ation');
      if(feedback) feedback.textContent = msg;
      showToast(msg || 'Erreur');
    }catch(_){ showToast('Erreur rÃ©seau'); if(feedback) feedback.textContent='Erreur rÃ©seau'; }
  });
}

/* ---------- Checkout (optionnel) ---------- */
function bindCheckout(){
  const btn = qs('#pay-btn'); if(!btn) return;
  let stripe=null, card=null;

  async function initStripe(){
    try{
      const r = await fetch(API.stripeConfig);
      if(!r.ok) throw 0;
      const cfg = await r.json();
      if(!cfg.publishableKey) throw 0;
      stripe = Stripe(cfg.publishableKey);
      const elements = stripe.elements();
      card = elements.create('card', { hidePostalCode:true, style:{ base:{ fontSize:'16px', color:'#111', fontFamily:'system-ui,Segoe UI,Roboto' } } });
      qs('#card-element') && card.mount('#card-element');
      card && card.on('change', e=>{ const ce=qs('#card-errors'); if(ce) ce.textContent = e.error? e.error.message : ''; });
    }catch(_){}
  }

  function updatePaymentUI(){
    const sel = (document.querySelector('input[name=payment_method]:checked')||{value:'card'}).value;
    const elCard = qs('#card-element');
    const elManual = qs('#card-manual');
    if(sel==='card'){ if(elCard) elCard.style.display=''; if(elManual) elManual.style.display='none'; if(!stripe) initStripe(); }
    else if(sel==='mock'){ if(elCard) elCard.style.display='none'; if(elManual) elManual.style.display=''; }
    else { if(elCard) elCard.style.display='none'; if(elManual) elManual.style.display='none'; }
  }

  btn.addEventListener('click', async ()=>{
    btn.disabled=true; btn.textContent='Traitement...';
    try{
      const items = loadCart();
      if(!items.length){ showToast('Le panier est vide'); btn.disabled=false; btn.textContent='Payer'; return; }
      const buyer = { name: qs('#buyer-name')?.value || '', email: qs('#buyer-email')?.value || '' };
      const selected = (document.querySelector('input[name=payment_method]:checked')||{value:'card'}).value;
      const auth = localStorage.getItem('md_access_token')? { Authorization: 'Bearer '+localStorage.getItem('md_access_token') } : {};

      if(selected==='cinetpay'){
        const r = await fetch(API.cinetpayCreate, { method:'POST', headers:{ 'Content-Type':'application/json', ...auth }, body: JSON.stringify({ items, buyer }) });
        if(!r.ok){ showToast('Impossible dâinitier CinetPay'); btn.disabled=false; btn.textContent='Payer'; return; }
        const j = await r.json();
        if(j.payment_url){ location.href = j.payment_url; return; }
        showToast('Erreur CinetPay'); btn.disabled=false; btn.textContent='Payer'; return;
      }

      if(selected==='mock'){
        const cardNumber = qs('#manual-card-number')?.value.trim();
        const cardExp = qs('#manual-card-exp')?.value.trim();
        const cardCvc = qs('#manual-card-cvc')?.value.trim();
        const cardName = qs('#manual-card-name')?.value.trim();
        if(!cardNumber || !cardExp || !cardCvc){ showToast('Renseignez la carte'); btn.disabled=false; btn.textContent='Payer'; return; }
        let exp_month=null, exp_year=null; const m=cardExp.match(/^(\d{1,2})\s*(?:\/|-)\\s*(\d{2,4})$/);
        if(m){ exp_month=+m[1]; exp_year=+m[2]; if(exp_year<100) exp_year += 2000; }
        const payload = { method:'card', card:{ number: cardNumber.replace(/\s+/g,''), exp_month, exp_year, cvc: cardCvc, name: cardName } };
        const r = await fetch(API.payMock, { method:'POST', headers:{ 'Content-Type':'application/json', ...auth }, body: JSON.stringify(payload) });
        if(r.ok){ const jm = await r.json(); if(jm.ok){ showToast('Paiement simulÃ© acceptÃ©'); clearCart(); setTimeout(()=>location.href='/',800); return; } }
        showToast('Paiement Ã©chouÃ© (dÃ©mo)'); btn.disabled=false; btn.textContent='Payer'; return;
      }

      // Stripe
      const r = await fetch(API.stripeIntent, { method:'POST', headers:{ 'Content-Type':'application/json', ...auth }, body: JSON.stringify({ items, buyer }) });
      if(!r.ok){ showToast('Init paiement impossible'); btn.disabled=false; btn.textContent='Payer'; return; }
      const data = await r.json();
      const clientSecret = data.client_secret;
      if(!clientSecret){ showToast('client_secret manquant'); btn.disabled=false; btn.textContent='Payer'; return; }
      if(!stripe || !card) await initStripe();
      if(stripe && card){
        const result = await stripe.confirmCardPayment(clientSecret, { payment_method: { card, billing_details:{ name: buyer.name||undefined, email: buyer.email||undefined } } });
        if(result.error){ qs('#card-errors') && (qs('#card-errors').textContent = result.error.message || 'Erreur paiement'); showToast('Paiement Ã©chouÃ©'); btn.disabled=false; btn.textContent='Payer'; return; }
        if(result.paymentIntent?.status==='succeeded'){ showToast('Paiement rÃ©ussi'); clearCart(); setTimeout(()=>location.href='/',800); return; }
        showToast('Ãtat: '+(result.paymentIntent?.status||'inconnu')); btn.disabled=false; btn.textContent='Payer'; return;
      }
    }catch(_){ showToast('Erreur rÃ©seau'); btn.disabled=false; btn.textContent='Payer'; }
  });

  qsa('input[name=payment_method]').forEach(r=> r.addEventListener('change', updatePaymentUI));
  updatePaymentUI();
}

function renderCheckoutPage(){
  const root = qs('#checkout-page'); if(!root) return;
  const itemsContainer = qs('#checkout-items'); const totalEl = qs('#checkout-total');
  const cart = loadCart();
  if(!cart || cart.length === 0){
    if(itemsContainer) itemsContainer.innerHTML = '<div class="muted">Votre panier est vide.</div>';
    if(totalEl) totalEl.textContent = 'â¬0.00';
    return;
  }
  itemsContainer.innerHTML = '';
  cart.forEach(it => {
    const row = document.createElement('div');
    row.style.display='flex'; row.style.justifyContent='space-between'; row.style.marginBottom='8px';
    row.innerHTML = `<div>${escapeHtml(it.name)} x${it.qty}</div><div>â¬${(Number(it.price||0)*it.qty).toFixed(2)}</div>`;
    itemsContainer.appendChild(row);
  });
  if(totalEl) totalEl.textContent = 'â¬' + cart.reduce((s,i)=> s + (Number(i.price||0)* (Number(i.qty)||0)), 0).toFixed(2);
}

/* ---------- Pages simples ---------- */
function renderCartPage(){
  const container = qs('#cart-items'); if(!container) return;
  const cart = loadCart();
  container.innerHTML='';
  if(!cart.length){ container.innerHTML='<div style="padding:18px;color:#666">Votre panier est vide.</div>'; qs('#cart-total')&&(qs('#cart-total').textContent='â¬0.00'); return; }
  cart.forEach(it=>{
    const row = document.createElement('div');
    row.className='cart-row';
    row.style.cssText='display:flex;justify-content:space-between;align-items:center;padding:12px;border-bottom:1px solid #eee;';
    row.innerHTML = `
      <div style="flex:1 1 300px">
        <div style="font-weight:700">${escapeHtml(it.name)}</div>
        <div class="small muted">â¬${Number(it.price||0).toFixed(2)}</div>
      </div>
      <div style="display:flex;align-items:center;gap:8px">
        <button class="btn" data-decr="${it.id}">â</button>
        <div style="min-width:28px;text-align:center">${it.qty}</div>
        <button class="btn" data-incr="${it.id}">+</button>
        <button class="btn btn-ghost" data-remove="${it.id}">Supprimer</button>
      </div>`;
    container.appendChild(row);
  });
  qs('#cart-total')&&(qs('#cart-total').textContent='â¬'+cartTotal().toFixed(2));
  qsa('[data-incr]').forEach(b=> b.addEventListener('click', ()=>{ const id=+b.dataset.incr; const c=loadCart(); const it=c.find(x=>x.id===id); if(it){ it.qty++; saveCart(c); renderCartPage(); }}));
  qsa('[data-decr]').forEach(b=> b.addEventListener('click', ()=>{ const id=+b.dataset.decr; const c=loadCart(); const it=c.find(x=>x.id===id); if(it){ it.qty=Math.max(1,it.qty-1); saveCart(c); renderCartPage(); }}));
  qsa('[data-remove]').forEach(b=> b.addEventListener('click', ()=>{ const id=+b.dataset.remove; const c=loadCart().filter(x=>x.id!==id); saveCart(c); renderCartPage(); }));
}

/* ---------- Dashboard Vendeur ---------- */
function token(){ return localStorage.getItem('md_access_token') || ''; }
function authHeaders(json=true){ const h={ Authorization:'Bearer '+token() }; if(json) h['Content-Type']='application/json'; return h; }

async function guardVendorPage(){
  const t = token();
  if(!t){ showToast('Connecte-toi pour accÃ©der au dashboard vendeur'); setTimeout(()=>location.href='/login.html',600); return false; }
  try{
    const r = await fetch(API.meVendor, { headers:{ Authorization:'Bearer '+t } });
    if(!r.ok) throw 0;
    const j = await r.json();
    if(!j.is_vendor){ showToast('Ton compte nâest pas vendeur'); setTimeout(()=>location.href='/',800); return false; }
    return true;
  }catch(_){ showToast('Session invalide â reconnecte-toi'); setTimeout(()=>location.href='/login.html',600); return false; }
}

async function vendorLoadMe(){
  try{
    const r = await fetch(API.meVendor, { headers: authHeaders(false) });
    if(!r.ok) return null;
    const me = await r.json();
    const line = qs('#me_line'); const shop = qs('#shop_name'); const st = qs('#vendor_status');
    line && (line.textContent = `@${me.username} â ${me.shop_name || 'Sans boutique'}`);
    shop && (shop.value = me.shop_name || '');
    st && (st.value = me.is_vendor ? 'Vendeur activÃ©' : 'Non vendeur');
    return me;
  }catch(_){ return null; }
}

async function vendorFetchMine(){
  const r = await fetch(API.myProducts, { headers: authHeaders(false) });
  if(!r.ok) throw 0;
  const j = await r.json();
  return j.results || j || [];
}

function vendorRenderRows(rows){
  const tb = qs('#prod_tbody'); if(!tb) return;
  tb.innerHTML='';
  if(!rows.length){ tb.innerHTML='<tr><td colspan="8" class="muted">Aucun produit.</td></tr>'; return; }
    rows.forEach(p=>{
    const tr=document.createElement('tr');
    tr.innerHTML = `
      <td><img class="thumb" src="${p.image_url || '/static/images/placeholder_64.svg'}" alt=""></td>
      <td>${escapeHtml(p.name||'')}</td>
      <td>â¬${Number(p.price||0).toFixed(2)}</td>
      <td>${p.stock ?? 0}</td>
      <td>${escapeHtml(p.family||'')}</td>
      <td>${escapeHtml(p.concentration||'')}</td>
      <td>${(p.tags||[]).join(', ')}</td>
      <td class="row-actions">
        <button class="btn" data-ed="${p.id}">Ãditer</button>
        <button class="btn btn-danger" data-del="${p.id}">Suppr.</button>
      </td>`;
    tb.appendChild(tr);
  });
  qsa('[data-ed]').forEach(b=> b.addEventListener('click', ()=> vendorOpenEdit(+b.dataset.ed)));
  qsa('[data-del]').forEach(b=> b.addEventListener('click', ()=> vendorDel(+b.dataset.del)));
}

async function vendorReload(){
  try{ const rows = await vendorFetchMine(); vendorRenderRows(rows); }
  catch(_){ const tb=qs('#prod_tbody'); tb && (tb.innerHTML='<tr><td colspan="8" class="muted">Erreur de chargement.</td></tr>'); }
}

async function vendorCreate(){
  const payload = {
    name: qs('#new_name')?.value.trim(),
    price: parseFloat(qs('#new_price')?.value || '0'),
    stock: parseInt(qs('#new_stock')?.value || '0',10),
    family: qs('#new_family')?.value.trim(),
    concentration: qs('#new_concentration')?.value.trim(),
    image_url: qs('#new_image_url')?.value.trim(),
    description: qs('#new_description')?.value.trim(),
    tags: (qs('#new_tags')?.value || '').split(',').map(s=>s.trim()).filter(Boolean),
  };
  if(!payload.name){ showToast('Nom requis'); return; }

  const r = await fetch(API.createProduct, { method:'POST', headers: authHeaders(true), body: JSON.stringify(payload) });
  if(!r.ok){ console.warn(await r.text()); showToast('CrÃ©ation Ã©chouÃ©e'); return; }
  const created = await r.json();
  const id = created.id;

  const file = qs('#new_image_file')?.files?.[0];
  if(file){
    const fd = new FormData();
    fd.append('image', file);
    const up = await fetch(API.uploadImage(id), { method:'POST', headers:{ Authorization:'Bearer '+token() }, body: fd });
    if(!up.ok){ console.warn(await up.text()); showToast('Image non tÃ©lÃ©versÃ©e'); }
  }

  showToast('Produit crÃ©Ã©');
  ['new_name','new_price','new_stock','new_family','new_concentration','new_image_url','new_description','new_tags'].forEach(id=>{ const el=qs('#'+id); if(el) el.value=''; });
  const fi = qs('#new_image_file'); if(fi) fi.value='';
  vendorReload();
}

async function vendorOpenEdit(id){
  try{
    const r = await fetch(API.productDetail(id));
    if(!r.ok) throw 0;
    const p = await r.json();
    qs('#edit_id').value = p.id;
    qs('#edit_name').value = p.name || '';
    qs('#edit_price').value = p.price ?? '';
    qs('#edit_stock').value = p.stock ?? '';
    qs('#edit_image_url').value = p.image_url || '';
    qs('#edit_family').value = p.family || '';
    qs('#edit_concentration').value = p.concentration || '';
    qs('#edit_tags').value = (p.tags||[]).join(', ');
    qs('#edit_description').value = p.description || '';
    qs('#edit_modal').style.display='flex';
  }catch(_){ showToast('Ouverture Ã©dition Ã©chouÃ©e'); }
}

async function vendorSaveEdit(){
  const id = +qs('#edit_id').value;
  const payload = {
    name: qs('#edit_name')?.value.trim(),
    price: parseFloat(qs('#edit_price')?.value || '0'),
    stock: parseInt(qs('#edit_stock')?.value || '0',10),
    image_url: qs('#edit_image_url')?.value.trim(),
    family: qs('#edit_family')?.value.trim(),
    concentration: qs('#edit_concentration')?.value.trim(),
    tags: (qs('#edit_tags')?.value || '').split(',').map(s=>s.trim()).filter(Boolean),
    description: qs('#edit_description')?.value.trim(),
  };
  const r = await fetch(API.updateProduct(id), { method:'PATCH', headers: authHeaders(true), body: JSON.stringify(payload) });
  if(!r.ok){ console.warn(await r.text()); showToast('Sauvegarde Ã©chouÃ©e'); return; }

  const file = qs('#edit_image_file')?.files?.[0];
  if(file){
    const fd = new FormData();
    fd.append('image', file);
    const up = await fetch(API.uploadImage(id), { method:'POST', headers:{ Authorization:'Bearer '+token() }, body: fd });
    if(!up.ok){ console.warn(await up.text()); showToast('Image non tÃ©lÃ©versÃ©e'); }
  }

  qs('#edit_modal').style.display='none';
  showToast('Modifications enregistrÃ©es');
  vendorReload();
}

async function vendorDel(id){
  if(!confirm('Supprimer ce produit ?')) return;
  // Utiliser DELETE conformÃ©ment Ã  l'API REST cÃ´tÃ© backend
  const r = await fetch(API.deleteProduct(id), { method:'DELETE', headers: authHeaders(false) });
  if(!r.ok){ console.warn(await r.text()); showToast('Suppression Ã©chouÃ©e'); return; }
  showToast('Produit supprimÃ©');
  vendorReload();
}

/* ---------- Bootstrap global ---------- */
document.body.classList.add('page-enter');
document.addEventListener('DOMContentLoaded', ()=>{
  document.body.classList.remove('page-enter');
  document.body.classList.add('page-loaded');

  // Header/cart
  renderCartCount(); renderDrawerItems(); bindCartDrawer();

  // Auth
  bindLogin(); bindSignup(); updateAuthLink();
  // si une intention vendeur reste en session, tenter l'upgrade automatique
  upgradeToVendorIfPending(localStorage.getItem('md_access_token')||'').catch(()=>{});

  // Search bar (si prÃ©sente)
  const searchForm = qs('#product-search-form');
  const searchInput = qs('#product-search-input');
  if(searchForm && searchInput){
    searchForm.addEventListener('submit', (e)=>{
      e.preventDefault();
      const v = (searchInput.value||'').trim();
      if(!v) { location.href='/products.html'; return; }
      location.href = '/products.html?q=' + encodeURIComponent(v);
    });
    const q = getQueryParam('q'); if(q) searchInput.value = q;
  }

  // Pages
  if(qs('#products-grid')){
    const page = (location.pathname||'').split('/').pop();
    if(page==='' || page==='index.html') renderIndex();
    else { const q = getQueryParam('q'); renderProducts(q); }
  }
  if(qs('#product-detail')) renderProductPage();
  if(qs('#cart-page')) renderCartPage();
  if(qs('#pay-btn')) bindCheckout();
  if(qs('#checkout-page')) renderCheckoutPage();

  // Dashboard vendeur
  if(qs('#vendor-guard')){
    (async ()=>{
      if(!(await guardVendorPage())) return;
      qs('#btn_reload')?.addEventListener('click', vendorReload);
      qs('#btn_create')?.addEventListener('click', vendorCreate);
      qs('#refresh-me')?.addEventListener('click', vendorLoadMe);
      qs('#edit_close')?.addEventListener('click', ()=> qs('#edit_modal').style.display='none');
      qs('#edit_save')?.addEventListener('click', vendorSaveEdit);
      await vendorLoadMe();
      await vendorReload();
    })();
  }
});

