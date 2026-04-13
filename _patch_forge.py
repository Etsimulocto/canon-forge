# ============================================================
# PATCH: wire Canon Forge paywall to PayPal $4.99
# Run from /c/Users/quart/canon-forge in Git Bash
# ============================================================

f = open('public/index.html', 'r', encoding='utf-8')
s = f.read()
f.close()

# Fix 1: replace goToCheckout stub with real PayPal call
old = '''function goToCheckout() {
  // TODO: wire Lemon Squeezy checkout URL when product is created
  alert('Checkout coming soon — Lemon Squeezy verification in progress.');
}'''
new = '''async function goToCheckout() {
  if (!currentUser) { closePaywall(); openAuth(); return; }
  try {
    const token = currentSession?.access_token;
    const r = await fetch(RAIL + '/create-order', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
      body: JSON.stringify({ amount: '499' })
    });
    const data = await r.json();
    if (!r.ok) { alert(data.detail || 'Payment error.'); return; }
    window.location.href = data.approve_url;
  } catch(e) { alert('Payment error. Try again.'); }
}'''
assert s.count(old) == 1, 'anchor 1 not found: ' + repr(old[:40])
s = s.replace(old, new, 1)

# Fix 2: handle PayPal return on forge.spiralside.com
# Add handlePayPalReturn call after updateUsesUI() at bottom of script
old2 = '''// Init anon uses on load
usesRemaining = Math.max(0, FREE_LIMIT - getAnonUses());
updateUsesUI();'''
new2 = '''// Init anon uses on load
usesRemaining = Math.max(0, FREE_LIMIT - getAnonUses());
updateUsesUI();

// Handle PayPal return
(async function handlePayPalReturn() {
  const params = new URLSearchParams(window.location.search);
  const payment = params.get('payment');
  const token = params.get('token');
  if (payment === 'success' && token) {
    try {
      // wait for auth to settle
      await new Promise(r => setTimeout(r, 800));
      const { data } = await sb.auth.getSession();
      const authToken = data?.session?.access_token;
      if (!authToken) return;
      const r = await fetch(RAIL + '/capture-order', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + authToken },
        body: JSON.stringify({ order_id: token })
      });
      const result = await r.json();
      if (r.ok) {
        isPaid = true;
        updateUsesUI();
        window.history.replaceState({}, document.title, window.location.pathname);
        setTimeout(() => alert('Payment successful! Canon Forge is now unlocked.'), 300);
      }
    } catch(e) {}
  } else if (payment === 'cancelled') {
    window.history.replaceState({}, document.title, window.location.pathname);
  }
})();'''
assert s.count(old2) == 1, 'anchor 2 not found: ' + repr(old2[:40])
s = s.replace(old2, new2, 1)

# Fix 3: update paywall price display to $4.99
old3 = '      <div class="paywall-price">$9.99</div>\n      <div class="paywall-price-sub">/ MONTH · CANCEL ANYTIME</div>'
new3 = '      <div class="paywall-price">$4.99</div>\n      <div class="paywall-price-sub">LIFETIME ACCESS · ONE-TIME PAYMENT</div>'
assert s.count(old3) == 1, 'anchor 3 not found: ' + repr(old3[:40])
s = s.replace(old3, new3, 1)

f = open('public/index.html', 'w', encoding='utf-8')
f.write(s)
f.close()
print('done')
