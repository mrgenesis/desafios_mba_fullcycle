const reportModel = require('../models/reportModel');

async function generate() {
    const rows = await reportModel.financialReportRows();

    const coursesById = new Map();
    for (const row of rows) {
        if (!coursesById.has(row.course_id)) {
            coursesById.set(row.course_id, { course: row.course_title, revenue: 0, students: [] });
        }

        if (row.enrollment_id === null) {
            continue;
        }

        const courseData = coursesById.get(row.course_id);
        const paid = row.status === 'PAID';

        if (paid) {
            courseData.revenue += row.amount;
        }
        courseData.students.push({
            student: row.student_name,
            paid: paid ? row.amount : 0,
        });
    }

    return Array.from(coursesById.values());
}

module.exports = { generate };
