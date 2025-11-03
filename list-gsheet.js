// Site-specific JavaScript goes here
let tableRows = []; // To store all rows for filtering
let currentSortColumn = null;
let currentSortOrder = 'asc';

/**
 * Load data from a Google Sheet and render it.
 * @param {string} bookId - The Google Sheet ID.
 * @param {Object} colConfig - An object specifying columns for the table.
 */
function loadSheet(bookId, sheetId, colConfig) {
    fetch(`https://docs.google.com/spreadsheets/d/${bookId}/gviz/tq?tqx=out:json&gid=${sheetId}`)
        .then(response => response.text())
        .then(data => {
            const jsonData = JSON.parse(data.substring(47, data.length - 2)); // Clean up unwanted characters
            const rows = jsonData.table.rows;
            tableRows = rows; // Store rows for filtering
            renderTable(rows, colConfig); // Render initial table
        })
        .catch(error => console.error('Error loading sheet data:', error));
}

/**
 * Render the data table based on column configuration.
 * @param {Array} rows - Rows of data to render in the table.
 * @param {Object} colConfig - An object specifying columns and headers for the table.
 */
function renderTable(rows, colConfig) {
    const sheetData = document.getElementById('sheetData');
    if (!sheetData) return; // Ensure sheetData element exists

    let tableContent = '<table id="studentTable"><thead><tr>';

    // Dynamically create headers with onclick events for sorting
    colConfig.columns.forEach((col, index) => {
        tableContent += `<th onclick="sortTable(${index}, '${colConfig.sortOrder}')">${col.header}</th>`;
    });

    tableContent += '</tr></thead><tbody>';

    // Render table rows
    rows.forEach(row => {
        tableContent += '<tr>';
        colConfig.columns.forEach(col => {
            const cellValue = row.c[col.index] ? row.c[col.index].v : ''; 
            tableContent += `<td>${cellValue}</td>`;
        });
        tableContent += '</tr>';
    });

    tableContent += '</tbody></table>';
    sheetData.innerHTML = tableContent;
    sheetData.querySelector('table').style.display = 'table'; // Make sure table is displayed
}


/**
 * Filter the table based on input from text fields.
 * @param {Object} filters - An object containing filter values for each column.
 */
function filterTable(filters) {
    // Check that tableRows is populated
    if (!tableRows || tableRows.length === 0) {
        console.error('No data available to filter.');
        return;
    }

    // Filter rows based on provided filters
    const filteredRows = tableRows.filter(row => {
        return Object.keys(filters).every(key => {
            const colIndex = filters[key].index;
            const filterValue = filters[key].value? filters[key].value.toLowerCase():'';
            const cellValue = row.c[colIndex] && row.c[colIndex].v ? String(row.c[colIndex].v).toLowerCase() : '';
            return cellValue.startsWith(filterValue);
        });
    });

    // Ensure colConfig is passed correctly
    renderTable(filteredRows, filters.colConfig);
}

/**
 * Sort the table by the selected column index and order.
 * @param {number} columnIndex - Index of the column to sort by.
 * @param {string} sortOrder - Sort order, either 'asc' or 'desc'.
 */
function sortTable(columnIndex, sortOrder) {
    const table = document.querySelector('#sheetData table');
    if (!table) {
        console.error("Table not found");
        return;
    }

    console.log("Table found, proceeding with sort...");
    const tbody = table.querySelector("tbody");
    if (!tbody){
        console.log("No tbody found");
        return;
    }

    const rows = Array.from(tbody.querySelectorAll("tr"));
    if (!rows || rows.length === 0) {
        console.error("No rows found in tbody");
        return;
    }

    // Reset sort direction if the same column is clicked
    if (currentSortColumn === columnIndex) {
        currentSortOrder = currentSortOrder === 'asc' ? 'desc' : 'asc';
    } else {
        currentSortColumn = columnIndex;
        currentSortOrder = sortOrder || 'asc';
    }

    // Clear previous sort indicators
    Array.from(table.querySelectorAll("th")).forEach(th => th.classList.remove('sorted-asc', 'sorted-desc'));
    table.querySelectorAll("th")[columnIndex].classList.add(currentSortOrder === 'asc' ? 'sorted-asc' : 'sorted-desc');

    // Sort rows
    rows.sort((a, b) => {
        const cellA = a.cells[columnIndex] ? a.cells[columnIndex].innerText.toLowerCase() : '';
        const cellB = b.cells[columnIndex] ? b.cells[columnIndex].innerText.toLowerCase() : '';

        const comparison = cellA.localeCompare(cellB);
        return currentSortOrder === 'asc' ? comparison : -comparison;
    });

    // Reorder rows in the table body
    rows.forEach(row => tbody.appendChild(row));
}
