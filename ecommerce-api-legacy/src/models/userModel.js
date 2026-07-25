const db = require('../config/database');

function getByEmail(email) {
    return db.get('SELECT * FROM users WHERE email = ?', [email]);
}

function getById(id) {
    return db.get('SELECT * FROM users WHERE id = ?', [id]);
}

async function create(name, email, passwordHash) {
    const result = await db.run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', [
        name,
        email,
        passwordHash,
    ]);
    return result.lastID;
}

function remove(id) {
    return db.run('DELETE FROM users WHERE id = ?', [id]);
}

module.exports = { getByEmail, getById, create, remove };
