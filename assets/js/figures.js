(function () {
    const VERBOSE = location.search.includes("debug");
    const L = (...a) => { if (VERBOSE) console.log("[fig]", ...a); };
    const W = (...a) => console.warn("[fig]", ...a);
    const E = (...a) => console.error("[fig]", ...a);

    // Read from the chart's own element when given one, so a container can
    // re-declare the palette for the charts inside it (see .figure-card in
    // base.css, which puts a chart on a light card in dark mode).
    const css = (n, el) => getComputedStyle(el || document.documentElement).getPropertyValue(n).trim();

    // The site may be served from a sub-path (a GitHub project page lives at
    // /<repo>/), so a root-absolute path like "/assets/data/x.json" - in a
    // data-vega attribute, a spec's data.url, or the vendor scripts below - is
    // resolved against the site root, found from this script's own URL
    // (<root>/assets/js/figures.js), rather than against the domain root.
    const SITE_ROOT = new URL("../../", document.currentScript.src);
    const siteUrl = (u) => (typeof u === "string" && u.startsWith("/") && !u.startsWith("//"))
        ? new URL(u.slice(1), SITE_ROOT).href : u;
    const rebaseDataUrls = (v) => {
        if (Array.isArray(v)) { v.forEach(rebaseDataUrls); return v; }
        if (v && typeof v === "object") {
            if (v.data && typeof v.data.url === "string") v.data.url = siteUrl(v.data.url);
            Object.keys(v).forEach(k => rebaseDataUrls(v[k]));
        }
        return v;
    };

    // matches the site's own mobile breakpoint (assets/css/base.css)
    const MOBILE_BP = 700;
    const isMobile = () => window.innerWidth <= MOBILE_BP;

    // Layout follows the width breakpoint above, but "can this thing hover?"
    // is a different question and width is a bad proxy for it: a tablet, or a
    // phone turned sideways, is well past 700px and still has no pointer to
    // hover with. (hover: hover) asks the device directly. Assume it can hover
    // where the query isn't supported, which just keeps today's behaviour.
    const canHover = () => !window.matchMedia || window.matchMedia("(hover: hover)").matches;

    const LIBS = ["vega.min.js", "vega-lite.min.js", "vega-embed.min.js"];

    const script = (src) => new Promise((ok, no) => {
        const s = document.createElement("script");
        s.src = src;
        s.onload = ok;
        s.onerror = () => no(new Error("could not load " + src));
        document.head.appendChild(s);
    });

    let loading;
    const ensureLibs = () => loading || (loading = LIBS.reduce(
        (p, f) => p.then(() => script(siteUrl("/assets/js/vendor/" + f))), Promise.resolve()));

    // A spec is fetched once per page and re-used for every later render of it
    // - a theme switch and a breakpoint crossing both re-render, and neither
    // changes what is on disk. A failed fetch is dropped from the cache so it
    // can be retried rather than failing forever.
    const specs = new Map();
    const loadSpec = (src) => {
        if (!specs.has(src)) {
            specs.set(src, fetch(siteUrl(src))
                .then(r => { L("spec fetch:", r.status, src); return r.ok ? r.json() : Promise.reject(new Error("HTTP " + r.status + " " + src)); })
                .catch(err => { specs.delete(src); throw err; }));
        }
        return specs.get(src);
    };

    const fail = (el, msg, err) => {
        if (el._view) { try { el._view.finalize(); } catch (e) {} el._view = null; }
        el.style.position = "";
        el.innerHTML = '<div class="figure-placeholder">' + msg + '</div>';
        E(msg, err || "");
        if (err && err.stack) E(err.stack);
    };

    // The page's ink, read from the raw (never-transitioned) palette variables
    // rather than the --primary-color/--secondary-color paint aliases. Those
    // aliases cross-fade on a theme switch, and getComputedStyle reports a
    // transitioning custom property as wherever the fade has got to - so a
    // chart drawn mid-switch used to bake in a half-faded grey, or, if it got
    // there first, the colour of the theme being left behind. See the palette
    // note at the top of assets/css/base.css.
    const ink = (el) => css("--ink", el);
    const inkDim = (el) => css("--ink-dim", el);

    // Most of this is belt-and-braces: the axis/legend/title colours below are
    // also set in CSS (see "chart chrome" in base.css), which is what makes a
    // theme switch instant. They stay here because the config is what the
    // exported PNG is rendered from, and CSS does not reach that.
    //
    // `header` covers the panel titles of a faceted chart. They are not axis
    // titles, legend titles or the chart title, so none of the other blocks
    // apply and Vega's own default - black - wins by default; that is why the
    // facet labels used to sit invisibly on the dark background.
    // The site's two sequential ramps, quiet end first, registered as Vega
    // schemes so a spec can ask for one by name - "theme-cool" for the
    // goals-style figures, "theme-warm" for the cost ones - instead of naming
    // a built-in like "blues", which is fixed in absolute terms and so cannot
    // follow the page. Re-registered on every render, which is what makes
    // them change with the theme; see the ramp note in base.css for why a
    // ramp has to be declared per theme rather than shared.
    const STOPS = ["-0", "-25", "-50", "-75", "-100"];
    const registerSchemes = () => {
        if (typeof vega === "undefined" || !vega.scheme) return;
        [["theme-cool", "--seq"], ["theme-warm", "--warm"]].forEach(([name, prefix]) => {
            const stops = STOPS.map(k => css(prefix + k)).filter(Boolean);
            if (stops.length === STOPS.length) vega.scheme(name, stops);
            else W("incomplete ramp for " + name + "; leaving it alone");
        });
    };

    const theme = (el) => {
        const ramp = ["--seq-0", "--seq-50", "--seq-100"].map(n => css(n, el)).filter(Boolean);
        const cats = ["--cat-1", "--cat-2", "--cat-3"].map(n => css(n, el)).filter(Boolean);
        const fg = ink(el), dim = inkDim(el);
        const disp = css("--font-display");
        const cfg = {
            background: "transparent",
            font: css("--font-body") || "sans-serif",
            axis: {
                labelColor: fg, titleColor: fg,
                labelFont: disp, titleFont: disp,
                labelFontSize: 12, titleFontSize: 12,
                domainColor: dim, tickColor: dim, grid: false
            },
            legend: {
                labelColor: fg, titleColor: fg,
                labelFont: css("--font-body"), titleFont: disp,
                labelFontSize: 12, titleFontSize: 12
            },
            header: {
                labelColor: fg, titleColor: fg,
                labelFont: disp, titleFont: disp,
                labelFontSize: 12, titleFontSize: 12
            },
            title: { color: fg, subtitleColor: fg, font: disp, fontSize: 14 },
            text: { color: fg, font: disp },
            view: { stroke: "transparent" },
            point: { stroke: null }
        };
        if (ramp.length === 3 || cats.length === 3) cfg.range = {};
        if (ramp.length === 3) cfg.range.heatmap = ramp;
        if (cats.length === 3) cfg.range.category = cats;
        return cfg;
    };

    // A spec can name a palette colour anywhere a colour is allowed by writing
    // the CSS variable without its leading dashes: "$ink", "$ink-dim",
    // "$surface", "$accent", "$seq-75", "$cat-2", and so on. They are resolved
    // against the current theme every time the chart is drawn, so a spec that
    // has to paint something itself - a cell stroke, a hand-placed rule -
    // still follows the theme instead of freezing one mode's hex code into the
    // JSON. Anything that is genuinely theme-independent (text sitting on top
    // of a coloured cell, say, where the cell is the background rather than
    // the page) should stay a literal hex code.
    //
    // Walking the whole spec also deep-copies it, which is what lets the
    // fetched spec be cached and re-used: render() mutates its copy.
    const TOKEN = /^\$([a-z][a-z0-9-]*)$/;
    const resolvePalette = (v, el) => {
        if (typeof v === "string") {
            const m = TOKEN.exec(v);
            if (!m) return v;
            const val = css("--" + m[1], el);
            if (!val) { W("unknown palette token " + v + " - left as-is"); return v; }
            return val;
        }
        if (Array.isArray(v)) return v.map(x => resolvePalette(x, el));
        if (v && typeof v === "object") {
            const out = {};
            Object.keys(v).forEach(k => { out[k] = resolvePalette(v[k], el); });
            return out;
        }
        return v;
    };

    // A spec with `"width": "container"` shrinks its plot to fit the phone,
    // starving discrete columns (e.g. 3 model columns with un-rotated labels)
    // until their labels collide - CSS can't fix that, since it's the actual
    // rendered plot that's too narrow, not oversized content being squashed.
    // A spec that wants a floor under that on narrow screens sets top-level
    // `_minMobileWidth` to the smallest plot width (px) its labels need; below
    // that the plot renders at that fixed width instead of the container's,
    // and el's own `overflow-x: auto` (see base.css) lets it scroll into view.
    const applyMinMobileWidth = (spec, el) => {
        const minWidth = spec._minMobileWidth;
        if (!minWidth || spec.width !== "container") return spec;
        spec.width = Math.max(el.offsetWidth || 0, minWidth);
        return spec;
    };

    // `"width": "container"` is only honoured on single and layered specs, not
    // faceted ones: a faceted chart renders at whatever fixed width its panels
    // declare, so any column wider than that leaves a gap down the right. A
    // faceted spec that wants to fill its column sets `_fitPanels` to its
    // column count, and the panel width gets measured off the container here.
    // MIN_PANEL keeps the panels legible on a phone instead of letting three
    // of them divide a 360px screen; el's own `overflow-x: auto` scrolls when
    // that floor makes the figure wider than the screen.
    // A faceted chart laid out in a row spends width, which is the one thing a
    // phone has none of: three panels side by side either shrink past
    // legibility or push the figure into a horizontal scroll. A spec that
    // reads as well stacked sets `_mobileStack` and gets one column on narrow
    // screens, trading the scarce axis for the plentiful one. Its `spacing`
    // should be a {row, column} pair, since stacking swaps which one applies.
    // A spec can declare params whose value should differ on a phone - the
    // reach of a mark that is sized for a wide layout, say - as
    // `_mobileParams: {name: value}`. Overriding the declared value keeps the
    // number that matters in the spec next to the mark that uses it, rather
    // than as a magic constant in here.
    const applyMobileParams = (spec) => {
        const overrides = spec._mobileParams;
        if (!overrides || !spec.params) return spec;
        spec.params.forEach((p) => {
            if (Object.prototype.hasOwnProperty.call(overrides, p.name)) p.value = overrides[p.name];
        });
        return spec;
    };

    const stackFacets = (spec) => {
        if (!spec._mobileStack || !spec.facet) return spec;
        // `columns` is a sibling of `facet`, not a property of it - Vega-Lite
        // ignores it silently in the wrong place.
        spec.columns = 1;
        // Laid out in a row, every panel sits on the same bottom edge and can
        // share one x axis. Stacked, the shared axis is drawn under the last
        // panel only, leaving the two above it with nothing to read against -
        // so each cell gets its own. The scale stays shared, so they are still
        // directly comparable.
        spec.resolve = spec.resolve || {};
        spec.resolve.axis = Object.assign({}, spec.resolve.axis, { x: "independent" });
        if (spec._fitPanels) spec._fitPanels = 1;
        return spec;
    };

    const MIN_PANEL = 150;
    // room the shared y axis (labels + title) and the outer padding need, which
    // sits outside the panels and so can't be divided among them
    const FACET_CHROME = 68;
    // vega-embed reserves this much to the right of every chart for its export
    // button (.vega-embed.has-actions). It is outside the svg but inside the
    // scroll container, so a chart sized to the container's full width
    // overflows by exactly this much.
    const ACTIONS_GUTTER = 38;
    const fitPanels = (spec, el) => {
        const n = spec._fitPanels;
        if (!n || !spec.spec) return spec;
        const avail = el.offsetWidth || 0;
        if (!avail) return spec;
        // spacing is either a number or a {row, column} pair; only the column
        // half sits between panels laid out in a row. Multiplying the object
        // itself gives NaN, which silently collapses the view to 0x0.
        const spacing = spec.spacing && typeof spec.spacing === "object"
            ? (spec.spacing.column || 0) : (spec.spacing || 0);
        const gaps = spacing * (n - 1);
        // A spec whose marks deliberately reach outside their panel (the
        // Incalmo ring, say) declares how much room that needs in total as
        // `_panelBleed`; without it the panels are sized as if the chart ended
        // at their edges and the figure overflows by exactly that much.
        const bleed = spec._panelBleed || 0;
        const room = avail - gaps - FACET_CHROME - bleed - ACTIONS_GUTTER;
        spec.spec.width = Math.max(Math.floor(room / n), MIN_PANEL);
        return spec;
    };

    // Where the actual marks live. A plain spec is its own unit; a layered one
    // keeps them in .layer; a faceted one wraps the whole child chart (layers
    // and all) in .spec. The patches below all walk marks, so they all need to
    // find them the same way - without this, a faceted spec silently skips
    // every one of them, tooltip-stripping included.
    const units = (spec) => {
        const inner = spec.spec || spec;
        return inner.layer || [inner];
    };

    // Vega-Lite's global config.legend doesn't propagate orient/direction/columns
    // (those are layout properties, not the styling ones config.legend actually
    // supports) - they have to be set per-encoding. On narrow screens, move every
    // color/shape legend under the plot instead of letting it eat into the plot's
    // width from the right, which is what squashes a categorical-legend chart
    // (like the scatterplot) on a phone.
    const patchLegendsForMobile = (spec) => {
        const bottomLegend = { orient: "bottom", direction: "horizontal", columns: 0 };
        const patchEncoding = (enc) => {
            if (!enc) return;
            ["color", "shape", "size", "opacity"].forEach((ch) => {
                if (enc[ch] && enc[ch].field) {
                    enc[ch].legend = Object.assign({}, enc[ch].legend, bottomLegend);
                }
            });
        };
        units(spec).forEach((u) => patchEncoding(u.encoding));
        return spec;
    };

    // A tooltip is a hover affordance, and a touch screen has no hover: every
    // tap on a mark pops one up, and it sits there until you happen to tap
    // somewhere else. Drop them wherever the device can't hover - both by
    // dropping the encodings (so the marks carry no tooltip data at all) and
    // by turning off the handler at embed time, since either alone is enough
    // but the pair leaves nothing to go wrong. Anything with a real pointer
    // keeps its tooltips; the specs on disk are untouched either way.
    const stripTooltips = (spec) => {
        units(spec).forEach((u) => {
            if (u.encoding) delete u.encoding.tooltip;
        });
        return spec;
    };

    // The shape legend (model) carries no colour of its own - colour is a
    // separate channel there (harness) - so Vega-Lite falls back to the point
    // mark's defaults for its symbols, and theme() sets point.stroke to null.
    // That leaves the symbols drawn in nothing much at all, which is why they
    // vanish against the dark background. Paint them with the dim ink,
    // which is a light grey in dark mode and a dark grey in light mode, so
    // they read in either theme; theme changes re-render, so this follows.
    // Fill and stroke both, since which one a symbol uses depends on its
    // shape. The colour legend is deliberately untouched - those symbols
    // carry the category colours and have to keep them.
    const patchShapeLegend = (spec, el) => {
        const dim = inkDim(el);
        if (!dim) return spec;
        units(spec).forEach((u) => {
            const enc = u.encoding;
            if (enc && enc.shape && enc.shape.field) {
                enc.shape.legend = Object.assign({}, enc.shape.legend, {
                    symbolFillColor: dim, symbolStrokeColor: dim
                });
            }
        });
        return spec;
    };

    const inspect = (el, view) => {
        const svg = el.querySelector("svg");
        L("view size:", view.width(), "x", view.height());
        L("container offsetWidth:", el.offsetWidth, " clientWidth:", el.clientWidth);
        if (!svg) { W("NO <svg> in the container"); L("container HTML:", el.innerHTML.slice(0, 400)); return; }
        const bb = svg.getBoundingClientRect();
        L("svg attrs w/h:", svg.getAttribute("width"), svg.getAttribute("height"));
        L("svg bounding box:", Math.round(bb.width), "x", Math.round(bb.height));
        L("svg computed display/visibility/opacity:",
          getComputedStyle(svg).display, getComputedStyle(svg).visibility, getComputedStyle(svg).opacity);
        L("marks: rect=", svg.querySelectorAll("rect").length,
          " path=", svg.querySelectorAll("path").length,
          " text=", svg.querySelectorAll("text").length);
        const r = svg.querySelector("g.mark-rect rect") || svg.querySelector("rect");
        if (r) L("first rect:", r.getAttribute("width"), "x", r.getAttribute("height"),
                 "fill=", r.getAttribute("fill"), "opacity=", r.getAttribute("opacity"));
        try {
            const names = Object.keys(view.getState({ data: true, signals: false }).data || {});
            L("view datasets:", names);
            names.forEach(n => {
                const d = view.data(n);
                if (d && d.length) L("  " + n + ": " + d.length + " rows; sample=", JSON.stringify(d[0]).slice(0, 220));
                else L("  " + n + ": EMPTY");
            });
        } catch (e) { W("could not enumerate datasets:", e.message); }
    };

    const observe = (el) => {
        el._mobile = isMobile();
        if (el._ro || typeof ResizeObserver !== "function") return;
        el._ro = new ResizeObserver(() => {
            const nowMobile = isMobile();
            if (nowMobile !== el._mobile) { el._mobile = nowMobile; render(el); return; }
            // A fit-to-container facet has its panel width baked into the spec,
            // so view.resize() can't widen it - only a re-render can. Wait for a
            // change worth the work, so dragging a window edge doesn't re-embed
            // on every animation frame.
            if (el._fitWidth && Math.abs(el.offsetWidth - el._fitWidth) > 24) { render(el); return; }
            if (el._view) el._view.resize().run();
        });
        el._ro.observe(el);
    };

    const render = (el) => {
        const src = el.dataset.vega;
        if (!src) return;
        L("--- rendering", src, "---");
        L("libs: vega=", typeof vega !== "undefined" ? vega.version : "MISSING",
          " vega-lite=", typeof vegaLite !== "undefined" ? vegaLite.version : "MISSING",
          " vegaEmbed=", typeof vegaEmbed);
        L("css vars: primary=", css("--primary-color"), " seq0=", css("--seq-0"),
          " seq100=", css("--seq-100"), " fontBody=", css("--font-body").slice(0, 30));
        L("container width before embed:", el.offsetWidth);

        if (typeof vegaEmbed !== "function") { fail(el, "vegaEmbed not loaded"); return; }

        // Whatever is already on screen stays there until the replacement is
        // ready, so a re-render (a theme switch, a breakpoint crossing) swaps
        // rather than blinking through an empty box. The incoming chart is
        // measured and drawn out of view but still laid out - visibility,
        // not display, so text metrics are real - at the same width it will
        // occupy once it takes over.
        const old = el.firstElementChild;
        const oldView = el._view;
        // vegaEmbed adds its own classes (.vega-embed, .has-actions, ...) directly
        // onto whatever element it's given, rather than wrapping it - so embedding
        // straight into `el` (.figure) would make .figure and .vega-embed the same
        // node. That breaks the scroll-container pattern used elsewhere on this
        // site (e.g. .table-wrap > table): .figure needs to stay pinned to the
        // viewport width so its overflow-x:auto has something to scroll against,
        // while .vega-embed needs to size to its actual (possibly wider) content
        // so the export button - position:absolute against .vega-embed's own box -
        // lands on the chart's real corner instead of the viewport's. A plain
        // inner div gives each element its own job.
        const inner = document.createElement("div");
        if (old) {
            el.style.position = "relative";
            inner.style.cssText = "position:absolute;top:0;left:0;width:100%;visibility:hidden";
        }
        el.appendChild(inner);

        // Bound inputs (the harness/statistic dropdowns) are chart state, not
        // page state: re-embedding builds a brand new view that starts at each
        // param's declared default. Carry the current values over so switching
        // theme doesn't silently reset the reader's selection.
        const carried = {};
        if (oldView && el._params) el._params.forEach(n => {
            try { carried[n] = oldView.signal(n); } catch (e) {}
        });

        loadSpec(src)
            .then(raw => {
                // resolvePalette deep-copies, so the cached spec is never touched
                const spec = rebaseDataUrls(resolvePalette(raw, el));
                el._params = (spec.params || []).filter(p => p.bind).map(p => p.name);
                L("spec keys:", Object.keys(spec).join(","), " data.url=", spec.data && spec.data.url);
                if (!VERBOSE) return spec;
                return fetch(spec.data.url)
                    .then(r => { L("data fetch:", r.status, spec.data.url); return r.ok ? r.json() : Promise.reject(new Error("HTTP " + r.status + " " + spec.data.url)); })
                    .then(rows => {
                        L("data rows:", rows.length, " sample=", JSON.stringify(rows[0]));
                        L("distinct harness values:", [...new Set(rows.map(r => r.harness))]);
                        return spec;
                    });
            })
            .then(spec => {
                spec = patchShapeLegend(spec, el);
                if (isMobile()) {
                    spec = applyMobileParams(spec);
                    spec = stackFacets(spec);
                    spec = patchLegendsForMobile(spec);
                    spec = applyMinMobileWidth(spec, el);
                    L("mobile: legends moved to bottom, width=", spec.width);
                }
                if (!canHover()) {
                    spec = stripTooltips(spec);
                    L("no hover available: tooltips stripped");
                }
                if (spec._fitPanels) {
                    spec = fitPanels(spec, el);
                    el._fitWidth = el.offsetWidth;
                    L("facet fitted to container:", el._fitWidth, "-> panel width", spec.spec.width);
                }
                delete spec._minMobileWidth;
                delete spec._fitPanels;
                delete spec._mobileStack;
                delete spec._panelBleed;
                delete spec._mobileParams;
                if (VERBOSE && typeof vegaLite !== "undefined" && vegaLite.compile) {
                    try { const c = vegaLite.compile(spec); L("vl.compile OK; vega marks:", (c.spec.marks || []).length); }
                    catch (e) { E("vl.compile FAILED:", e.message); throw e; }
                }
                registerSchemes();
                // tooltip: the second half of stripTooltips - see there.
                return vegaEmbed(inner, spec, {
                    config: theme(el), renderer: "svg", logLevel: VERBOSE ? 3 : 1,
                    tooltip: canHover(),
                    actions: { export: true, source: false, compiled: false, editor: false }
                });
            })
            .then(res => {
                Object.keys(carried).forEach(n => {
                    try { res.view.signal(n, carried[n]); } catch (e) { W("could not restore", n, e.message); }
                });
                if (Object.keys(carried).length) res.view.run();

                if (old) {
                    if (oldView) { try { oldView.finalize(); } catch (e) {} }
                    old.remove();
                    inner.removeAttribute("style");
                    el.style.position = "";
                }
                el._view = res.view;
                live.add(el);
                observe(el);
                L("embed resolved");
                if (VERBOSE) inspect(el, res.view);
            })
            .catch(err => fail(el, "Figure failed: " + (err && err.message ? err.message : err), err));
    };

    // nav.js navigates by replacing the panel's markup, which throws away the
    // old page's figures without telling anyone. Their Vega views would go on
    // holding datasets, listeners and a ResizeObserver each, so tear down
    // anything that is no longer in the document before drawing the new page.
    const live = new Set();
    const sweep = () => live.forEach((el) => {
        if (el.isConnected) return;
        if (el._view) { try { el._view.finalize(); } catch (e) {} el._view = null; }
        if (el._ro) { try { el._ro.disconnect(); } catch (e) {} el._ro = null; }
        live.delete(el);
    });

    const renderAll = () => {
        sweep();
        const els = document.querySelectorAll("[data-vega]");
        if (!els.length) return;
        L("found", els.length, "figure(s)");
        ensureLibs()
            .then(() => els.forEach(render))
            .catch(err => els.forEach(el => fail(el, "Figure failed: " + err.message, err)));
    };

    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", renderAll);
    else renderAll();
    document.addEventListener("content:swapped", renderAll);

    // Axis, legend and title colours follow the theme from CSS and need no
    // help here. This re-render is for what CSS cannot reach: the colour
    // scales the marks are drawn from (--cat-* and --seq-*), which are baked
    // into the view when it is compiled. theme.js flips a class and the
    // attribute in the same tick, so coalesce the burst into one render.
    let themeRender;
    new MutationObserver(m => {
        if (!m.some(x => x.attributeName === "data-theme")) return;
        clearTimeout(themeRender);
        themeRender = setTimeout(renderAll, 50);
    }).observe(document.documentElement, { attributes: true });
})();
