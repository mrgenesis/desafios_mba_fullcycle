const sqlite3 = require('sqlite3').verbose();

let db;

function getDb() {
    if (!db) {
        db = new sqlite3.Database(':memory:');
    }
    return db;
}

function run(sql, params = []) {
    return new Promise((resolve, reject) => {
        getDb().run(sql, params, function callback(err) {
            if (err) return reject(err);
            resolve({ lastID: this.lastID, changes: this.changes });
        });
    });
}

function get(sql, params = []) {
    return new Promise((resolve, reject) => {
        getDb().get(sql, params, (err, row) => {
            if (err) return reject(err);
            resolve(row);
        });
    });
}

function all(sql, params = []) {
    return new Promise((resolve, reject) => {
        getDb().all(sql, params, (err, rows) => {
            if (err) return reject(err);
            resolve(rows);
        });
    });
}

function initDb() {
    return new Promise((resolve, reject) => {
        const database = getDb();
        database.serialize(() => {
            database.run('CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, pass TEXT)');
            database.run('CREATE TABLE courses (id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER)');
            database.run('CREATE TABLE enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER)');
            database.run('CREATE TABLE payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT)');
            database.run('CREATE TABLE audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME)');

            database.run("INSERT INTO users (name, email, pass) VALUES ('Leonan', 'leonan@fullcycle.com.br', '123')");
            database.run("INSERT INTO courses (title, price, active) VALUES ('Clean Architecture', 997.00, 1), ('Docker', 497.00, 1)");
            database.run('INSERT INTO enrollments (user_id, course_id) VALUES (1, 1)');
            database.run(
                "INSERT INTO payments (enrollment_id, amount, status) VALUES (1, 997.00, 'PAID')",
                (err) => {
                    if (err) return reject(err);
                    resolve();
                }
            );
        });
    });
}

module.exports = { getDb, run, get, all, initDb };
