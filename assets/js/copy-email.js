// Copy-email buttons (.copy-email with data-u / data-d): the address is only
// assembled on click, so it never appears whole in the page. Delegated on the
// document so it keeps working after nav.js swaps the page content.
(function () {
    document.addEventListener("click", function (e) {
        const b = e.target.closest(".copy-email");
        if (!b) return;
        const addr = b.dataset.u + "@" + b.dataset.d;
        const tip = b.querySelector(".copy-email-tip");
        const done = (msg) => {
            if (!tip) return;
            tip.textContent = msg;
            tip.classList.add("show");
            clearTimeout(b._t);
            b._t = setTimeout(() => tip.classList.remove("show"), 1600);
        };
        const fallback = () => {
            const t = document.createElement("textarea");
            t.value = addr;
            t.setAttribute("readonly", "");
            t.style.position = "fixed";
            t.style.opacity = "0";
            document.body.appendChild(t);
            t.select();
            let ok = false;
            try { ok = document.execCommand("copy"); } catch (x) {}
            t.remove();
            done(ok ? "Email copied" : "Copy failed");
        };
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(addr).then(() => done("Email copied"), fallback);
        } else {
            fallback();
        }
    });
})();
