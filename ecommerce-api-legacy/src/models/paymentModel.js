const db = require('../config/database');

function create(enrollmentId, amount, status) {
    return db.run('INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)', [
        enrollmentId,
        amount,
        status,
    ]);
}

function removeByEnrollments(enrollmentIds) {
    if (!enrollmentIds.length) {
        return Promise.resolve();
    }
    const placeholders = enrollmentIds.map(() => '?').join(',');
    return db.run(`DELETE FROM payments WHERE enrollment_id IN (${placeholders})`, enrollmentIds);
}

module.exports = { create, removeByEnrollments };
