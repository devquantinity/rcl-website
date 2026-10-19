/* Rhu Law Chambers - small site behaviours (no dependencies). */
(function () {
    'use strict';

    // Dock the fixed header once the page scrolls so it stays legible over
    // light sections. A sentinel + IntersectionObserver never lags behind
    // fast or programmatic scrolling the way a scroll listener can.
    var nav = document.querySelector('.navbar');
    if (nav) {
        var dock = function (on) { nav.classList.toggle('rlc-nav-docked', on); };
        if ('IntersectionObserver' in window) {
            var sentinel = document.createElement('div');
            sentinel.setAttribute('aria-hidden', 'true');
            sentinel.style.cssText = 'position:absolute;top:0;left:0;width:1px;height:60px;pointer-events:none;visibility:hidden;';
            document.body.insertBefore(sentinel, document.body.firstChild);
            new IntersectionObserver(function (entries) { dock(!entries[0].isIntersecting); }).observe(sentinel);
        } else {
            var pending = false;
            var check = function () { pending = false; dock((window.pageYOffset || document.documentElement.scrollTop) > 60); };
            window.addEventListener('scroll', function () {
                if (!pending) { pending = true; window.requestAnimationFrame(check); }
            }, { passive: true });
            check();
        }
    }

    // While the full-screen mobile menu is open, stop the page behind it from scrolling.
    var menuButton = document.querySelector('.menu-button');
    if (menuButton && 'MutationObserver' in window) {
        new MutationObserver(function () {
            document.documentElement.classList.toggle('rlc-menu-open', menuButton.classList.contains('w--open'));
        }).observe(menuButton, { attributes: true, attributeFilter: ['class'] });
    }

    // Areas of expertise: on phones each area opens its explanation in place;
    // on wide screens the open area is shown in a column beside the list.
    var areas = document.querySelector('[data-rlc-areas]');
    if (areas) {
        var items = [].slice.call(areas.querySelectorAll('details.rlc-area'));
        var panel = areas.querySelector('.rlc-area-panel');
        var wide = window.matchMedia('(min-width: 992px)');
        var pad = function (n) { return (n < 10 ? '0' : '') + n; };
        // fade the panel's bottom edge while a long write-up has more to scroll to
        var more = function () {
            var scroller = panel && panel.querySelector('.rlc-area-scroll');
            if (!scroller) return;
            panel.classList.toggle('has-more', scroller.scrollTop + scroller.clientHeight < scroller.scrollHeight - 4);
        };
        var render = function (item) {
            if (!panel || !item) return;
            var source = item.querySelector('.rlc-area-text');
            var text = source ? '<div class="rlc-area-text">' + source.innerHTML + '</div>' : '';
            panel.innerHTML = '<div class="rlc-area-scroll">' +
                '<div class="label rlc-area-count">' + pad(items.indexOf(item) + 1) + ' / ' + items.length + '</div>' +
                '<h2 class="rlc-area-title">' + item.querySelector('summary').innerHTML + '</h2>' + text +
                '<a class="primary-button w-button" href="contact-us.html">Discuss your matter</a></div>';
            panel.hidden = false;
            panel.classList.remove('is-in');
            void panel.offsetWidth;
            panel.classList.add('is-in');
            panel.querySelector('.rlc-area-scroll').addEventListener('scroll', more, { passive: true });
            more();
        };
        window.addEventListener('resize', more);
        var only = function (item) {
            items.forEach(function (other) { if (other !== item && other.open) other.open = false; });
        };
        var fromHash = function () {
            var id = decodeURIComponent((window.location.hash || '').slice(1));
            var target = id ? document.getElementById(id) : null;
            return items.indexOf(target) !== -1 ? target : null;
        };
        items.forEach(function (item) {
            item.querySelector('summary').addEventListener('click', function (event) {
                // in the column layout one area always stays selected
                if (wide.matches && item.open) event.preventDefault();
            });
            item.addEventListener('toggle', function () {
                if (!item.open) return;
                only(item);
                if (wide.matches) { render(item); return; }
                // closing an open area above can pull this one up under the header
                var top = item.getBoundingClientRect().top;
                if (top < 80) window.scrollBy(0, top - 96);
            });
        });
        var sync = function () {
            if (!wide.matches) return;
            var current = items.filter(function (i) { return i.open; })[0] || fromHash() || items[0];
            only(current);
            current.open = true;
            render(current);
        };
        var start = fromHash();
        if (start) start.open = true;
        areas.classList.add('is-ready');
        sync();
        if (wide.addEventListener) wide.addEventListener('change', sync);
        else if (wide.addListener) wide.addListener(sync);
        window.addEventListener('hashchange', function () {
            var target = fromHash();
            if (!target) return;
            target.open = true;
            if (wide.matches) render(target);
        });
    }

    // Enquiry form: posts to the form relay, which emails enquiry@rlchambers.com.my.
    var form = document.querySelector('form[data-rlc-enquiry]');
    if (!form) return;
    var status = document.getElementById('rlc-enquiry-status');
    var button = form.querySelector('[type="submit"]');
    var idle = button ? button.value : '';

    function show(kind, html) {
        if (!status) return;
        status.className = 'rlc-form-status is-' + kind;
        status.innerHTML = html;
        status.hidden = false;
        status.focus();
    }

    form.addEventListener('submit', function (event) {
        event.preventDefault();
        if (form.elements._honey && form.elements._honey.value) return;
        if (!form.checkValidity()) { form.reportValidity(); return; }

        var data = {};
        new FormData(form).forEach(function (value, key) { data[key] = value; });
        data._subject = 'Website enquiry - ' + (data.name || 'New enquiry') + (data.area ? ' (' + data.area + ')' : '');
        data._template = 'table';
        data._captcha = 'false';

        if (button) { button.disabled = true; button.value = 'Sending…'; }
        if (status) status.hidden = true;

        fetch(form.getAttribute('data-endpoint'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
            body: JSON.stringify(data)
        })
            .then(function (response) {
                return response.json().catch(function () { return {}; }).then(function (json) {
                    if (!response.ok || !(json.success === true || json.success === 'true')) throw new Error(json.message || 'Not sent');
                });
            })
            .then(function () {
                form.reset();
                show('success', 'Thank you. Your enquiry has been sent and our team will get back to you shortly.');
            })
            .catch(function () {
                show('error', 'Sorry, your enquiry could not be sent just now. Please email us at <a href="mailto:enquiry@rlchambers.com.my">enquiry@rlchambers.com.my</a> or call +60 12-399 1241.');
            })
            .then(function () {
                if (button) { button.disabled = false; button.value = idle; }
            });
    });
})();
