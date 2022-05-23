function main() {
  for (const e of document.querySelectorAll(".equations span.kx")) {
    katex.render(e.innerText, e);
    e.classList.remove("kx");
  }
}

window.addEventListener("DOMContentLoaded", main);
