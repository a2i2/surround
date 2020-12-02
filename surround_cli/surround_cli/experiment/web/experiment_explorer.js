function updateMetricColumns(row, table, results) {
    let headerRow = table.rows[0];

    if (results != null) {
        // This loop covers new & existing metrics (exist in other experiments)
        for (var metricName in results.metrics) {
            doesExists = false;

            // If metric in results already present in table, set the correct column
            for (var i = 6; i < headerRow.cells.length; i++) {
                if (headerRow.cells[i].innerHTML == metricName) {
                    row.cells[i].innerHTML = results.metrics[metricName];
                    doesExists = true;
                    break;
                }
            }
            
            // If doesnt exist, add the column to all rows
            if (!doesExists) {
                headerRow.insertAdjacentHTML("beforeEnd", "<th>" + metricName + "</th>");
                document.querySelectorAll("#experiments tbody tr").forEach(row => row.insertCell(-1).innerHTML = "N/A");
            }
        }

        // This loop ensures metrics that exist in other experiments but this one
        for (var i = 6; i < headerRow.cells.length; i++) {
            let alreadyExists = false;

            for (var metricName in results.metrics) {
                if (metricName == headerRow.cells[i].innerHTML) {
                    alreadyExists = true; 
                    break;
                }
            }
            
            // If existing metric (from other experiments) is not present in these results, set to N/A
            if (!alreadyExists) {
                row.cells[i].innerHTML = "N/A";
            }
        }
    }
    else {
        // No results, so set all extra columns to N/A
        for (var i = 6; i < row.cells.length; i++) {
            row.cells[i].innerHTML = "N/A";
        }
    }
}

function populateExperimentRow(experimentInfo, row, table) {
    const statusCell = row.cells[1];
    const authorCell = row.cells[2];
    const notesCell = row.cells[3];
    const finishTimeCell = row.cells[4];

    statusCell.innerHTML = experimentInfo.results != null ? "Complete" : "Running";
    authorCell.innerHTML = experimentInfo.execution_info.author.name;
    notesCell.innerHTML = experimentInfo.execution_info.notes.join("<br />");
    finishTimeCell.innerHTML = experimentInfo.results != null ? experimentInfo.results.end_time : "N/A";

    updateMetricColumns(row, table, experimentInfo.results);
}

function getExperiment(projectName, experimentId, callback) {
    const request = new XMLHttpRequest();
    request.open("GET", window.origin + "/getter/experiment?project_name=" + projectName + "&experiment=" + experimentId, true);
    request.onreadystatechange = () => {
        // When the async request is complete
        if (request.readyState == 4) {
            // Get the experiment information and populate the table
            var experimentInfo = JSON.parse(request.response);
            callback(experimentInfo);
        }
    }
    request.send();
}

function loadExperiments() {
    const urlParams = new URLSearchParams(window.location.search);
    const projectName = urlParams.get("project_name");
    const table = document.getElementById("experiments");
    const rows = document.querySelectorAll("#experiments tbody tr");
    rows.forEach(row => getExperiment(projectName, row.cells[0].childNodes[0].innerHTML, (experimentInfo) => populateExperimentRow(experimentInfo, row, table)));
}

function getSelectedExperimentId() {
    const selectedRow = document.querySelector("#experiments tbody .is-selected");
    return selectedRow != null ? selectedRow.cells[0].childNodes[0].innerHTML : null;
}

function showEditDialog(sender) {
    if (sender.hasAttribute("disabled"))
        return;
    
    const urlParams = new URLSearchParams(window.location.search);
    const projectName = urlParams.get("project_name");
    const experimentId = getSelectedExperimentId();

    if (experimentId == null)
        return;

    const request = new XMLHttpRequest();
    request.onreadystatechange = function() {
        if (request.readyState == 4) {
            let textArea = document.getElementById("editTextArea");
            textArea.value = request.response;

            showDialog("editDialog", sender);
        }
    }
    request.open("GET", window.location.origin + "/notes?project_name=" + projectName + "&experiment=" + experimentId, true);
    request.send();
}

function saveEdits() {
    const newChanges = document.getElementById("editTextArea").value.split("\n");
    const saveButton = document.getElementById("saveEditLink");

    if (saveButton.classList.contains("is-loading"))
        return;
    else
        saveButton.classList.add("is-loading");

    const experimentDate = getSelectedExperimentId();

    if (experimentDate == null)
        return;

    const urlParams = new URLSearchParams(window.location.search);
    const projectName = urlParams.get("project_name");

    const body = {
        projectName: projectName,
        experiment: experimentDate,
        notes: newChanges
    };

    const request = new XMLHttpRequest();
    request.onreadystatechange = function() {
        if (request.readyState == 4) {
            location.reload();
        }
    }
    request.open("POST", window.location.origin + "/notes", true);
    request.setRequestHeader("Content-Type", "application/json");
    request.send(JSON.stringify(body));
}

function showDialog(dialogId, sender) {
    if (sender.hasAttribute("disabled"))
        return;

    let dialog = document.getElementById(dialogId);
    
    if (!dialog.classList.contains("is-active"))
        dialog.classList.add("is-active");
}

function hideDialog(dialogId) {
    let dialog = document.getElementById(dialogId);
    
    if (dialog.classList.contains("is-active"))
        dialog.classList.remove("is-active");
}

function onCheckboxChange() {
    const buttons = document.getElementsByClassName("exp-select-required");
    const selected = document.querySelectorAll("#experiments tbody tr.is-selected");

    for (let i = 0; i < buttons.length; i++) {
        if (selected.length == 1)
            buttons[i].removeAttribute("disabled");
        else if (selected.length > 1)
        {
            if (buttons[i].classList.contains("exp-select-multiple"))
                buttons[i].removeAttribute("disabled");
            else
                buttons[i].setAttribute("disabled", "");
        }
        else
            buttons[i].setAttribute("disabled", "");
    }
}

function selectAllExperiments() {
    const allRows = document.querySelectorAll("#experiments tbody tr");
    const selectedRows = document.querySelectorAll("#experiments tbody tr.is-selected");

    if (selectedRows.length == allRows.length) 
        selectedRows.forEach(row => row.classList.remove("is-selected"));
    else
        allRows.forEach(row => row.classList.add("is-selected"));

    onCheckboxChange();
}

function selectExperiment(obj) {
    if (obj.classList.contains("is-selected"))
        obj.classList.remove("is-selected");
    else
        obj.classList.add("is-selected");

    onCheckboxChange();
}

function deleteSelectedExperiments() {
    const table = document.getElementById("experiments");
    const deleteButton = document.getElementById("deleteLink");

    if (deleteButton.classList.contains("is-loading"))
        return;

    const selected = [];
    const selectedRows = document.querySelectorAll("#experiments tbody tr.is-selected");
    selectedRows.forEach(row => selected.push(row.cells[0].childNodes[0].innerHTML));

    if (selected.length > 0) {
        deleteButton.classList.add("is-loading");

        const urlParams = new URLSearchParams(window.location.search);
        const projectName = urlParams.get("project_name");
    
        const request = new XMLHttpRequest();
        request.onreadystatechange = function() {
            if (request.readyState == 4) {
                location.reload();
            }
        }
        request.open("POST", window.location.origin + "/delete", true);
        request.setRequestHeader("Content-Type", "application/json");
        request.send(JSON.stringify({
            projectName: projectName,
            experiments: selected
        }));
    }
}

function downloadExperiment(sender) {
    if (sender.hasAttribute("disabled"))
        return;

    const urlParams = new URLSearchParams(window.location.search);
    const projectName = urlParams.get("project_name");

    const selectedExperiment = getSelectedExperimentId();
    if (selectedExperiment != null)
        window.location = "./download?project_name=" + projectName + "&experiment=" + selectedExperiment;
}

window.onload = () => {
    loadExperiments();
}