function main() {
  for (const e of document.querySelectorAll("span.katex-input")) {
    katex.render(e.innerText, e);
    e.classList.remove("katex-input");
  }
}

window.addEventListener("DOMContentLoaded", main);
