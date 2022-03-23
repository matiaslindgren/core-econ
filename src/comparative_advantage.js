const data = {
  greta: {
    apples: {
      max: 1250,
      consume: 500,
    },
    wheat: {
      max: 50,
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
      consume: 14,
    },
  },
};

const applesPerWheat = 40;

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

function updateState({ skipId }) {
  const format = (x) => (typeof x === "number" ? x.toFixed(1) : x);
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
      input.innerHTML = format(values.value);
      if (input.classList.contains("total")) {
        input.classList.remove("negative");
        input.classList.remove("positive");
        if (values.value > 0) {
          input.classList.add("positive");
        } else if (values.value < 0) {
          input.classList.add("negative");
        }
      }
    }
  };
  const updateFace = ({ id, isDead }) => {
    const face = document.getElementById(id);
    face.innerHTML = isDead ? "&#x1F480;" : "&#x1F60A;";
  };
  const balanceProduction = (a, b) => {
    if (a.id === skipId) {
      return a;
    }
    return Object.assign(a, {
      value: a.max * (1 - b.value / b.max),
    });
  };
  const exchange = (aProd, aExport, bProd, bExport, rate) => {
    if (aExport.id === skipId) {
      return aExport;
    }
    return Object.assign(aExport, {
      value: Math.min(aProd.value, rate * bExport.value),
      max: Math.min(aProd.value, rate * bProd.value),
    });
  };

  // Get current state
  let g_ap = getInput("greta-apples-produce");
  let g_wp = getInput("greta-wheat-produce");
  let g_ae = getInput("greta-apples-exchange");
  let g_we = getInput("greta-wheat-exchange");
  let c_ap = getInput("carlos-apples-produce");
  let c_wp = getInput("carlos-wheat-produce");
  let c_ae = getInput("carlos-apples-exchange");
  let c_we = getInput("carlos-wheat-exchange");

  // Apply constraints to state
  g_ap = balanceProduction(g_ap, g_wp);
  g_wp = balanceProduction(g_wp, g_ap);
  g_ae = exchange(g_ap, g_ae, c_wp, c_we, applesPerWheat);
  g_we = exchange(g_wp, g_we, c_ap, c_ae, 1 / applesPerWheat);
  c_ap = balanceProduction(c_ap, c_wp);
  c_wp = balanceProduction(c_wp, c_ap);
  c_ae = exchange(c_ap, c_ae, g_wp, g_we, applesPerWheat);
  c_we = exchange(c_wp, c_we, g_ap, g_ae, 1 / applesPerWheat);

  // Compute totals
  const g_at = {
    value: g_ap.value + c_ae.value - g_ae.value - data.greta.apples.consume,
  };
  const g_wt = {
    value: g_wp.value + c_we.value - g_we.value - data.greta.wheat.consume,
  };
  const c_at = {
    value: c_ap.value + g_ae.value - c_ae.value - data.carlos.apples.consume,
  };
  const c_wt = {
    value: c_wp.value + g_we.value - c_we.value - data.carlos.wheat.consume,
  };

  // Update state
  update("greta-apples-produce", g_ap);
  update("greta-wheat-produce", g_wp);
  update("greta-apples-exchange", g_ae);
  update("greta-wheat-exchange", g_we);
  update("greta-apples-total", g_at);
  update("greta-wheat-total", g_wt);
  update("carlos-apples-produce", c_ap);
  update("carlos-wheat-produce", c_wp);
  update("carlos-apples-exchange", c_ae);
  update("carlos-wheat-exchange", c_we);
  update("carlos-apples-total", c_at);
  update("carlos-wheat-total", c_wt);
  updateFace({ id: "greta-state", isDead: g_at.value < 0 || g_wt.value < 0 });
  updateFace({ id: "carlos-state", isDead: c_at.value < 0 || c_wt.value < 0 });
}

function rangeInput({ id, min, max, step, init }) {
  const input = document.createElement("input");
  input.type = "range";
  input.id = id;
  input.step = step;
  input.min = min;
  input.max = max;
  input.value = init;
  const value = document.createElement("span");
  value.innerHTML = init;
  input.oninput = (e) => {
    value.innerHTML = e.target.value;
    updateState({ skipId: id });
  };
  const container = document.createElement("span");
  container.appendChild(input);
  container.appendChild(value);
  return container;
}

function spanWithId(id, className) {
  const span = document.createElement("span");
  span.id = id;
  if (className) {
    span.classList.add(className);
  }
  return span;
}

function main() {
  let e = document.querySelector("#table-max-production tbody");
  e.innerHTML = "";
  e.appendChild(tableRow(["", "Apples", "Wheat (tons)", "Apples / Wheat"]));
  e.appendChild(getMaxProd("Greta"));
  e.appendChild(getMaxProd("Carlos"));

  const applesStep = 1;
  const wheatStep = Math.min(
    data.greta.wheat.max / data.greta.apples.max,
    data.carlos.wheat.max / data.carlos.apples.max
  );
  e = document.querySelector("#grid-input");
  e.innerHTML = "";
  addGridRow(e, ["", "", "", "Produce", "Exchange", "Consume", "Total"]);
  addGridRow(e, [
    "Greta",
    spanWithId("greta-state"),
    "Apples",
    rangeInput({
      id: "greta-apples-produce",
      min: 0,
      max: data.greta.apples.max,
      step: applesStep,
      init: 0,
    }),
    rangeInput({
      id: "greta-apples-exchange",
      min: 0,
      max: 0,
      step: applesStep,
      init: 0,
    }),
    -data.greta.apples.consume,
    spanWithId("greta-apples-total", "total"),
  ]);
  addGridRow(e, [
    "",
    "",
    "Wheat",
    rangeInput({
      id: "greta-wheat-produce",
      min: 0,
      max: data.greta.wheat.max,
      step: wheatStep,
      init: data.greta.wheat.max,
    }),
    rangeInput({
      id: "greta-wheat-exchange",
      min: 0,
      max: 15,
      step: wheatStep,
      init: 15,
    }),
    -data.greta.wheat.consume,
    spanWithId("greta-wheat-total", "total"),
  ]);
  addGridRow(e, [
    "Carlos",
    spanWithId("carlos-state"),
    "Apples",
    rangeInput({
      id: "carlos-apples-produce",
      min: 0,
      max: data.carlos.apples.max,
      step: applesStep,
      init: data.carlos.apples.max,
    }),
    rangeInput({
      id: "carlos-apples-exchange",
      min: 0,
      max: data.carlos.apples.max,
      step: applesStep,
      init: 600,
    }),
    -data.carlos.apples.consume,
    spanWithId("carlos-apples-total", "total"),
  ]);
  addGridRow(e, [
    "",
    "",
    "Wheat",
    rangeInput({
      id: "carlos-wheat-produce",
      min: 0,
      max: data.carlos.wheat.max,
      step: wheatStep,
      init: 0,
    }),
    rangeInput({
      id: "carlos-wheat-exchange",
      min: 0,
      max: data.carlos.wheat.max,
      step: wheatStep,
      init: 0,
    }),
    -data.carlos.wheat.consume,
    spanWithId("carlos-wheat-total", "total"),
  ]);

  updateState({ skipId: null });
}

window.addEventListener("DOMContentLoaded", main);
