export function getColumnType(colToken, tables) {
    const tableId = colToken.split(': ')[0];
    const colId = colToken.split(': ')[1];
    const cols = tables[tableId];
    const colIndex = cols.map(col => col[0]).indexOf(colId);
    if (colIndex >= 0)
        return cols[colIndex][1];
    else
        return "none"
}

export function type2icon(type) {
    let iconClass = "";
    if (type === "text")
        iconClass = "fas fa-font"
    else if (type === "number")
        iconClass = "fas fa-list-ol"
    else if (type === "key")
        iconClass = "fas fa-key"
    return iconClass
}