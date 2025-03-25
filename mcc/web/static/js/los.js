const CLASS_FOR_LEVEL = ["danger", "success", "info", "warning"];
const FILE_TYPES = ["NetCDF", "HDF4", "HDF5", "ASCII", "Binary"];

document.addEventListener("DOMContentLoaded", () => {
	fetch("./static/js/LoSDictionary.json")
		.then(response => {
			return response.json();
		})
		.then(json => {
			makeTabs();
			buildPicker(json);
			buildBaseTable(json);
		});
});

function makeTabs() {
	const tabs = document.createElement("ul");
	tabs.className = "nav nav-tabs nav-justified";
	tabs.id = "los-tabs";
	[
		["Find a Level of Service", "los-picker"],
		["Levels of Service Matrix", "los-matrix"]
	].forEach((item, idx) => {
		const title = item[0];
		const tabInner = document.createElement("a");
		tabInner.innerHTML = title;
		tabInner.classList.add("nav-link");
		tabInner.setAttribute("data-tab", item[1]);
		if (!idx) tabInner.classList.add("active");

		const tab = document.createElement("li");
		tab.className = "nav-item";

		tab.appendChild(tabInner);
		tabs.appendChild(tab);
	});
	tabs.addEventListener("click", handleTabClick);
	document.getElementById("los-container").appendChild(tabs);
}

function buildPicker(json, legend) {
	const container = document.createElement("div");
	container.id = "los-picker";
	container.className = "tab-content";

	const heading = document.createElement("div");
	heading.className = "row";
	headingText = document.createElement("h1");
	headingText.innerHTML = "Find a Level of Service";
	heading.appendChild(headingText);
	// container.appendChild(heading);

	const pickerForm = document.createElement("div");
	pickerForm.className = "col-12 picker";

	const pickerButtonsContainer = document.createElement("div");
	pickerButtonsContainer.className = "row";

	const pickerOptions = [
		[FILE_TYPES, "File Type"],
		[[0, 1, 2, 3, 4], "Data Level"]
	];
	pickerOptions.forEach(optionType => {
		const options = optionType[0];
		const optionTitle = optionType[1];

		// Make base picker div
		const picker = document.createElement("div");
		picker.className = "dropdown";

		// Add toggle button
		const toggle = document.createElement("button");
		toggle.className = "btn btn-primary dropdown-toggle";
		toggle.setAttribute("data-toggle", "dropdown");
		toggle.innerHTML = "Pick a " + optionTitle;
		toggle.id = optionTitle
			.toLowerCase()
			.split(" ")
			.join("-");

		// Add menu options
		const dropdownMenu = document.createElement("div");
		dropdownMenu.className = "dropdown-menu";
		options.forEach(item => {
			const option = document.createElement("a");
			option.className = "dropdown-item";
			option.href = "#";
			option.innerHTML = item;
			dropdownMenu.appendChild(option);
		});

		// Put it all together and add event handlers
		picker.append(toggle, dropdownMenu);
		picker.addEventListener("click", evt =>
			handleFileTypeDropdown(evt, json, legend)
		);
		pickerForm.append(picker);
	});
	container.appendChild(pickerForm);

	const divider = document.createElement("hr");
	container.appendChild(divider);

	const resultsContainer = document.createElement("div");
	resultsContainer.id = "results-container";
	resultsContainer.className = "col-12";
	container.appendChild(resultsContainer);

	document.getElementById("los-container").append(container);
}

function buildBaseTable(json) {
	const legend = json.legend;
	const indices = json.indices;

	const container = document.createElement("div");
	container.id = "los-matrix";
	container.className = "tab-content";
	container.hidden = true;

	const tableHeadingDiv = document.createElement("div");
	tableHeadingDiv.className = "row";
	const tableHeading = document.createElement("h1");
	tableHeading.innerHTML = "Levels of Service Matrix";
	// tableHeadingDiv.appendChild(tableHeading);

	const tableContainer = document.createElement("div");
	tableContainer.className = "row";

	json.sections.forEach((section, idx) => {
		const container = document.createElement("div");
		container.className = "col-12";

		const headingDiv = document.createElement("div");
		headingDiv.className = "row";

		const heading = document.createElement("h3");
		heading.innerHTML = section.title;
		headingDiv.appendChild(heading);
		if (idx) container.appendChild(document.createElement("hr"));
		container.appendChild(headingDiv);

		const sections = document.createElement("div");
		section.services.forEach(service => {
			sections.appendChild(buildService(service, legend, indices));
		});

		container.appendChild(sections);

		tableContainer.appendChild(container);
	});

	container.append(tableHeadingDiv, tableContainer);
	document.getElementById("los-container").append(container);
}

function buildService(service, legend, indices) {
	const containerName = service.service.split(" ").join("_");

	const container = document.createElement("div");
	container.className = "row";

	const heading = document.createElement("h5");

	const toggleButton = document.createElement("button");
	toggleButton.setAttribute("type", "button");
	toggleButton.setAttribute("data-target-dropdown", containerName);
	toggleButton.className = "btn btn-outline-secondary";
	toggleButton.innerHTML = "Show";
	toggleButton.addEventListener("click", toggleDropdown);

	heading.appendChild(toggleButton);
	heading.appendChild(document.createTextNode(service.service));

	container.appendChild(heading);

	const table = document.createElement("table");
	table.id = containerName;
	table.className = "table los-table";
	table.hidden = true;

	const headerRow = document.createElement("tr");
	fileTypeHeader = document.createElement("th");
	fileTypeHeader.innerHTML = "File Type";
	headerRow.append(fileTypeHeader);
	indices.forEach(index => {
		const cell = document.createElement("th");
		cell.innerHTML = index.charAt(0).toUpperCase() + index.slice(1);
		headerRow.append(cell);
	});

	table.appendChild(headerRow);

	FILE_TYPES.forEach(fileType => {
		table.appendChild(makeFileFormatRow(service, fileType, legend));
	});

	container.appendChild(table);

	return container;
}

function makeFileFormatRow(service, fileType, legend) {
	const row = document.createElement("tr");

	const serviceName = document.createElement("th");
	serviceName.setAttribute("scope", "row");
	serviceName.innerHTML = fileType;
	row.appendChild(serviceName);
	service[fileType].forEach(level => {
		const cell = document.createElement("td");
		cell.className = "table-" + CLASS_FOR_LEVEL[level];
		cell.innerHTML = legend[level];
		row.appendChild(cell);
	});
	return row;
}

function toggleDropdown(evt) {
	evt.target.classList.toggle("active");
	const targetDropdown = document.getElementById(
		evt.target.dataset.targetDropdown
	);
	targetDropdown.hidden = !targetDropdown.hidden;
	evt.target.innerHTML = targetDropdown.hidden ? "Show" : "Hide";
}

function handleFileTypeDropdown(evt, json) {
	if (evt.target.classList.contains("dropdown-toggle")) {
		const currentDropdown = evt.currentTarget.querySelector(
			"div.dropdown-menu"
		);

		evt.currentTarget.parentElement
			.querySelectorAll("div.dropdown-menu")
			.forEach(dd => {
				if (dd === currentDropdown) {
					return dd.classList.toggle("show");
				}
				dd.classList.remove("show");
			});
	}

	if (evt.target.classList.contains("dropdown-item")) {
		evt.currentTarget
			.querySelector(".dropdown-menu")
			.classList.remove("show");
		evt.currentTarget.querySelector("button").innerHTML =
			evt.target.innerHTML;
		updatePicker(json);
	}
}

function updatePicker(json) {
	const pickerDiv = document.getElementById("los-picker");

	// Do nothing if the user hasn't selected something for all fields
	if (
		[...pickerDiv.querySelectorAll("button")].some(button =>
			button.innerHTML.startsWith("Pick a")
		)
	)
		return;

	// Empty out the previous results
	const resultsContainer = document.getElementById("results-container");
	while (resultsContainer.firstChild) {
		resultsContainer.removeChild(resultsContainer.firstChild);
	}

	// Get the selected values
	const selectedFileType = document.getElementById("file-type").innerHTML;
	const selectedLevel = document.getElementById("data-level").innerHTML;

	// Draw the results into a table
	json.sections.forEach(section => {
		const headerContainer = document.createElement("div");
		headerContainer.className = "row";
		const headerText = document.createElement("h3");
		headerText.innerHTML = section.title;
		headerContainer.appendChild(headerText);

		const sectionContainer = document.createElement("div");
		sectionContainer.className = "row";

		const resultsTable = document.createElement("table");
		resultsTable.className = "table";

		const headerRow = document.createElement("tr");
		["Service", "Level"].forEach(col => {
			const cell = document.createElement("th");
			cell.innerHTML = col;
			headerRow.appendChild(cell);
		});

		section.services.forEach(service => {
			const row = document.createElement("tr");

			const serviceCell = document.createElement("td");
			serviceCell.innerHTML = service.service;

			const levelOfService = service[selectedFileType][selectedLevel];
			const levelOfServiceCell = document.createElement("td");
			levelOfServiceCell.innerHTML = json.legend[levelOfService];
			levelOfServiceCell.className =
				"table-" + CLASS_FOR_LEVEL[levelOfService];

			row.append(serviceCell, levelOfServiceCell);
			resultsTable.append(row);
		});

		sectionContainer.appendChild(resultsTable);
		resultsContainer.append(headerContainer, sectionContainer);
	});
}

function handleTabClick(evt) {
	document
		.getElementById("los-tabs")
		.querySelectorAll("a")
		.forEach(tab => {
			if (tab === evt.target) {
				tab.classList.add("active");
				document.getElementById(evt.target.dataset.tab).hidden = false;
				return;
			}
			tab.classList.remove("active");
			document.getElementById(tab.dataset.tab).hidden = true;
		});
	document
		.querySelectorAll("div.dropdown-menu")
		.forEach(dd => dd.classList.remove("show"));
}
