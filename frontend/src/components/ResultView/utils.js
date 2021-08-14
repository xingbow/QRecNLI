export function getColumnType(colToken, tables) {
    const tableId = colToken.split(': ')[0];
    const colId = colToken.split(': ')[1];
    const cols = tables[tableId];
    const colIndex = cols.map(col => col[0]).indexOf(colId);
    const type = cols[colIndex][1];
    return type
}