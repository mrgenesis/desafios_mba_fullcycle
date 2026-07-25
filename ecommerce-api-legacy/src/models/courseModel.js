const db = require('../config/database');

function getById(id) {
    return db.get('SELECT * FROM courses WHERE id = ? AND active = 1', [id]);
}

function getAll() {
    return db.all('SELECT * FROM courses', []);
}

module.exports = { getById, getAll };
