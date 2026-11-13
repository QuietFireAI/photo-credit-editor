/*! photo-credit.js: shows photo credits on a website from photo-credits.json. MIT License.
 *
 * Add one tag near the end of each page that should show credits:
 *
 *   <script src="js/photo-credit.js" defer
 *           data-manifest="photo-credits.json"
 *           data-list="#creditList"
 *           data-rotators=".hero-slideshow"
 *           data-images="main img"></script>
 *
 * Every data- setting is optional:
 *   data-manifest    where photo-credits.json lives, relative to the page  (default "photo-credits.json")
 *   data-list        element to fill with the full credits list           (default "#creditList")
 *   data-rotators    slideshow boxes that get a small caption for the slide on show
 *   data-active      inside a slideshow, the selector for the slide on show (for example ".active").
 *                    Leave it out for fade slideshows: the most opaque slide is used.
 *   data-images      ordinary pictures that get a credit line under them
 *   data-item-class  class put on each entry in the credits list          (default "photo-credit-item")
 *   data-prefix      text before a caption                                (default "Photo: ")
 *   data-empty       text shown in the list when no picture has a credit yet
 *   data-style       "off" to skip the small built-in caption styling
 *
 * The script reads the one JSON file from your own site. It sends nothing anywhere.
 */
(function () {
  'use strict';

  var tag = document.currentScript;
  function opt(name, fallback) {
    var v = tag ? tag.getAttribute('data-' + name) : null;
    return v === null ? fallback : v;
  }
  var cfg = {
    manifest: opt('manifest', 'photo-credits.json'),
    list: opt('list', '#creditList'),
    rotators: opt('rotators', ''),
    active: opt('active', ''),
    images: opt('images', ''),
    itemClass: opt('item-class', 'photo-credit-item'),
    prefix: opt('prefix', 'Photo: '),
    empty: opt('empty', 'Credits are being gathered and will be listed here.'),
    style: opt('style', 'on') !== 'off'
  };

  var entries = [];   // { key, base, data }
  var cache = {};

  function stripExt(p) { return p.replace(/\.[a-z0-9]+$/i, ''); }
  function baseName(p) { return p.slice(p.lastIndexOf('/') + 1); }
  function decode(p) { try { return decodeURIComponent(p); } catch (e) { return p; } }

  /* A path as written in photo-credits.json, relative to the site's top folder. */
  function entryKey(file) {
    var p = decode(String(file || '').trim().split(/[?#]/)[0]).replace(/\\/g, '/').replace(/^(\.\/|\/)+/, '');
    return stripExt(p).toLowerCase();
  }
  /* A picture address as the browser sees it: src, or a CSS background-image value. */
  function urlKey(u) {
    u = String(u || '').trim();
    var m = u.match(/url\((['"]?)(.*?)\1\)/i);
    if (m) u = m[2];
    if (!u || u === 'none') return '';
    try { u = new URL(u, document.baseURI).pathname; } catch (e) { u = u.split(/[?#]/)[0]; }
    return stripExt(decode(u).replace(/^\/+/, '')).toLowerCase();
  }

  /* Find the credit for a picture address. The file type is ignored, so a .webp copy matches the .jpg entry. */
  function find(u) {
    var k = urlKey(u);
    if (!k) return null;
    if (k in cache) return cache[k];
    var best = null, i;
    for (i = 0; i < entries.length; i++) {
      var e = entries[i];
      if (k === e.key || k.slice(-(e.key.length + 1)) === '/' + e.key) {
        if (!best || e.key.length > best.key.length) best = e;
      }
    }
    if (!best) {
      var b = baseName(k), hits = [];
      for (i = 0; i < entries.length; i++) if (entries[i].base === b) hits.push(entries[i]);
      if (hits.length === 1) best = hits[0];
    }
    cache[k] = best ? best.data : null;
    return cache[k];
  }

  function line(p) { return p.credit + (p.source ? ', ' + p.source : ''); }
  /* The page for a Creative Commons license, worked out from its name, so the license can be linked as the license asks. */
  function licenseUrl(p) {
    if (/^https?:\/\//i.test(p.licenseUrl || '')) return p.licenseUrl;
    var name = String(p.license || '');
    var m = /\bcc[ -]?(by(?:-(?:nc|nd|sa))*)[ -]?(\d\.\d)/i.exec(name);
    if (m) return 'https://creativecommons.org/licenses/' + m[1].toLowerCase() + '/' + m[2] + '/';
    if (/\bcc0\b/i.test(name)) return 'https://creativecommons.org/publicdomain/zero/1.0/';
    return '';
  }
  function shown(p) { return p && !p.skip && String(p.credit || '').trim(); }

  function addStyle() {
    if (!cfg.style || document.getElementById('photo-credit-style')) return;
    var s = document.createElement('style');
    s.id = 'photo-credit-style';
    /* :where() keeps these rules at the lowest priority, so any rule in the site's own stylesheet wins. */
    s.textContent =
      ':where(.photo-credit){position:absolute;right:0;bottom:0;z-index:2;padding:2px 8px;font:11px/1.4 system-ui,sans-serif;' +
      'color:#fff;background:rgba(0,0,0,.55);pointer-events:none;transition:opacity .3s}' +
      ':where(.photo-credit-inline){display:block;font-size:.75em;opacity:.75}';
    document.head.appendChild(s);
  }

  function fillList(photos) {
    if (!cfg.list) return;
    var list;
    try { list = document.querySelector(cfg.list); } catch (e) { list = null; }
    if (!list) return;
    list.textContent = '';
    var rows = photos.filter(shown);
    if (!rows.length) {
      var none = document.createElement('p');
      none.className = 'photo-credit-empty';
      none.textContent = cfg.empty;
      list.appendChild(none);
      return;
    }
    rows.forEach(function (p) {
      var item = document.createElement('div');
      item.className = cfg.itemClass;
      var h = document.createElement('h3');
      h.textContent = p.title || p.file;
      item.appendChild(h);
      var who = document.createElement('p');
      who.textContent = line(p);
      item.appendChild(who);
      if (p.license) {
        var lic = document.createElement('p');
        lic.className = 'photo-credit-license';
        var deed = licenseUrl(p);
        if (deed) {
          var la = document.createElement('a');
          la.href = deed; la.target = '_blank'; la.rel = 'license noopener noreferrer';
          la.textContent = p.license;
          lic.appendChild(la);
        } else {
          lic.textContent = p.license;
        }
        item.appendChild(lic);
      }
      if (/^https?:\/\//i.test(p.link || '')) {
        var a = document.createElement('a');
        a.href = p.link; a.target = '_blank'; a.rel = 'noopener noreferrer';
        a.textContent = 'Source';
        item.appendChild(a);
      }
      list.appendChild(item);
    });
  }

  function slideUrl(el) {
    if (!el) return '';
    if (el.tagName === 'IMG') return el.currentSrc || el.getAttribute('src') || '';
    var bg = getComputedStyle(el).backgroundImage;
    if (bg && bg !== 'none') return bg;
    var img = el.querySelector('img');
    return img ? (img.currentSrc || img.getAttribute('src') || '') : '';
  }

  function slideOnShow(box) {
    if (cfg.active) {
      try { return box.querySelector(cfg.active); } catch (e) { return null; }
    }
    var on = null, top = 0.5;
    for (var i = 0; i < box.children.length; i++) {
      var c = box.children[i];
      if (c.classList.contains('photo-credit')) continue;
      var cs = getComputedStyle(c);
      if (cs.display === 'none' || cs.visibility === 'hidden') continue;
      var o = parseFloat(cs.opacity);
      if (o >= top) { top = o; on = c; }
    }
    return on;
  }

  function tagRotators() {
    var boxes, animated = false;
    try { boxes = document.querySelectorAll(cfg.rotators); } catch (e) { return false; }
    Array.prototype.forEach.call(boxes, function (box) {
      var cap = null;
      for (var i = 0; i < box.children.length; i++) {
        var c = box.children[i];
        if (c.classList.contains('photo-credit')) cap = c;
        else if (getComputedStyle(c).animationName !== 'none') animated = true;
      }
      var on = slideOnShow(box);
      var p = find(slideUrl(on) || slideUrl(box));
      if (!shown(p)) { if (cap && cap.style.opacity !== '0') cap.style.opacity = '0'; return; }
      if (!cap) {
        cap = document.createElement('div');
        cap.className = 'photo-credit';
        if (getComputedStyle(box).position === 'static') box.style.position = 'relative';
        box.appendChild(cap);
      }
      var text = cfg.prefix + line(p);
      if (cap.textContent !== text) cap.textContent = text;
      if (cap.style.opacity !== '1') cap.style.opacity = '1';
    });
    return animated;
  }

  /* Every address a picture may be using, including the ones lazy loaders keep until the picture is needed. */
  function addresses(img) {
    return [img.currentSrc, img.getAttribute('src'), img.getAttribute('data-src'),
      img.getAttribute('data-lazy-src'), img.getAttribute('data-original')].filter(Boolean);
  }

  function tagImages() {
    var imgs;
    try { imgs = document.querySelectorAll(cfg.images); } catch (e) { return; }
    Array.prototype.forEach.call(imgs, function (img) {
      if (img.tagName !== 'IMG') return;
      var list = addresses(img), signature = list.join('|');
      if (img._photoCreditFor === signature) return;        // nothing about this picture changed
      img._photoCreditFor = signature;
      var p = null;
      for (var i = 0; i < list.length && !p; i++) { var hit = find(list[i]); if (shown(hit)) p = hit; }
      var cap = img._photoCreditCaption;
      if (!p) {                                             // the picture changed to one with no credit
        if (cap) { cap.remove(); img._photoCreditCaption = null; }
        return;
      }
      if (!cap) {
        cap = document.createElement('span');
        cap.className = 'photo-credit-inline';
        var fig = img.closest('figure');
        if (fig) {
          var fc = fig.querySelector('figcaption');
          if (!fc) { fc = document.createElement('figcaption'); fig.appendChild(fc); }
          fc.appendChild(cap);
        } else {
          img.insertAdjacentElement('afterend', cap);
        }
        img._photoCreditCaption = cap;
      }
      var text = cfg.prefix + line(p);
      if (cap.textContent !== text) cap.textContent = text;
    });
  }

  /* Captions are brought up to date when the page changes, not on a clock. */
  var waiting = null, clock = null;
  function refresh() {
    waiting = null;
    var animated = cfg.rotators ? tagRotators() : false;
    if (cfg.images) tagImages();
    /* A slideshow run purely by a CSS animation changes with no page event to listen for.
       Only then is a once-a-second check kept, and only while the page is on show. */
    if (animated && !clock) clock = setInterval(function () { if (!document.hidden) schedule(); }, 1000);
    else if (!animated && clock) { clearInterval(clock); clock = null; }
  }
  function schedule() { if (!waiting) waiting = setTimeout(refresh, 200); }
  function ours(node) { return node && node.nodeType === 1 && /(^|\s)photo-credit(-inline)?(\s|$)/.test(node.className || ''); }
  function watch() {
    if (typeof MutationObserver === 'undefined') { setInterval(schedule, 1000); return; }
    new MutationObserver(function (records) {
      for (var i = 0; i < records.length; i++) {
        var r = records[i];
        if (ours(r.target)) continue;                       // our own captions changing
        if (r.type === 'childList' && r.addedNodes.length + r.removedNodes.length &&
            Array.prototype.every.call(r.addedNodes, ours) && Array.prototype.every.call(r.removedNodes, ours)) continue;
        schedule();
        return;
      }
    }).observe(document.documentElement, {
      subtree: true, childList: true, attributes: true,
      attributeFilter: ['src', 'srcset', 'style', 'class', 'hidden', 'data-src', 'data-lazy-src', 'data-original']
    });
    ['load', 'transitionend', 'animationend', 'animationiteration'].forEach(function (name) {
      document.addEventListener(name, schedule, true);
    });
  }

  function start(d) {
    var photos = d && Array.isArray(d.photos) ? d.photos : (Array.isArray(d) ? d : []);
    photos = photos.filter(function (p) { return p && typeof p === 'object' && p.file; });
    photos.forEach(function (p) {
      if (!shown(p)) return;
      var k = entryKey(p.file);
      if (k) entries.push({ key: k, base: baseName(k), data: p });
    });
    addStyle();
    fillList(photos);
    if (cfg.rotators || cfg.images) { refresh(); watch(); }
  }

  function run() {
    /* The hour stamp lets a freshly uploaded photo-credits.json show up within an hour despite caching. */
    var url = cfg.manifest + (cfg.manifest.indexOf('?') === -1 ? '?' : '&') + 'v=' + Math.floor(Date.now() / 36e5);
    fetch(url).then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); }).then(start).catch(function (e) {
      if (window.console && console.warn) console.warn('photo-credit.js: could not read ' + cfg.manifest + ' (' + e.message + ')');
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', run);
  else run();
})();
