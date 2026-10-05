(function () {
    const panel = () => document.querySelector(".frosted");

    const go = (url, push) => {
        const p = panel();
        if (!p) { location.href = url; return; }

        fetch(url).then(r => r.ok ? r.text() : Promise.reject(r.status)).then(html => {
            const doc = new DOMParser().parseFromString(html, "text/html");
            const next = doc.querySelector(".frosted");
            if (!next) throw new Error("no .frosted in response");

            p.innerHTML = next.innerHTML;
            document.title = doc.title;
            if (push) history.pushState({}, "", url);
            window.scrollTo(0, 0);
            document.dispatchEvent(new CustomEvent("content:swapped"));
        }).catch(() => {
            location.href = url;
        });
    };

    document.addEventListener("click", (e) => {
        if (e.defaultPrevented || e.button !== 0) return;
        if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;

        const a = e.target.closest("a");
        if (!a || !a.href || a.target || a.hasAttribute("download")) return;

        const url = new URL(a.href);
        if (url.origin !== location.origin) return;
        if (url.pathname === location.pathname && url.hash) return;

        e.preventDefault();
        if (url.href === location.href) return;
        go(url.href, true);
    });

    window.addEventListener("popstate", () => go(location.href, false));
})();
