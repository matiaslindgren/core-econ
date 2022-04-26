function main() {
  for (const e of document.querySelectorAll("span.katex-inline")) {
    katex.render(e.innerText, e);
    e.classList.remove("katex-inline");
  }
  for (const e of document.querySelectorAll("span.katex-display")) {
    katex.render(e.innerText, e, { displayMode: true });
    e.classList.remove("katex-display");
  }
}

window.addEventListener("DOMContentLoaded", main);
