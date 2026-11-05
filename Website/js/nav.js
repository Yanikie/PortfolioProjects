(() => {
  const sidebar = document.getElementById("sidebar");
  const button = document.getElementById("menuButton");

  // -------- Mobile drawer --------
  let backdrop = null;

  function setOpen(open) {
    sidebar.classList.toggle("is-open", open);
    button.setAttribute("aria-expanded", String(open));

    if (open) {
      backdrop = document.createElement("div");
      backdrop.className = "backdrop";
      backdrop.addEventListener("click", () => setOpen(false));
      document.body.appendChild(backdrop);
      sidebar.querySelector("a").focus();
    } else if (backdrop) {
      backdrop.remove();
      backdrop = null;
    }
  }

  button.addEventListener("click", () => setOpen(!sidebar.classList.contains("is-open")));

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && sidebar.classList.contains("is-open")) {
      setOpen(false);
      button.focus();
    }
  });

  sidebar.addEventListener("click", (event) => {
    if (event.target.closest("a") && sidebar.classList.contains("is-open")) {
      setOpen(false);
    }
  });

  // -------- Current page --------
  const path = location.pathname.replace(/index\.html$/, "");
  for (const link of sidebar.querySelectorAll("a")) {
    if (link.getAttribute("href") === path && path !== "/") {
      link.setAttribute("aria-current", "page");
    }
  }

  // -------- Active section on the homepage --------
  const sectionLinks = [...sidebar.querySelectorAll('a[href^="/#"]')];
  const sections = sectionLinks
    .map((link) => document.getElementById(link.hash.slice(1)))
    .filter(Boolean);

  if (!sections.length) return;

  function markActive() {
    const atBottom = window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 2;
    const line = window.innerHeight * 0.4;
    let current = null;

    for (const section of sections) {
      if (section.getBoundingClientRect().top <= line) current = section;
    }
    if (atBottom) current = sections[sections.length - 1];

    for (const link of sectionLinks) {
      link.classList.toggle("is-active", current !== null && link.hash === "#" + current.id);
    }
  }

  window.addEventListener("scroll", markActive, { passive: true });
  markActive();
})();
