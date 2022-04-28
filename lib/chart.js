function renderTooltip(event, value, config) {
  const tooltipContainer = document.getElementById("custom-tooltip-element");
  tooltipContainer.classList.add("visible");
  if (!value) {
    tooltipContainer.classList.remove("visible");
    return;
  }
  tooltipContainer.setAttribute(
    "style",
    `top: ${event.clientY + 15}px; left: ${event.clientX + 15}px`
  );
  const colorScheme = vega.scheme(findScheme(spec));
  let { datatype, title, ...values } = value;
  values = Array.from(Object.keys(values), (key, i) => ({
    key: key,
    val: values[key],
    color: colorScheme[i],
  }));
  values.sort((a, b) => parseFloat(b.val) - parseFloat(a.val));
  const fmt = getFormatter(config.formatter[datatype]);
  tooltipContainer.innerHTML = sortedTable(title, values, fmt).outerHTML;
}

function getFormatter({ name, digits }) {
  const currency = (c) =>
    Intl.NumberFormat("en-US", {
      maximumSignificantDigits: digits,
      style: "currency",
      currency: c,
    });
  const unit = (u) =>
    Intl.NumberFormat("en-US", { maximumSignificantDigits: digits, style: "unit", unit: u });
  switch (name) {
    case "hour":
      return unit("hour");
    case "USD":
    default:
      return currency("USD");
  }
}

function svgCircle(color) {
  return [
    `<svg style="display: table-cell; height: 1em; width: 1em; fill: ${color};" viewBox="0 0 2 2" xmlns="http://www.w3.org/2000/svg">`,
    `<circle cx="1.1" cy="1.1" r="0.8"/>`,
    `</svg>`,
  ].join("\n");
}

const element = (tag) => document.createElement(tag);

function findScheme(spec) {
  for (const layer of spec.hconcat || spec.vconcat || spec.layer) {
    const scheme =
      layer &&
      layer.encoding &&
      layer.encoding.color &&
      layer.encoding.color.scale &&
      layer.encoding.color.scale.scheme;
    if (scheme) {
      return scheme;
    }
  }
  return "tableau10";
}

function sortedTable(title, values, fmt) {
  const container = element("div");
  const header = element("h4");
  header.setAttribute("style", "margin: 0 auto 0.5em;");
  header.innerText = title;
  container.appendChild(header);
  const tbody = element("tbody");
  for (let row of values) {
    const tr = element("tr");
    tr.innerHTML = [
      `<td>${svgCircle(row.color)}</td>`,
      `<td>${row.key}</td>`,
      `<td>${fmt.format(row.val)}</td>`,
    ].join("\n");
    tbody.appendChild(tr);
  }
  const table = element("table");
  table.classList.add("tooltip");
  table.appendChild(tbody);
  container.appendChild(table);
  return container;
}

let vegaView;

function buildChart(spec, options) {
  vegaEmbed("#vega-container", spec, options)
    .then((result) => {
      vegaView = result.view;
      const meta = spec.usermeta;
      if (!meta) {
        return;
      }
      if (meta.inputsOnTop) {
        const bindings = document.querySelector("#vega-container.vega-embed form.vega-bindings");
        const canvas = document.querySelector("#vega-container.vega-embed canvas");
        canvas.parentNode.insertBefore(bindings, canvas);
      }
      if (meta.customTooltip) {
        result.view.tooltip((handler, event, item, value) =>
          renderTooltip(event, value, meta.customTooltip)
        );
      }
      return result.view.runAsync();
    })
    .catch(console.error);
}
