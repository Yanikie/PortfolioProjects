const burger = document.getElementById("navBurger");
const menu = document.getElementById("mobileMenu");

// Foldable mobile menu which also closes
if (burger && menu) {
  burger.addEventListener('click', () => {
    menu.classList.toggle('open');
  });
}
const links = document.querySelectorAll('.mobile-menu__link');

if (links.length) {
  links.forEach(link => {
    link.addEventListener('click', () => {
      if (menu) {
        menu.classList.remove('open');
      }
      links.forEach(l => l.classList.remove('active'));
      link.classList.add('active');
    });
  });
}

links.forEach(link => {
  link.addEventListener("click", () => {
    links.forEach(l => l.classList.remove("active"));
    link.classList.add("active");
  });
});