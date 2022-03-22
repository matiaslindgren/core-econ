const data = {
  greta: {
    apples: {
      max: 1200,
      consume: 600,
    },
    wheat: {
      max: 60,
      consume: 30,
    },
  },
  carlos: {
    apples: {
      max: 1000,
      consume: 300,
    },
    wheat: {
      max: 20,
      consume: 10,
    },
  },
};

const applesPerWheat = (d) => d.apples.max / d.wheat.max;

function getMaxProd(who) {
  const d = data[who.toLowerCase()];
  return tableRow([
    who,
    d.apples.max,
    d.wheat.max,
    (d.apples.max / d.wheat.max).toFixed(0),
  ]);
}

function tableRow(row) {
  const tr = document.createElement("tr");
  for (let x of row) {
    const td = document.createElement("td");
    td.innerHTML = x;
    tr.appendChild(td);
  }
  return tr;
}

function addGridRow(e, row) {
  for (let x of row) {
    const div = document.createElement("div");
    div.classList.add("grid-element");
    if (typeof x !== "object") {
      const span = document.createElement("span");
      span.innerHTML = x;
      x = span;
    }
    div.appendChild(x);
    e.appendChild(div);
  }
}

function getInput(id) {
  const input = document.getElementById(id);
  return {
    id: id,
    value: parseFloat(input.value),
    min: parseFloat(input.min),
    max: parseFloat(input.max),
    step: parseFloat(input.step),
  };
}

function updateAll({ skipId }) {
  console.log(skipId);
  const update = (id, values) => {
    if (id === skipId) {
      return;
    }
    const input = document.getElementById(id);
    if (input.tagName === "INPUT") {
      for (const key in values) {
        if (typeof key !== "undefined") {
          input[key] = values[key];
        }
      }
      input.nextSibling.innerHTML = input.value;
    } else {
      input.innerHTML = values.value;
    }
  };
  const constrain = (a, b) => {
    if (a.id === skipId) {
      return a;
    }
    return Object.assign(a, {
      value: Math.round(a.max * (1 - b.value / b.max)),
    });
  };
  const max = (a, b) => {
    if (a.id === skipId) {
      return a;
    }
    return Object.assign(a, {
      value: Math.round(Math.min(a.value, b.value)),
      max: Math.round(b.value),
    });
  };

  let g_ap = getInput("greta-apples-produce");
  let g_wp = getInput("greta-wheat-produce");
  g_ap = constrain(g_ap, g_wp);
  g_wp = constrain(g_wp, g_ap);

  let g_ae = getInput("greta-apples-export");
  let g_we = getInput("greta-wheat-export");
  g_ae = max(g_ae, g_ap);
  g_we = max(g_we, g_wp);

  let g_ac = data.greta.apples.consume;
  let g_wc = data.greta.wheat.consume;

  update("greta-apples-produce", g_ap);
  update("greta-wheat-produce", g_wp);
  update("greta-apples-export", g_ae);
  update("greta-wheat-export", g_we);
  update("greta-apples-total", { value: g_ap.value - g_ae.value - g_ac });
  update("greta-wheat-total", { value: g_wp.value - g_we.value - g_wc });
}

function range({ id, min, max, step, init }) {
  const container = document.createElement("span");
  const input = document.createElement("input");
  const value = document.createElement("span");
  input.type = "range";
  input.id = id;
  input.step = step;
  input.min = min;
  input.max = max;
  input.value = init;
  value.innerHTML = init;
  input.oninput = (e) => {
    value.innerHTML = e.target.value;
    updateAll({ skipId: id });
  };
  container.appendChild(input);
  container.appendChild(value);
  return container;
}

function spanWithId(id) {
  const span = document.createElement("span");
  span.id = id;
  return span;
}

function main() {
  let e = document.querySelector("#table-max-production tbody");
  e.innerHTML = "";
  e.appendChild(tableRow(["", "Apples", "Wheat (tons)", "Apples / Wheat"]));
  e.appendChild(getMaxProd("Greta"));
  e.appendChild(getMaxProd("Carlos"));

  e = document.querySelector("#grid-input");
  e.innerHTML = "";
  addGridRow(e, ["", "", "Consume", "Produce", "Export", "Total"]);
  addGridRow(e, [
    "Greta",
    "Apples",
    data.greta.apples.consume,
    range({
      id: "greta-apples-produce",
      min: 0,
      max: data.greta.apples.max,
      step: applesPerWheat(data.greta),
      init: 0,
    }),
    range({
      id: "greta-apples-export",
      min: 0,
      max: 0,
      step: applesPerWheat(data.greta),
      init: 0,
    }),
    spanWithId("greta-apples-total"),
  ]);
  addGridRow(e, [
    "",
    "Wheat",
    data.greta.wheat.consume,
    range({
      id: "greta-wheat-produce",
      min: 0,
      max: data.greta.wheat.max,
      step: 1,
      init: data.greta.wheat.max,
    }),
    range({
      id: "greta-wheat-export",
      min: 0,
      max: 0,
      step: 1,
      init: 0,
    }),
    spanWithId("greta-wheat-total"),
  ]);
  addGridRow(e, [
    "Carlos",
    "Apples",
    data.carlos.apples.consume,
    range({
      id: "carlos-apples-produce",
      min: 0,
      max: data.carlos.apples.max,
      step: applesPerWheat(data.carlos),
      init: data.carlos.apples.max,
    }),
    range({
      id: "carlos-apples-export",
      min: 0,
      max: data.carlos.apples.max,
      step: applesPerWheat(data.carlos),
      init: 0,
    }),
    spanWithId("carlos-apples-total"),
  ]);
  addGridRow(e, [
    "",
    "Wheat",
    data.carlos.wheat.consume,
    range({
      id: "carlos-wheat-produce",
      min: 0,
      max: data.carlos.wheat.max,
      step: 1,
      init: 0,
    }),
    range({
      id: "carlos-wheat-export",
      min: 0,
      max: data.carlos.wheat.max,
      step: 1,
      init: 0,
    }),
    spanWithId("carlos-wheat-total"),
  ]);

  updateAll({ skipId: null });
}

window.addEventListener("DOMContentLoaded", main);
