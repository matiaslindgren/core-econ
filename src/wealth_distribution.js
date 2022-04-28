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
  const people = [
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
    span.innerHTML = chooseRandom(people) + chooseRandom(skinColors);
  }
}

function inputs() {
  return document.querySelectorAll("form.vega-bindings .vega-bind input[type='range']");
}

function randomizeIncomes() {
  for (const input of inputs()) {
    input.value = Math.min(100, Math.max(0, 100 * Math.random()));
    input.dispatchEvent(new Event("change"));
  }
}

function sortInputsByIncome() {
  let rows = Array.from(inputs(), (x) => x.parentElement.parentElement);
  const inputValue = (row) => parseFloat(row.querySelector("label input[type='range']").value);
  rows = rows.sort((a, b) => inputValue(b) - inputValue(a));
  for (const row of rows) {
    row.parentElement.insertBefore(row, row.parentElement.lastChild);
  }
}

function updateGini() {
  vegaView.runAsync().then(() => {
    const gini = vegaView.data("layer_0_layer_0_pathgroup")[0].datum.gini;
    if (!Number.isFinite(gini)) {
      return;
    }
    const fmt = new Intl.NumberFormat("en-US", {
      style: "percent",
      maximumFractionDigits: 1,
    });
    document.getElementById("gini-label").innerText = fmt.format(gini);
  });
}

function main() {
  const inputForm = document.querySelector("form.vega-bindings");

  const topRow = create("div", "vega-bind");
  topRow.innerHTML = `
    <label class='inputs-header'>
      <span class='vega-bind-name'>Person</span>
      <span>Income</span>
    </label>`;
  inputForm.insertBefore(topRow, inputForm.firstChild);

  const vegaContainer = document.getElementById("vega-container");
  const giniContainer = create("div", "gini-container");
  giniContainer.innerHTML = "<span>Gini: </span><span id='gini-label'></span>";
  vegaContainer.insertBefore(giniContainer, vegaContainer.lastChild);

  for (const input of inputs()) {
    const oninput = input.oninput;
    input.oninput = (e) => {
      updateGini();
      e.preventDefault();
      if (oninput) {
        oninput(e);
      }
    };
  }

  const inputNames = document.querySelectorAll("form.vega-bindings .vega-bind span.vega-bind-name");
  for (const name of inputNames) {
    if (/^person_\d+:$/.test(name.innerText)) {
      name.classList.add("emoji");
    }
  }

  const randomizeButton = create("button", "randomize-button", "Randomize");
  randomizeButton.onclick = (e) => {
    randomizeEmojis();
    randomizeIncomes();
    sortInputsByIncome();
    updateGini();
    e.preventDefault();
  };
  const bottomRow = create("div", "vega-bind");
  bottomRow.appendChild(randomizeButton);
  inputForm.appendChild(bottomRow);

  randomizeEmojis();
  updateGini();
}

window.addEventListener("DOMContentLoaded", main);
