function handleTooltip(_, event, _, value) {
  const tooltipContainer = document.getElementById("custom-tooltip-element");
  tooltipContainer.classList.add("visible");
  if (!value) {
    tooltipContainer.classList.remove("visible");
    return;
  }
  tooltipContainer.setAttribute("style", `top: ${event.clientY}px; left: ${event.clientX}px`);
  const colorScheme = vega.scheme(findScheme(spec));
  let { title, ...values } = value;
  values = Array.from(Object.keys(values), (key, i) => ({
    key: key,
    val: values[key],
    color: colorScheme[i],
  }));
  values.sort((a, b) => parseFloat(b.val) - parseFloat(a.val));
  tooltipContainer.innerHTML = sortedTable(title, values).outerHTML;
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
  for (const layer of spec.layer) {
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

function sortedTable(title, values) {
  const container = element("div");
  const header = element("h4");
  header.setAttribute("style", "margin: 0 auto 0.5em;");
  header.innerText = title;
  container.appendChild(header);
  const tbody = element("tbody");
  const fmt = Intl.NumberFormat("en-US", {
    maximumSignificantDigits: 4,
    style: "currency",
    currency: "USD",
  });
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

function buildChart(spec, options, useCustomTooltip) {
  vegaEmbed("#vega-container", spec, options)
    .then((result) => {
      const bindings = document.querySelector("#vega-container.vega-embed form.vega-bindings");
      const canvas = document.querySelector("#vega-container.vega-embed canvas");
      canvas.parentNode.insertBefore(bindings, canvas);
      if (useCustomTooltip) {
        result.view.tooltip(handleTooltip);
      }
      return result.view.runAsync();
    })
    .catch(console.error);
}
