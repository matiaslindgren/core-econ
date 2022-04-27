function chooseRandom(a) {
  return a[Math.floor(Math.random() * a.length)];
}

function create(tag, cls, text) {
  const e = document.createElement(tag);
  if (cls) {
    e.classList.add(cls);
  }
  if (text) {
    e.innerText = text;
  }
  return e;
}

function randomizeEmojis() {
  const emojis = [
    "&#x1F468;",
    "&#x1F469;",
    "&#x1F471;",
    "&#x1F474;",
    "&#x1F475;",
    "&#x1F9D1;",
    "&#x1F9D3;",
    "&#x1F9D4;",
  ];
  const skinColors = ["&#x1F3FB;", "&#x1F3FC;", "&#x1F3FD;", "&#x1F3FE;", "&#x1F3FF;"];
  const emojiSpans = document.querySelectorAll("form.vega-bindings .vega-bind span.emoji");
  for (const span of emojiSpans) {
    span.innerHTML = chooseRandom(emojis) + chooseRandom(skinColors);
  }
}

// https://stackoverflow.com/a/36481059/5951112
// Standard Normal variate using Box-Muller transform.
function randn_bm() {
  let u = 0;
  let v = 0;
  while (u === 0) u = Math.random(); //Converting [0,1) to (0,1)
  while (v === 0) v = Math.random();
  return Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
}

function inputs() {
  return document.querySelectorAll("form.vega-bindings .vega-bind input[type='range']");
}

function randomizeIncomes() {
  for (const input of inputs()) {
    input.value = Math.min(100, Math.max(1, 20 * (2 + randn_bm())));
    input.dispatchEvent(new Event("change"));
  }
}

function sortInputsByIncome() {
  let rows = Array.from(inputs(), (x) => x.parentElement.parentElement);
  const inputValue = (row) => parseFloat(row.querySelector("label input[type='range']").value);
  rows = rows.sort((a, b) => inputValue(b) - inputValue(a));
  for (const row of rows) {
    row.parentElement.appendChild(row);
  }
}

function main() {
  const inputForm = document.querySelector("form.vega-bindings");

  const topLabel = create("label", "inputs-header");
  topLabel.appendChild(create("span", "vega-bind-name", "Person"));
  topLabel.appendChild(create("span", null, "Income"));
  const topRow = create("div", "vega-bind");
  topRow.appendChild(topLabel);
  inputForm.insertBefore(topRow, inputForm.firstChild);

  const inputNames = document.querySelectorAll("form.vega-bindings .vega-bind span.vega-bind-name");
  for (const name of inputNames) {
    if (/^person_\d+:$/.test(name.innerText)) {
      name.classList.add("emoji");
    }
  }
  randomizeEmojis();

  const randomizeButton = create("button", "randomize-button", "Randomize");
  randomizeButton.onclick = (e) => {
    randomizeEmojis();
    randomizeIncomes();
    sortInputsByIncome();
    e.preventDefault();
  };
  const bottomRow = create("div", "vega-bind");
  bottomRow.appendChild(randomizeButton);
  inputForm.appendChild(bottomRow);
}

window.addEventListener("DOMContentLoaded", main);
