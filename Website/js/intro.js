(() => {
  const root = document.documentElement;
  if (!root.classList.contains("has-intro")) return;

  const title = document.getElementById("introTitle");
  const name = document.getElementById("introName");
  const target = document.getElementById("topbarName");
  const spacer = document.getElementById("introSpacer");
  const sidebar = document.getElementById("sidebar");
  const topbar = document.querySelector(".topbar");

  let start = null;

  // The intro is done when the content reaches the bottom of the top bar
  function distance() {
    return spacer.offsetHeight - topbar.offsetHeight;
  }

  // -------- Measure --------
  // Measures the name in its resting (centred) position and the top bar target
  function measure() {
    title.style.transform = "";
    root.style.setProperty("--p", "0");

    const box = title.getBoundingClientRect();
    const from = name.getBoundingClientRect();
    const to = target.getBoundingClientRect();
    const fromSize = parseFloat(getComputedStyle(name).fontSize);
    const toSize = parseFloat(getComputedStyle(target).fontSize);

    const originX = from.left + from.width / 2 - box.left;
    const originY = from.top + from.height / 2 - box.top;
    title.style.transformOrigin = `${originX}px ${originY}px`;

    start = {
      dx: to.left + to.width / 2 - (from.left + from.width / 2),
      dy: to.top + to.height / 2 - (from.top + from.height / 2),
      scale: toSize / fromSize,
    };
    update();
  }

  // -------- Animate --------
  function ease(t) {
    return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
  }

  function update() {
    const p = Math.min(Math.max(window.scrollY / distance(), 0), 1);
    const e = ease(p);

    root.style.setProperty("--p", p.toFixed(3));
    root.classList.toggle("intro-done", p >= 1);

    const scale = 1 + (start.scale - 1) * e;
    title.style.transform =
      `translate(-50%, -50%) translate(${start.dx * e}px, ${start.dy * e}px) scale(${scale})`;
  }

  let queued = false;
  window.addEventListener("scroll", () => {
    if (queued) return;
    queued = true;
    requestAnimationFrame(() => {
      queued = false;
      update();
    });
  }, { passive: true });

  window.addEventListener("resize", measure);
  document.fonts.ready.then(measure);
  measure();

  // -------- Keyboard --------
  // Tabbing into the menu while the intro is showing skips straight to the layout
  sidebar.addEventListener("focusin", () => {
    if (window.scrollY < distance()) {
      window.scrollTo({ top: distance(), behavior: "instant" });
    }
  });
})();
