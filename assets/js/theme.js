(function () {
    const root = document.documentElement;

    // The address-bar colour on mobile. Read from --surface rather than
    // repeated here, so the palette in base.css stays the only place a colour
    // is written down. See the palette note at the top of that file.
    const meta = document.querySelector('meta[name="theme-color"]');
    const paintChrome = () => {
        if (!meta) return;
        const surface = getComputedStyle(root).getPropertyValue("--surface").trim();
        if (surface) meta.setAttribute("content", surface);
    };

    // The button is a two-state control, so say so rather than leaving a
    // screen reader to infer it from an icon drawn in CSS.
    const describe = () => {
        const light = root.getAttribute("data-theme") === "light";
        document.querySelectorAll(".nav-toggle").forEach((b) => {
            b.setAttribute("aria-pressed", String(light));
            b.setAttribute("title", light ? "Switch to dark mode" : "Switch to light mode");
        });
    };

    const apply = (next, remember) => {
        const fade = parseFloat(getComputedStyle(root).getPropertyValue("--theme-fade")) * 1000;

        root.classList.add("theming");
        root.setAttribute("data-theme", next);
        if (remember) { try { localStorage.setItem("theme", next); } catch (err) {} }
        paintChrome();
        describe();
        setTimeout(() => root.classList.remove("theming"), fade);
    };

    document.addEventListener("click", (e) => {
        if (!e.target.closest(".nav-toggle")) return;
        apply(root.getAttribute("data-theme") === "light" ? "dark" : "light", true);
    });

    // A reader who has never touched the toggle is following their operating
    // system (see the bootstrap in _includes/head.html), so keep following it
    // when it changes rather than stranding them in whichever theme the OS
    // happened to be in when the page loaded. Anyone who has chosen is left
    // alone. addEventListener on a MediaQueryList is the modern spelling;
    // older Safari only has addListener.
    const os = window.matchMedia && window.matchMedia("(prefers-color-scheme: light)");
    const follow = (e) => {
        let stored = null;
        try { stored = localStorage.getItem("theme"); } catch (err) {}
        if (stored === "light" || stored === "dark") return;
        apply(e.matches ? "light" : "dark", false);
    };
    if (os) {
        if (os.addEventListener) os.addEventListener("change", follow);
        else if (os.addListener) os.addListener(follow);
    }

    // The nav currently lives outside the panel nav.js swaps, so the toggle
    // survives an in-page navigation - but re-describing costs nothing and
    // means the state stays right if the nav ever moves inside it.
    document.addEventListener("content:swapped", describe);

    paintChrome();
    describe();
})();
