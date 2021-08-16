import axios from 'axios'

const GET_REQUEST = 'get'
const POST_REQUEST = 'post'
const dataServerUrl = `${process.env.DATA_SERVER_URL || 'http://127.0.0.1:5010'}/api`

function request(url, params, type, callback) {
    let func
    if (type === GET_REQUEST) {
        func = axios.get
    } else if (type === POST_REQUEST) {
        func = axios.post
    }

    func(url, params).then((response) => {
            if (response.status === 200) {
                callback(response["data"])
            } else {
                console.error(response) /* eslint-disable-line */
            }
        })
        .catch((error) => {
            console.error(error) /* eslint-disable-line */
        })
}

function initialization(dataset, callback) {
    // console.log("dataset: ", dataset);
    const url = `${dataServerUrl}/initialization/${dataset}`
    const params = {}
    request(url, params, GET_REQUEST, callback)
}

function getDBInfo(db_id, callback) {
    const url = `${dataServerUrl}/get_database_meta/${db_id}`
    const params = {}
    request(url, params, GET_REQUEST, callback)
}

function getTables(dbselected, callback) {
    const url = `${dataServerUrl}/get_tables/${dbselected}`
    const params = {}
    request(url, params, GET_REQUEST, callback)
}

function getTableCols(tableName, callback) {
    const url = `${dataServerUrl}/get_cols/${tableName}`
    const params = {}
    request(url, params, GET_REQUEST, callback)
}

function loadTablesContent(tableName, callback) {
    const url = `${dataServerUrl}/load_tables/${tableName}`
    const params = {}
    request(url, params, GET_REQUEST, callback)
}

function text2SQL(userQuery, callback) {
    const url = `${dataServerUrl}/text2sql/${userQuery[0]}/${userQuery[1]}`
    const params = {}
    request(url, params, GET_REQUEST, callback);
}

function SQL2VL(sql, db_id, callback) {
    const url = `${dataServerUrl}/sql2vis/${sql}/${db_id}`;
    const params = {};
    request(url, params, GET_REQUEST, callback);
}

function SQL2text(sql, db_id, callback) {
    const url = `${dataServerUrl}/sql2text/${sql}/${db_id}`;
    const params = {};
    request(url, params, GET_REQUEST, callback);
}

function SQLSugg(db_id, callback) {
    const url = `${dataServerUrl}/sql_sugg/${db_id}`;
    const params = {};
    request(url, params, GET_REQUEST, callback);
}

export default {
    dataServerUrl,
    initialization,
    getDBInfo,
    getTables,
    getTableCols,
    loadTablesContent,
    text2SQL,
    SQL2VL,
    SQL2text,
    SQLSugg
}