// Small frontend JS: fetch products, cart (localStorage), login form, checkout (demo)
const BACKEND_URL = window.BACKEND_URL || 'http://127.0.0.1:8000';
const CART_KEY = 'md_cart_v1';

function qs(s){ return document.querySelector(s) }
function qsa(s){ return Array.from(document.querySelectorAll(s)) }

// small helper: read a query param
function getQueryParam(name){ try{ const params = new URLSearchParams(window.location.search); return params.get(name) }catch(e){return null} }

function loadCart(){ try{ return JSON.parse(localStorage.getItem(CART_KEY)||'[]') }catch(e){return []} }
function saveCart(c){ localStorage.setItem(CART_KEY, JSON.stringify(c)); renderCartCount(); renderDrawerItems(); }
// Small toast helper for user feedback
function showToast(msg, timeout=2500){
  let el = qs('#md-toast');
  if(!el){ el = document.createElement('div'); el.id='md-toast'; el.style.position='fixed'; el.style.right='18px'; el.style.bottom='18px'; el.style.background='#0f172a'; el.style.color='#fff'; el.style.padding='12px 16px'; el.style.borderRadius='8px'; el.style.boxShadow='0 8px 24px rgba(2,6,23,0.4)'; el.style.zIndex=9999; el.style.fontSize='14px'; document.body.appendChild(el); }
  el.textContent = msg;
  el.style.opacity = '1';
  el.style.transform = 'translateY(0)';
  clearTimeout(el._hideTimer);
  el._hideTimer = setTimeout(()=>{ el.style.opacity='0'; el.style.transform='translateY(8px)'; }, timeout);
}
function addToCart(product, qty=1){ const cart=loadCart(); const idx=cart.findIndex(i=>i.id===product.id); if(idx>=0) cart[idx].qty+=qty; else cart.push({id:product.id,name:product.name,price:product.price,qty}); saveCart(cart); showToast(`${product.name} ajouté au panier`); }
function clearCart(){ saveCart([]); }
function cartTotal(){ return loadCart().reduce((s,i)=>s+i.price*i.qty,0) }

function renderCartCount(){ const n = loadCart().reduce((s,i)=>s+i.qty,0); const el=qs('#cart-count'); if(el) el.textContent=n }
function renderDrawerItems(){ const root=qs('#drawer-items'); if(!root) return; const cart=loadCart(); root.innerHTML=''; if(cart.length===0){ root.innerHTML='<div style="padding:18px;color:#666">Votre panier est vide.</div>'; qs('#drawer-total').textContent='€0.00'; return } cart.forEach(it=>{ const row=document.createElement('div'); row.style.display='flex'; row.style.justifyContent='space-between'; row.style.padding='8px 12px'; row.innerHTML=`<div>${escapeHtml(it.name)} x${it.qty}</div><div>€${(it.price*it.qty).toFixed(2)}</div>`; root.appendChild(row) }); qs('#drawer-total').textContent='€'+cartTotal().toFixed(2) }

function escapeHtml(s){ return (s+'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;' ,"'":"&#39;"}[c]||c)) }

async function fetchProducts(){ try{ const res=await fetch(BACKEND_URL+'/api/products/'); if(!res.ok) throw new Error('fetch failed'); return await res.json() }catch(e){console.error(e); return []} }

async function renderIndex(){
  const list = await fetchProducts();
  const grid = qs('#products-grid');
  if(!grid) return;
  grid.innerHTML = '';
  list.slice(0,9).forEach((p, idx) => {
    const card = document.createElement('div');
    card.className = 'card fade-in';
    card.style.animationDelay = (idx * 80) + 'ms';
    card.innerHTML = `
      <img src="${p.image_url || 'https://images.unsplash.com/photo-1519741490371-66a3fb4f3f4b?q=80&w=1200&auto=format&fit=crop'}"/>
      <div class="body">
        <div class="title">${escapeHtml(p.name)}</div>
        <div class="meta">${escapeHtml(p.family || '')}</div>
        <div class="row">
          <div class="price">€${p.price}</div>
          <div>
            <a class="btn" href="/product.html?id=${p.id}">Voir</a>
            <button class="btn btn-primary" data-add="${p.id}">Ajouter</button>
          </div>
        </div>
      </div>
    `;
    grid.appendChild(card);
  });

  // bind add buttons after DOM insertion
  qsa('[data-add]').forEach(b => b.addEventListener('click', async () => {
    const id = b.dataset.add;
    const list = await fetchProducts();
    const p = list.find(x => x.id == id);
    if(p) addToCart(p, 1);
  }));
}

async function renderProducts(q){
  const list = await fetchProducts();
  const grid = qs('#products-grid');
  if(!grid) return;
  grid.innerHTML = '';
  const filter = (q||'').toLowerCase().trim();
  const items = filter ? list.filter(p=> (p.name||'').toLowerCase().includes(filter) || (p.short_description||'').toLowerCase().includes(filter) || (p.long_description||'').toLowerCase().includes(filter) || (p.family||'').toLowerCase().includes(filter)) : list;
  items.forEach((p, idx) => {
    const card = document.createElement('div');
    card.className = 'card fade-in';
    card.style.animationDelay = (idx * 40) + 'ms';
    card.innerHTML = `
      <img src="${p.image_url || 'https://images.unsplash.com/photo-1519741490371-66a3fb4f3f4b?q=80&w=1200&auto=format&fit=crop'}"/>
      <div class="body">
        <div class="title">${escapeHtml(p.name)}</div>
        <div class="meta">${escapeHtml(p.family || '')}</div>
        <div class="row">
          <div class="price">€${p.price}</div>
          <div>
            <a class="btn" href="/product.html?id=${p.id}">Voir</a>
            <button class="btn btn-primary" data-add="${p.id}">Ajouter</button>
          </div>
        </div>
      </div>
    `;
    grid.appendChild(card);
  });
  // bind add buttons after DOM insertion
  qsa('[data-add]').forEach(b => b.addEventListener('click', async () => {
    const id = b.dataset.add;
    const list = await fetchProducts();
    const p = list.find(x => x.id == id);
    if(p) addToCart(p, 1);
  }));
}

async function renderProductPage(){
  const params = new URLSearchParams(location.search);
  const id = params.get('id');
  if(!id) return;
  const resp = await fetch(BACKEND_URL+`/api/products/${id}/`);
  if(!resp.ok) return;
  const p = await resp.json();
  qs('#p-name').textContent = p.name;
  qs('#p-price').textContent = '€' + p.price;
  qs('#p-desc').textContent = p.long_description || p.short_description || '';
  qs('#p-img').src = p.image_url || 'https://via.placeholder.com/900x600';
  const familyEl = qs('#p-family'); if(familyEl) familyEl.textContent = p.family || '';
  qs('#add-single').addEventListener('click', ()=>addToCart(p,1));

  // similar products (staggered animation)
  let similar = [];
  try{
    const sres = await fetch(BACKEND_URL+`/api/recommender/products/${id}/?k=3`);
    if(sres.ok){ const sjson = await sres.json(); similar = sjson.similar || []; }
  }catch(e){ /* ignore */ }

  const simcont = qs('#similar-list');
  simcont.innerHTML = '';
  similar.forEach((s, i) => {
    const el = document.createElement('div');
    el.className = 'card fade-in';
    el.style.animationDelay = (i * 80) + 'ms';
    el.innerHTML = `
      <img src="${s.image_url || 'https://via.placeholder.com/300'}"/>
      <div class="body">
        <div class="title">${escapeHtml(s.name)}</div>
        <div class="meta">€${s.price}</div>
        <div style="margin-top:8px"><a class="btn" href="/product.html?id=${s.id}">Voir</a></div>
      </div>
    `;
    simcont.appendChild(el);
  });
}

function renderCartPage(){
  const container = qs('#cart-items');
  if(!container) return;
  const cart = loadCart();
  container.innerHTML = '';
  if(cart.length===0){ container.innerHTML = '<div style="padding:18px;color:#666">Votre panier est vide.</div>'; qs('#cart-total').textContent='€0.00'; return }

  cart.forEach((it, idx)=>{
    const row = document.createElement('div');
    row.className = 'cart-row';
    row.style.display='flex'; row.style.justifyContent='space-between'; row.style.alignItems='center'; row.style.padding='12px'; row.style.borderBottom='1px solid #eee';
    row.innerHTML = `
      <div style="flex:1 1 300px">
        <div style="font-weight:700">${escapeHtml(it.name)}</div>
        <div class="small muted">€${it.price.toFixed(2)}</div>
      </div>
      <div style="display:flex;align-items:center;gap:8px">
        <button class="btn" data-decr="${it.id}">−</button>
        <div style="min-width:28px;text-align:center">${it.qty}</div>
        <button class="btn" data-incr="${it.id}">+</button>
        <button class="btn btn-ghost" data-remove="${it.id}">Supprimer</button>
      </div>
    `;
    container.appendChild(row);
  });

  qs('#cart-total').textContent = '€' + cartTotal().toFixed(2);

  // bind buttons
  qsa('[data-incr]').forEach(b => b.addEventListener('click', ()=>{ const id=b.dataset.incr; const c=loadCart(); const i=c.find(x=>x.id==id); if(i){ i.qty+=1; saveCart(c); renderCartPage(); }}));
  qsa('[data-decr]').forEach(b => b.addEventListener('click', ()=>{ const id=b.dataset.decr; const c=loadCart(); const i=c.find(x=>x.id==id); if(i){ i.qty = Math.max(1, i.qty-1); saveCart(c); renderCartPage(); }}));
  qsa('[data-remove]').forEach(b => b.addEventListener('click', ()=>{ const id=b.dataset.remove; const c=loadCart().filter(x=>x.id!=id); saveCart(c); renderCartPage(); }));
}

function bindCartDrawer(){
  const open = qs('#open-cart');
  const close = qs('#close-drawer');
  const drawer = qs('#cart-drawer');
  if(open) open.addEventListener('click', ()=>{
    // If user is already on the cart page or on checkout, open the drawer; otherwise navigate to the cart page
    const p = (location.pathname || '').split('/').pop();
    if(p === 'cart.html' || p === 'checkout.html'){
      if(drawer) drawer.classList.add('open');
    }else{
      window.location.href = '/cart.html';
    }
  });
  if(close) close.addEventListener('click', ()=>{ if(drawer) drawer.classList.remove('open') });
}


// Updated bindLogin: after successful login update the header auth link
function bindLogin(){
  const f=qs('#login-form'); if(!f) return;
  f.addEventListener('submit', async e=>{
    e.preventDefault();
    const email=f.querySelector('input[name=email]').value;
    const password=f.querySelector('input[name=password]').value;
    try{
      const res=await fetch(BACKEND_URL+'/api/auth/token/', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({email,password})});
      if(!res.ok){ alert('Échec connexion'); return }
      const data=await res.json();
      localStorage.setItem('md_access_token', data.access);
      localStorage.setItem('md_refresh_token', data.refresh);
      // update header UI to reflect logged in state
      updateAuthLink();
      alert('Connecté');
      window.location.href='/';
    }catch(err){ console.error(err); alert('Erreur') }
  })
}

function bindCheckout(){
  const btn = qs('#pay-btn'); if(!btn) return;
  // Only initialize Stripe on checkout page when card element exists
  let stripe = null; let card = null;
  async function initStripe(){
    try{
      const res = await fetch(BACKEND_URL + '/api/orders/stripe/config/');
      if(!res.ok) throw new Error('no stripe config');
      const cfg = await res.json();
      if(!cfg.publishableKey) throw new Error('no publishable key');
      stripe = Stripe(cfg.publishableKey);
      const elements = stripe.elements();
      card = elements.create('card', {hidePostalCode:true, style:{base:{fontSize:'16px',color:'#111',fontFamily:'system-ui,Segoe UI,Roboto'}}});
      const mount = qs('#card-element'); if(mount) card.mount(mount);
      if(card) card.on('change', e=>{ const ce = qs('#card-errors'); if(ce) ce.textContent = e.error ? e.error.message : '' });
    }catch(e){ console.warn('Stripe init failed', e); }
  }

  // Update payment UI depending on selected method
  function updatePaymentUI(){
    const sel = (document.querySelector('input[name=payment_method]:checked')||{value:'card'}).value;
    const elCard = qs('#card-element');
    const elManual = qs('#card-manual');
    if(sel === 'card'){
      if(elCard) elCard.style.display = '';
      if(elManual) elManual.style.display = 'none';
      // initialize stripe if not already
      if(!stripe) initStripe();
    }else if(sel === 'mock'){
      if(elCard) elCard.style.display = 'none';
      if(elManual) elManual.style.display = '';
    }else{
      // cinetpay or others: hide card inputs
      if(elCard) elCard.style.display = 'none';
      if(elManual) elManual.style.display = 'none';
    }
  }

  btn.addEventListener('click', async ()=>{
    btn.disabled = true;
    btn.textContent = 'Traitement...';
    try{
      const items = loadCart();
      if(items.length===0){ showToast('Le panier est vide'); btn.disabled=false; btn.textContent='Payer'; return }
      const buyer = { name: (qs('#buyer-name')? qs('#buyer-name').value : ''), email: (qs('#buyer-email')? qs('#buyer-email').value : '') };
      // Decide payment method (card / cinetpay / mock)
      const selected = (document.querySelector('input[name=payment_method]:checked') || {value:'card'}).value;

      if(selected === 'cinetpay'){
        // create a CinetPay transaction on the backend and redirect the user
        try{
          const cres = await fetch(BACKEND_URL + '/api/orders/cinetpay/create/', {
            method: 'POST',
            headers: {'Content-Type':'application/json','Authorization': (localStorage.getItem('md_access_token')? 'Bearer '+localStorage.getItem('md_access_token') : '')},
            body: JSON.stringify({ items, buyer })
          });
          if(!cres.ok){ const t = await cres.text(); console.warn('cinetpay create failed', t); showToast('Impossible d\'initier le paiement CinetPay'); btn.disabled=false; btn.textContent='Payer'; return }
          const cj = await cres.json();
          if(cj && cj.payment_url){ window.location.href = cj.payment_url; return }
          showToast('Erreur réponse CinetPay'); btn.disabled=false; btn.textContent='Payer'; return;
        }catch(e){ console.error(e); showToast('Erreur réseau'); btn.disabled=false; btn.textContent='Payer'; return }
      }

      // If selected is mock, use the mock payment endpoint (manual fake card)
      if(selected === 'mock'){
        const cardNumber = qs('#manual-card-number') ? qs('#manual-card-number').value.trim() : '';
        const cardExp = qs('#manual-card-exp') ? qs('#manual-card-exp').value.trim() : '';
        const cardCvc = qs('#manual-card-cvc') ? qs('#manual-card-cvc').value.trim() : '';
        const cardName = qs('#manual-card-name') ? qs('#manual-card-name').value.trim() : '';
        if(!cardNumber || !cardExp || !cardCvc){ showToast('Veuillez renseigner les informations de carte'); btn.disabled=false; btn.textContent='Payer'; return }
        let exp_month = null, exp_year = null; const m = cardExp.match(/^(\d{1,2})\s*(?:\/?|-)\s*(\d{2,4})$/); if(m){ exp_month = parseInt(m[1],10); exp_year = parseInt(m[2],10); if(exp_year<100) exp_year += 2000; }
        const mockPayload = { method: 'card', card: { number: cardNumber.replace(/\s+/g,''), exp_month, exp_year, cvc: cardCvc, name: cardName } };
        try{
          const mockRes = await fetch(BACKEND_URL + '/api/orders/pay/mock/', { method: 'POST', headers: {'Content-Type':'application/json','Authorization': (localStorage.getItem('md_access_token')? 'Bearer '+localStorage.getItem('md_access_token') : '')}, body: JSON.stringify(mockPayload) });
          if(mockRes.ok){ const jm = await mockRes.json(); if(jm.ok){ showToast('Paiement simulé accepté'); clearCart(); setTimeout(()=> window.location.href='/',800); return } }
          const txt = await mockRes.text(); console.warn('mock pay failed', txt); showToast('Paiement échoué (mode démo)'); btn.disabled=false; btn.textContent='Payer'; return;
        }catch(e){ console.error(e); showToast('Erreur réseau'); btn.disabled=false; btn.textContent='Payer'; return }
      }

      // Default: card via Stripe
      // Create PaymentIntent on backend
      const res = await fetch(BACKEND_URL + '/api/orders/stripe/create-payment-intent/', {
        method: 'POST',
        headers: {
          'Content-Type':'application/json',
          'Authorization': (localStorage.getItem('md_access_token')? 'Bearer '+localStorage.getItem('md_access_token') : '')
        },
        body: JSON.stringify({ items, buyer })
      });

      if(!res.ok){
        const txt = await res.text(); console.warn('create intent failed', txt);
        showToast('Impossible d\'initier le paiement. Connectez-vous et réessayez.');
        btn.disabled=false; btn.textContent='Payer';
        return;
      }

      const data = await res.json();
      const clientSecret = data.client_secret;
      if(!clientSecret){ showToast('Erreur: client_secret manquant'); btn.disabled=false; btn.textContent='Payer'; return }

      // Ensure stripe/card are initialized
      if(!stripe || !card) await initStripe();

      if(stripe && card){
        const result = await stripe.confirmCardPayment(clientSecret, {
          payment_method: {
            card: card,
            billing_details: { name: buyer.name || undefined, email: buyer.email || undefined }
          }
        });

        if(result.error){
          const ce = qs('#card-errors'); if(ce) ce.textContent = result.error.message || 'Erreur de paiement';
          showToast('Paiement échoué');
          btn.disabled=false; btn.textContent='Payer';
          return;
        }

        if(result.paymentIntent && result.paymentIntent.status === 'succeeded'){
          showToast('Paiement réussi — merci !');
          clearCart();
          setTimeout(()=> window.location.href='/', 800);
          return;
        }

        showToast('Paiement traité — état: ' + (result.paymentIntent? result.paymentIntent.status : 'unknown'));
        btn.disabled=false; btn.textContent='Payer';
        return;
      }

    }catch(e){ console.error(e); showToast('Erreur réseau'); btn.disabled=false; btn.textContent='Payer'; }
  });

  // Wire payment method radios to update UI
  qsa('input[name=payment_method]').forEach(r => r.addEventListener('change', updatePaymentUI));
  // initial UI update
  updatePaymentUI();
}

// init
function bindSignup(){
  const f = qs('#signup-form');
  if(!f) return;
  f.addEventListener('submit', async e=>{
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
      const res = await fetch(BACKEND_URL + '/api/auth/register/', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify(data)
      });
      if(res.ok){
        // Auto-activate flow: try to login immediately (dev convenience)
        showToast('Compte créé — connexion en cours...');
        try{
          const loginRes = await fetch(BACKEND_URL + '/api/auth/token/', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ email: data.email, password: data.password }) });
          if(loginRes.ok){
            const d = await loginRes.json();
            localStorage.setItem('md_access_token', d.access);
            localStorage.setItem('md_refresh_token', d.refresh);
            showToast('Connecté');
            updateAuthLink();
            setTimeout(()=> window.location.href = '/profile.html', 600);
            return;
          }
        }catch(e){ /* fallthrough to fallback message */ }

        // Fallback message (in case automatic login fails)
        try{ sessionStorage.setItem('signup_pending', JSON.stringify({ email: data.email, password: data.password })); }catch(e){}
        if(feedback) feedback.innerHTML = `Compte créé. Si la connexion automatique échoue, utilisez la page de connexion : <a href="/login.html">Se connecter</a>`;
        return;
      }
      const j = await res.json().catch(()=>null);
      const msg = j && j.detail ? j.detail : (j && typeof j === 'object' ? JSON.stringify(j) : 'Erreur création');
      if(feedback) feedback.textContent = msg;
      showToast(msg || 'Erreur');
    }catch(err){ console.error(err); showToast('Erreur réseau'); if(feedback) feedback.textContent='Erreur réseau'; }
  });
}

// Update or replace the "Se connecter" link in the header depending on auth state
async function updateAuthLink(){
  try{
    const token = localStorage.getItem('md_access_token');
    const nav = document.querySelector('header nav');
    if(!nav) return;
    // find the first link that points to /login.html in the nav
    const navLinks = Array.from(nav.querySelectorAll('a'));
    const loginLink = navLinks.find(a => a.getAttribute('href') === '/login.html');
    if(!loginLink) return;

    // remove any existing account link to avoid duplicates
    const existingAcct = nav.querySelector('a[data-account-link]');
    if(existingAcct) existingAcct.remove();

    if(!token){
      // not logged in — restore "Se connecter"
      const newLink = loginLink.cloneNode(true);
      newLink.textContent = 'Se connecter';
      newLink.setAttribute('href', '/login.html');
      newLink.removeAttribute('data-account-link');
      loginLink.parentNode.replaceChild(newLink, loginLink);
      return;
    }

  // Verify token by calling profile endpoint
  let username = null;
  let profileData = null;
    try{
      const pres = await fetch(BACKEND_URL + '/api/auth/profile/', { headers: { 'Authorization': 'Bearer ' + token } });
      if(!pres.ok){ throw new Error('invalid token') }
      const pj = await pres.json();
      profileData = pj;
      username = pj.username || pj.email || null;
    }catch(err){
      // invalid token — clear and restore link
      localStorage.removeItem('md_access_token');
      localStorage.removeItem('md_refresh_token');
      const newLink2 = loginLink.cloneNode(true);
      newLink2.textContent = 'Se connecter';
      newLink2.setAttribute('href', '/login.html');
      loginLink.parentNode.replaceChild(newLink2, loginLink);
      return;
    }

  // replace login link with logout (no username displayed in header)
  const logoutText = 'Se déconnecter';
    const logoutLink = loginLink.cloneNode(true);
    logoutLink.textContent = logoutText;
    logoutLink.setAttribute('href', '#');
    // add a data attribute so we can detect account link separately
    logoutLink.setAttribute('data-account-link', 'true');
    // attach handler
    logoutLink.addEventListener('click', (ev)=>{
      ev.preventDefault();
      localStorage.removeItem('md_access_token');
      localStorage.removeItem('md_refresh_token');
      showToast('Déconnecté');
      setTimeout(()=> window.location.href = '/', 400);
    });
    loginLink.parentNode.replaceChild(logoutLink, loginLink);

    // add a "Profil" link after logoutLink
    const accountLink = document.createElement('a');
  accountLink.href = '/profile.html'; // link to profile page
  accountLink.textContent = 'Profil';
    accountLink.setAttribute('data-account-link', 'true');
    accountLink.style.marginLeft = '8px';
    logoutLink.parentNode.insertBefore(accountLink, logoutLink.nextSibling);

    // add a "Personnaliser" link for logged-in users (quick access to the IA chat)
    try{
      // don't show the personalize link when viewing the Django admin pages
      if(!window.location.pathname.startsWith('/admin')){
        const personalizeLink = document.createElement('a');
        personalizeLink.href = '/personalize.html';
        personalizeLink.textContent = 'Personnaliser';
        personalizeLink.setAttribute('data-account-link', 'true');
        personalizeLink.style.marginLeft = '8px';
        logoutLink.parentNode.insertBefore(personalizeLink, accountLink);
      }
    }catch(e){/* ignore */}

  // If profile indicates superuser, add an Admin link
    try{
      if(profileData && profileData.is_superuser){
        const adminLink = document.createElement('a');
        adminLink.href = '/admin/';
        adminLink.textContent = 'Admin';
        adminLink.setAttribute('data-account-link', 'true');
        adminLink.style.marginLeft = '8px';
        logoutLink.parentNode.insertBefore(adminLink, accountLink.nextSibling);
        // add an impersonate button for superusers
        const impBtn = document.createElement('a');
        impBtn.href = '#';
        impBtn.textContent = 'Impersoner';
        impBtn.setAttribute('data-account-link', 'true');
        impBtn.style.marginLeft = '8px';
        impBtn.addEventListener('click', (ev)=>{ ev.preventDefault(); impersonatePrompt(); });
        logoutLink.parentNode.insertBefore(impBtn, adminLink.nextSibling);
      }
    }catch(e){/* ignore */}

    // If an impersonation session was started (admin stored original tokens), show a banner
    try{
      if(sessionStorage.getItem('impersonation_original')){
        renderImpersonationBanner(profileData && (profileData.username || profileData.email));
      }
    }catch(e){/* ignore */}

  }catch(e){ console.warn('updateAuthLink failed', e) }
}

// Prompt the admin for an email/username and request impersonation
function impersonatePrompt(){
  const id = prompt('Entrez l\'email ou le username de l\'utilisateur à impersoner :');
  if(!id) return; impersonateUser(id);
}

async function impersonateUser(identifier){
  const token = localStorage.getItem('md_access_token');
  if(!token){ showToast('Vous devez être connecté en tant qu\'admin pour impersoner'); return }
  try{
    const res = await fetch(BACKEND_URL + '/api/auth/impersonate/', { method: 'POST', headers: {'Content-Type':'application/json', 'Authorization': 'Bearer ' + token}, body: JSON.stringify({ email: identifier, username: identifier }) });
    if(!res.ok){ const txt = await res.text().catch(()=>null); showToast('Impersonation échouée: '+(txt||res.status)); return }
    const j = await res.json();
    // save original tokens so admin can restore later
    try{ const orig = { access: localStorage.getItem('md_access_token'), refresh: localStorage.getItem('md_refresh_token'), admin_username: (window._md && window._md.profile && window._md.profile.username) || null }; sessionStorage.setItem('impersonation_original', JSON.stringify(orig)); }catch(e){}
    // replace tokens with impersonated user tokens
    if(j.access) localStorage.setItem('md_access_token', j.access);
    if(j.refresh) localStorage.setItem('md_refresh_token', j.refresh);
    showToast('Impersonation activée — vous êtes maintenant connecté en tant que ' + (j.user && (j.user.username || j.user.email)));
    updateAuthLink();
    renderImpersonationBanner(j.user && (j.user.username || j.user.email));
  }catch(err){ console.error(err); showToast('Erreur réseau'); }
}

function renderImpersonationBanner(who){
  // remove existing banner
  const existing = qs('#impersonation-banner'); if(existing) existing.remove();
  const b = document.createElement('div'); b.id = 'impersonation-banner'; b.style.position='fixed'; b.style.left='0'; b.style.right='0'; b.style.top='0'; b.style.background='#ffefc2'; b.style.color='#111'; b.style.padding='8px 12px'; b.style.textAlign='center'; b.style.zIndex=99999; b.style.boxShadow='0 4px 8px rgba(0,0,0,0.06)';
  b.innerHTML = `Vous impersonnez: <strong>${escapeHtml(who||'utilisateur')}</strong> — <a id="stop-impersonation" href="#">Arrêter</a>`;
  document.body.appendChild(b);
  qs('#stop-impersonation').addEventListener('click', (ev)=>{ ev.preventDefault(); stopImpersonation(); });
}

function stopImpersonation(){
  const raw = sessionStorage.getItem('impersonation_original');
  if(!raw){ showToast('Aucune session admin sauvegardée'); return }
  try{
    const orig = JSON.parse(raw);
    if(orig.access) localStorage.setItem('md_access_token', orig.access);
    if(orig.refresh) localStorage.setItem('md_refresh_token', orig.refresh);
    sessionStorage.removeItem('impersonation_original');
    showToast('Impersonation arrêtée — retour au compte admin');
    // remove banner
    const b = qs('#impersonation-banner'); if(b) b.remove();
    updateAuthLink();
  }catch(e){ console.error(e); showToast('Impossible de restaurer la session admin'); }
}

// Page transition: mark entering state then flip to loaded on DOMContentLoaded
document.body.classList.add('page-enter');
document.addEventListener('DOMContentLoaded', ()=>{
  // fade in
  document.body.classList.remove('page-enter');
  document.body.classList.add('page-loaded');

  renderCartCount(); renderDrawerItems(); bindCartDrawer(); bindLogin(); bindSignup(); bindCheckout();

  // Update auth link in header: show 'Se déconnecter' when logged in
  updateAuthLink();

  // search form handling: submit redirects to products page with q param
  const searchForm = qs('#product-search-form');
  const searchInput = qs('#product-search-input');
  if(searchForm && searchInput){
    searchForm.addEventListener('submit', e=>{ e.preventDefault(); const v = (searchInput.value||'').trim(); if(!v) { window.location.href = '/products.html'; return } window.location.href = '/products.html?q=' + encodeURIComponent(v); });
    // if we're on products page and there's a q param, set input value
    const q = getQueryParam('q'); if(q && searchInput) searchInput.value = q;
  }

  // Render pages: decide between index or products list
  if(qs('#products-grid')){
    const path = (location.pathname||'').split('/').pop();
    if(path === '' || path === 'index.html'){
      renderIndex();
    }else{
      const q = getQueryParam('q'); if(q) renderProducts(q); else renderProducts();
    }
  }
  if(qs('#product-detail')) renderProductPage();
  if(qs('#cart-page')) renderCartPage();
  if(qs('#personalize-root')) renderPersonalizePage();
})

// Personalization page: chat UI for authenticated users
async function renderPersonalizePage(){
  const token = localStorage.getItem('md_access_token');
  const root = qs('#personalize-root');
  if(!root){ return }
  // Require authentication
  if(!token){
    showToast('Connecte-toi pour utiliser le personnaliseur');
    setTimeout(()=> window.location.href = '/login.html', 900);
    return;
  }

  const msgsEl = qs('#messages');
  const input = qs('#personalize-input');
  const sendBtn = qs('#personalize-send');
  const finalizeBtn = qs('#personalize-finalize');
  const recipeEl = qs('#suggested-recipe');

  // example buttons: fill input or fill+send
  const exampleUseBtn = qs('#personalize-example-use');
  const exampleSendBtn = qs('#personalize-example-send');
  const exampleText = "Compose‑moi une formule avec vanille en tête, jasmin au coeur, ambre en base; intensité moyenne; budget 50€.";
  if(exampleUseBtn){ exampleUseBtn.addEventListener('click', ()=>{ input.value = exampleText; input.focus(); }); }
  if(exampleSendBtn){ exampleSendBtn.addEventListener('click', ()=>{ input.value = exampleText; sendMessage(exampleText); }); }

  let conversationId = null;

  function appendMsg(role, text){
    const d = document.createElement('div'); d.className = 'msg ' + role; d.innerHTML = `<div>${escapeHtml(text)}</div>`;
    msgsEl.appendChild(d); msgsEl.scrollTop = msgsEl.scrollHeight;
  }

  // create conversation for this user
  try{
    const res = await fetch(BACKEND_URL + '/api/conversations/create/', { method: 'POST', headers: {'Authorization': 'Bearer ' + token} });
    if(!res.ok){ if(res.status===401){ showToast('Session expirée, reconnecte-toi'); setTimeout(()=> window.location.href='/login.html',800); return } throw new Error('create conv failed') }
    const conv = await res.json();
    conversationId = conv.id;
  }catch(e){ console.error(e); showToast('Impossible de démarrer une conversation'); return }

  // initial assistant greeting
  appendMsg('assistant', "Bonjour — dites-moi vos goûts, je vous proposerai une formule personnalisée.");

  async function sendMessage(text){
    if(!text || !conversationId) return;
    // append user message locally
    appendMsg('user', text);
    input.value = '';
    try{
      const payload = { role: 'user', text: text };
      const res = await fetch(BACKEND_URL + `/api/conversations/${conversationId}/messages/`, {
        method: 'POST', headers: {'Content-Type':'application/json', 'Authorization': 'Bearer ' + token}, body: JSON.stringify(payload)
      });
      if(!res.ok){ if(res.status===401){ showToast('Session expirée'); setTimeout(()=> window.location.href='/login.html',800); return } const txt = await res.text(); console.warn('msg send failed', txt); showToast('Erreur envoi'); return }
      const j = await res.json();
      if(j.assistant){ appendMsg('assistant', j.assistant.text); }
      if(j.suggested_recipe){ recipeEl.style.display='block'; recipeEl.innerHTML = '<strong>Proposition :</strong><pre>' + escapeHtml(JSON.stringify(j.suggested_recipe, null, 2)) + '</pre>'; }
    }catch(err){ console.error(err); showToast('Erreur réseau'); }
  }

  sendBtn.addEventListener('click', ()=>{ const t = (input.value||'').trim(); if(t) sendMessage(t); });
  input.addEventListener('keypress', e=>{ if(e.key === 'Enter'){ e.preventDefault(); const t=(input.value||'').trim(); if(t) sendMessage(t); } });

  finalizeBtn.addEventListener('click', async ()=>{
    if(!conversationId) return; try{ const res = await fetch(BACKEND_URL + `/api/conversations/${conversationId}/finalize/`, { method:'POST', headers:{ 'Authorization': 'Bearer ' + token } }); if(res.ok){ showToast('Conversation finalisée — un email vous sera envoyé pour confirmation'); finalizeBtn.disabled=true } else { if(res.status===401){ showToast('Session expirée'); setTimeout(()=> window.location.href='/login.html',800); return } const t=await res.text(); console.warn('finalize failed', t); showToast('Erreur finalisation') } }catch(err){ console.error(err); showToast('Erreur réseau') } });
}

// export for debugging
window._md = { loadCart, saveCart, addToCart, clearCart }
