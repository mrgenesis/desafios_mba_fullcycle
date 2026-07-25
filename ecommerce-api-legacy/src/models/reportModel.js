const db = require('../config/database');

function financialReportRows() {
    return db.all(`
        SELECT courses.id AS course_id, courses.title AS course_title,
               enrollments.id AS enrollment_id,
               COALESCE(users.name, 'Unknown') AS student_name,
               payments.amount AS amount, payments.status AS status
        FROM courses
        LEFT JOIN enrollments ON enrollments.course_id = courses.id
        LEFT JOIN users ON users.id = enrollments.user_id
        LEFT JOIN payments ON payments.enrollment_id = enrollments.id
        ORDER BY courses.id, enrollments.id
    `);
}

module.exports = { financialReportRows };
