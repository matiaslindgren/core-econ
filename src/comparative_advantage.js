const data = {
  greta: {
    apples: {
      max: 1250,
      consume: 500,
      initExport: 0,
    },
    wheat: {
      max: 50,
      consume: 30,
      initExport: 15,
    },
  },
  carlos: {
    apples: {
      max: 1000,
      consume: 300,
      initExport: 600,
    },
    wheat: {
      max: 20,
      consume: 14,
      initExport: 0,
    },
  },
  emoji: {
    dead: "&#x1F480;",
    neutral: "&#x1F610;",
    happy: "&#x1F60A;",
  },
};

function applesPerWheat() {
  return parseInt(document.getElementById("wheat-to-apples-xrate").value);
}

function getMaxProd(who) {
  const d = data[who.toLowerCase()];
  return tableRow([who, d.apples.max, "or", d.wheat.max, (d.apples.max / d.wheat.max).toFixed(0)]);
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
    if (typeof x === "number") {
      div.classList.add("number");
    }
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
  };
}

function updateInput(id, values) {
  const input = document.getElementById(id);
  for (const key in values) {
    if (typeof key !== "undefined") {
      input[key] = values[key];
    }
  }
  input.nextSibling.innerHTML = input.value;
}

function updateState({ applyConstraints, skipId }) {
  const format = (x) => (typeof x === "number" ? x.toFixed(1) : x);
  const update = (id, values) => {
    if (id === skipId) {
      return;
    }
    const input = document.getElementById(id);
    if (input.tagName === "INPUT") {
      updateInput(id, values);
    } else {
      input.innerHTML = format(values.value);
      if (input.classList.contains("balance")) {
        input.classList.remove("negative");
        input.classList.remove("positive");
        if (values.value >= 0.05) {
          input.classList.add("positive");
        } else if (values.value <= -0.05) {
          input.classList.add("negative");
        }
      }
    }
  };
  const updateFace = ({ faceId, balance }) => {
    let face;
    if (balance < 0) {
      face = data.emoji.dead;
    } else if (balance === 0) {
      face = data.emoji.neutral;
    } else {
      face = data.emoji.happy;
    }
    document.getElementById(faceId).innerHTML = face;
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
  let g_ae = getInput("greta-apples-export");
  let g_wp = getInput("greta-wheat-produce");
  let g_we = getInput("greta-wheat-export");

  let c_ap = getInput("carlos-apples-produce");
  let c_ae = getInput("carlos-apples-export");
  let c_wp = getInput("carlos-wheat-produce");
  let c_we = getInput("carlos-wheat-export");

  if (applyConstraints) {
    g_ap = balanceProduction(g_ap, g_wp);
    g_wp = balanceProduction(g_wp, g_ap);
    g_ae = exchange(g_ap, g_ae, c_wp, c_we, applesPerWheat());
    g_we = exchange(g_wp, g_we, c_ap, c_ae, 1 / applesPerWheat());

    c_ap = balanceProduction(c_ap, c_wp);
    c_wp = balanceProduction(c_wp, c_ap);
    c_ae = exchange(c_ap, c_ae, g_wp, g_we, applesPerWheat());
    c_we = exchange(c_wp, c_we, g_ap, g_ae, 1 / applesPerWheat());
  }

  // Compute balance
  const g_ab = {
    value: g_ap.value + c_ae.value - g_ae.value - data.greta.apples.consume,
  };
  const g_wb = {
    value: g_wp.value + c_we.value - g_we.value - data.greta.wheat.consume,
  };

  const c_ab = {
    value: c_ap.value + g_ae.value - c_ae.value - data.carlos.apples.consume,
  };
  const c_wb = {
    value: c_wp.value + g_we.value - c_we.value - data.carlos.wheat.consume,
  };

  // Update state
  update("greta-apples-produce", g_ap);
  update("greta-apples-export", g_ae);
  update("greta-apples-import", c_ae);
  update("greta-apples-balance", g_ab);
  update("greta-wheat-produce", g_wp);
  update("greta-wheat-export", g_we);
  update("greta-wheat-import", c_we);
  update("greta-wheat-balance", g_wb);

  update("carlos-apples-produce", c_ap);
  update("carlos-apples-export", c_ae);
  update("carlos-apples-import", g_ae);
  update("carlos-apples-balance", c_ab);
  update("carlos-wheat-produce", c_wp);
  update("carlos-wheat-export", c_we);
  update("carlos-wheat-import", g_we);
  update("carlos-wheat-balance", c_wb);

  updateFace({ faceId: "greta-state", balance: Math.min(g_ab.value, g_wb.value) });
  updateFace({ faceId: "carlos-state", balance: Math.min(c_ab.value, c_wb.value) });
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
    updateState({ applyConstraints: true, skipId: id });
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

function button(label, onclick) {
  const btn = document.createElement("button");
  btn.innerText = label;
  btn.onclick = onclick;
  return btn;
}

function main() {
  let e = document.querySelector("#table-max-production tbody");
  e.innerHTML = "";
  e.appendChild(tableRow(["", "Apples", "", "Wheat (tons)", "Apples / Wheat"]));
  e.appendChild(getMaxProd("Greta"));
  e.appendChild(getMaxProd("Carlos"));

  const applesStep = 5;
  const wheatStep = 0.02;
  e = document.querySelector("#grid-input");
  e.innerHTML = "";
  const headerRow = ["", "", "", "Produce", "Export", "Import", "Consume", "Balance"];
  const emptyRow = Array.from(headerRow, () => "");
  addGridRow(e, headerRow);
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
      id: "greta-apples-export",
      min: 0,
      max: 0,
      step: applesStep,
      init: 0,
    }),
    spanWithId("greta-apples-import"),
    -data.greta.apples.consume,
    spanWithId("greta-apples-balance", "balance"),
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
      id: "greta-wheat-export",
      min: 0,
      max: data.greta.wheat.max,
      step: wheatStep,
      init: data.greta.wheat.initExport,
    }),
    spanWithId("greta-wheat-import"),
    -data.greta.wheat.consume,
    spanWithId("greta-wheat-balance", "balance"),
  ]);
  addGridRow(e, emptyRow);
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
      id: "carlos-apples-export",
      min: 0,
      max: data.carlos.apples.max,
      step: applesStep,
      init: data.carlos.apples.initExport,
    }),
    spanWithId("carlos-apples-import"),
    -data.carlos.apples.consume,
    spanWithId("carlos-apples-balance", "balance"),
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
      id: "carlos-wheat-export",
      min: 0,
      max: data.carlos.wheat.max,
      step: wheatStep,
      init: 0,
    }),
    spanWithId("carlos-wheat-import"),
    -data.carlos.wheat.consume,
    spanWithId("carlos-wheat-balance", "balance"),
  ]);
  addGridRow(e, emptyRow);
  addGridRow(e, [
    "",
    "",
    "",
    button("Total autarky", (_) => {
      updateInput("greta-apples-produce", { value: data.greta.apples.consume });
      updateInput("greta-apples-export", { value: 0 });
      updateInput("greta-wheat-produce", { value: data.greta.wheat.consume });
      updateInput("greta-wheat-export", { value: 0 });
      updateInput("carlos-apples-produce", { value: data.carlos.apples.consume });
      updateInput("carlos-apples-export", { value: 0 });
      updateInput("carlos-wheat-produce", { value: data.carlos.wheat.consume });
      updateInput("carlos-wheat-export", { value: 0 });
      updateState({ applyConstraints: false, skipId: null });
    }),
    button("Full specialization", (_) => {
      updateInput("greta-apples-produce", { value: 0 });
      updateInput("greta-apples-export", { value: data.greta.apples.initExport });
      updateInput("greta-wheat-produce", { value: data.greta.wheat.max });
      updateInput("greta-wheat-export", { value: data.greta.wheat.initExport });
      updateInput("carlos-apples-produce", { value: data.carlos.apples.max });
      updateInput("carlos-apples-export", { value: data.carlos.apples.initExport });
      updateInput("carlos-wheat-produce", { value: 0 });
      updateInput("carlos-wheat-export", { value: data.carlos.wheat.initExport });
      updateState({ applyConstraints: false, skipId: null });
      updateState({ applyConstraints: true, skipId: null });
    }),
    "",
    "",
  ]);

  const applyNewRates = document.getElementById("xrate-apply");
  const updateAll = (_) => {
    updateState({ applyConstraints: true, skipId: null });
    applyNewRates.disabled = true;
  };
  applyNewRates.onclick = updateAll;
  document.getElementById("wheat-to-apples-xrate").oninput = (_) => {
    applyNewRates.disabled = false;
  };
  updateAll(null);
}

window.addEventListener("DOMContentLoaded", main);
