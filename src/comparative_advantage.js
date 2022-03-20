const data = {
	greta: {
		apples: {
			max: 1250,
			consume: 500,
		},
		corn: {
			max: 50,
			consume: 30,
		},
	},
	carlos: {
		apples: {
			max: 1000,
			consume: 300,
		},
		corn: {
			max: 20,
			consume: 14,
		},
	},
};

const emoji = {
	apples: '&#x1F34E;',
	corn: '&#x1F33D;',
};

function getMaxProd(who) {
	const d = data[who.toLowerCase()];
	return tableRow([who, d.apples.max, d.corn.max, (d.apples.max / d.corn.max).toFixed(0)]);
};

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

function getInt(id) {
	return parseInt(document.getElementById(id).value);
}

function updateAll() {
	const ga_out = getInt("greta-apples-produce");
	const ga_in = getInt("greta-apples-import");
	update("greta-apples-surplus", ga_out + ga_in - data.greta.apples.consume);

	const gc_out = getInt("greta-corn-produce");
	const gc_in = getInt("greta-corn-import");
	update("greta-corn-surplus", gc_out + gc_in - data.greta.corn.consume);

	const ca_out = getInt("carlos-apples-produce");
	const ca_in = getInt("carlos-apples-import");
	update("carlos-apples-surplus", ca_out + ca_in - data.carlos.apples.consume);

	const cc_out = getInt("carlos-corn-produce");
	const cc_in = getInt("carlos-corn-import");
	update("carlos-corn-surplus", cc_out + cc_in - data.carlos.corn.consume);
}

function range(id, min, max, init) {
	const container = document.createElement("span");
	const input = document.createElement("input");
	input.type = "range";
	input.id = id;
	input.min = min;
	input.max = max;
	input.value = init;
	const value = document.createElement("span");
	value.innerHTML = init;
	input.oninput = (e) => {
		value.innerHTML = e.target.value;
		updateAll();
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

function update(id, value) {
	const e = document.getElementById(id);
	e.innerHTML = value;
}

function main() {
	let e = document.querySelector("#table-max-production tbody");
	e.innerHTML = '';
	e.appendChild(tableRow([
		'',
		'Apples (' + emoji.apples + ')',
		'Corn (' + emoji.corn + ')',
		emoji.apples + ' / ' + emoji.corn
	]));
	e.appendChild(getMaxProd('Greta'));
	e.appendChild(getMaxProd('Carlos'));

	e = document.querySelector("#grid-input");
	e.innerHTML = '';
	addGridRow(e, ['', '', 'Consume', 'Produce', 'Import', 'Surplus']);
	addGridRow(e, [
		'Greta',
		emoji.apples,
		data.greta.apples.consume,
		range('greta-apples-produce', 0, data.greta.apples.max, 0),
		range('greta-apples-import', 0, data.carlos.apples.max, 600),
		spanWithId('greta-apples-surplus'),
	]);
	addGridRow(e, [
		'',
		emoji.corn,
		data.greta.corn.consume,
		range('greta-corn-produce', 0, data.greta.corn.max, 50),
		range('greta-corn-import', 0, data.carlos.corn.max, 0),
		spanWithId('greta-corn-surplus'),
	]);
	addGridRow(e, [
		'Carlos',
		emoji.apples,
		data.carlos.apples.consume,
		range('carlos-apples-produce', 0, data.carlos.apples.max, 1000),
		range('carlos-apples-import', 0, data.greta.apples.max, 0),
		spanWithId('carlos-apples-surplus'),
	]);
	addGridRow(e, [
		'',
		emoji.corn,
		data.carlos.corn.consume,
		range('carlos-corn-produce', 0, data.carlos.corn.max, 0),
		range('carlos-corn-import', 0, data.greta.corn.max, 15),
		spanWithId('carlos-corn-surplus'),
	]);

	updateAll();
}

window.addEventListener("DOMContentLoaded", main);
