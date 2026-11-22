(function () {
  var C = window.SWELTER_CONFIG || {}, V = window.VARIANT || {};
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  function store(k, v) { try { if (v === undefined) return JSON.parse(localStorage.getItem(k)); localStorage.setItem(k, JSON.stringify(v)); } catch (e) { return null; } }

  // ---- session + source ----
  var sid = store("sw_sid");
  if (!sid) { sid = Math.random().toString(36).slice(2, 10) + Date.now().toString(36); store("sw_sid", sid); }
  var q = new URLSearchParams(location.search);
  var ref = [q.get("utm_source"), q.get("utm_campaign"), q.get("utm_content")].filter(Boolean).join("|")
    || (q.get("fbclid") ? "fb" : "") || (document.referrer ? new URL(document.referrer).hostname : "direct");
  if (q.get("utm_source") || q.get("fbclid")) store("sw_ref", ref); else ref = store("sw_ref") || ref;
  var isTest = q.has("test") || store("sw_test");
  if (q.has("test")) store("sw_test", true);

  function log(event, qty, email) {
    if (!C.FORM) return;
    var f = C.FIELDS, b = new URLSearchParams();
    b.append(f.event, isTest ? "test_" + event : event); b.append(f.variant, V.slug || "");
    b.append(f.qty, qty == null ? "" : String(qty)); b.append(f.email, email || "");
    b.append(f.ref, ref); b.append(f.sid, sid);
    try {
      if (navigator.sendBeacon && navigator.sendBeacon(C.FORM, b)) return;
    } catch (e) {}
    fetch(C.FORM, { method: "POST", mode: "no-cors", body: b, keepalive: true }).catch(function () {});
  }

  // ---- Meta pixel ----
  if (C.PIXEL_ID) {
    !function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');
    fbq("init", C.PIXEL_ID); fbq("track", "PageView");
  }
  function px(ev, data) { if (window.fbq && C.PIXEL_ID) fbq("track", ev, Object.assign({ currency: C.CURRENCY, content_ids: [V.slug], content_name: V.name, content_type: "product" }, data || {})); }

  if (!V.slug) return;
  var viewKey = "sw_view_" + V.slug;
  if (!sessionStorage.getItem(viewKey)) { try { sessionStorage.setItem(viewKey, 1); } catch (e) {} log("view"); }
  px("ViewContent", { value: V.price });

  // ---- product picker ----
  var form = $("[data-buy]"), qty = 1;
  function bundle() { var r = $("input[name=bundle]:checked"); return { boxes: +r.value, price: +r.dataset.price }; }
  function total() { return bundle().price * qty; }
  function paint() { $("[data-qty]").textContent = qty; $$("[data-total]").forEach(function (e) { e.textContent = "$" + total(); }); }
  $$("[data-step]").forEach(function (b) { b.addEventListener("click", function () { qty = Math.max(1, Math.min(20, qty + +b.dataset.step)); paint(); }); });
  $$("input[name=bundle]").forEach(function (r) { r.addEventListener("change", paint); });

  // ---- cart (boxes are what we measure) ----
  var cart = store("sw_cart_" + V.slug) || [];
  function boxes() { return cart.reduce(function (s, l) { return s + l.boxes * l.qty; }, 0); }
  function sub() { return cart.reduce(function (s, l) { return s + l.price * l.qty; }, 0); }
  function save() { store("sw_cart_" + V.slug, cart); renderCart(); }
  function renderCart() {
    $$(".cart-count").forEach(function (e) { e.textContent = boxes(); });
    var el = $("[data-lines]");
    el.innerHTML = cart.length ? "" : '<p class="empty">Your cart is empty.</p>';
    cart.forEach(function (l, i) {
      var d = document.createElement("div"); d.className = "line";
      d.innerHTML = '<img src="../assets/' + V.slug + '.svg" alt=""><div><b>' + V.name + '</b><span>' + l.boxes + (l.boxes > 1 ? " boxes" : " box") + ' · $' + l.price + '</span>' +
        '<div class="stepper sm"><button data-l="' + i + '" data-d="-1">−</button><output>' + l.qty + '</output><button data-l="' + i + '" data-d="1">+</button></div></div><b>$' + l.price * l.qty + '</b>';
      el.appendChild(d);
    });
    $$("[data-l]", el).forEach(function (b) {
      b.addEventListener("click", function () {
        var l = cart[+b.dataset.l]; l.qty += +b.dataset.d;
        if (l.qty < 1) cart.splice(+b.dataset.l, 1);
        log("cart_change", boxes()); save();
      });
    });
    $("[data-subtotal]").textContent = "$" + sub();
    $("[data-ship]").textContent = boxes() >= 2 ? "Free shipping" : (boxes() ? "Add another box for free shipping" : "");
    $("[data-checkout]").disabled = !cart.length;
  }
  function openCart() { $("[data-drawer]").classList.add("open"); $("[data-drawer]").setAttribute("aria-hidden", "false"); }
  function closeAll() { $$(".open").forEach(function (e) { e.classList.remove("open"); e.setAttribute("aria-hidden", "true"); }); }

  function addToCart() {
    var b = bundle(), line = cart.filter(function (l) { return l.boxes === b.boxes; })[0];
    if (line) line.qty += qty; else cart.push({ boxes: b.boxes, price: b.price, qty: qty });
    log("add_to_cart", b.boxes * qty);
    px("AddToCart", { value: total(), num_items: b.boxes * qty });
    save(); openCart();
  }
  form.addEventListener("submit", function (e) { e.preventDefault(); addToCart(); });
  var stickyAdd = $("[data-sticky-add]");
  stickyAdd.addEventListener("click", addToCart);
  $$("[data-open-cart]").forEach(function (b) { b.addEventListener("click", openCart); });
  $$("[data-close]").forEach(function (b) { b.addEventListener("click", closeAll); });
  $$("[data-drawer],[data-modal]").forEach(function (o) { o.addEventListener("click", function (e) { if (e.target === o) closeAll(); }); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeAll(); });

  // sticky bar on mobile once the buy box scrolls away
  if ("IntersectionObserver" in window) new IntersectionObserver(function (es) { $("[data-sticky]").classList.toggle("show", !es[0].isIntersecting); }).observe(form);

  // ---- checkout -> reserve ----
  $("[data-checkout]").addEventListener("click", function () {
    log("checkout", boxes());
    px("InitiateCheckout", { value: sub(), num_items: boxes() });
    $("[data-summary]").textContent = boxes() + (boxes() > 1 ? " boxes" : " box") + " of " + V.name + " · $" + sub() + " → $" + Math.round(sub() * 0.7) + " at launch";
    closeAll(); var m = $("[data-modal]"); m.classList.add("open"); m.setAttribute("aria-hidden", "false");
  });
  $("[data-reserve]").addEventListener("submit", function (e) {
    e.preventDefault();
    var email = $("input[type=email]", e.target).value.trim();
    log("reserve", boxes(), email);
    px("Lead", { value: sub() });
    $("[data-step-reserve]").hidden = true; $("[data-step-done]").hidden = false;
    cart = []; save();
  });

  paint(); renderCart();
})();
