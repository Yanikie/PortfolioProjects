const burger = document.getElementById("navBurger");
const menu = document.getElementById("mobileMenu");

// Foldable mobile menu which also closes
burger.addEventListener("click", () => {
  menu.classList.toggle("open");
});
document.querySelectorAll(".mobile-menu__link").forEach(link => {
  link.addEventListener("click", () => {
    menu.classList.remove("open");
  });
});

// Note last clicked button
const links = document.querySelectorAll(".mobile-menu__link");

links.forEach(link => {
  link.addEventListener("click", () => {
    links.forEach(l => l.classList.remove("active"));
    link.classList.add("active");
  });
});