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
