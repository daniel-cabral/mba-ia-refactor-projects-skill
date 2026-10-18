module.exports = (db) => ({
    findActiveById: (id) => db.get('SELECT * FROM courses WHERE id = ? AND active = 1', [id]),
    // Courses with their enrollments, students and payments in a single query.
    findReportRows: (limit, offset) => db.all(
        `SELECT c.id AS course_id, c.title, e.id AS enrollment_id, u.name AS student_name,
                p.amount AS payment_amount, p.status AS payment_status
         FROM (SELECT * FROM courses ORDER BY id LIMIT ? OFFSET ?) c
         LEFT JOIN enrollments e ON e.course_id = c.id
         LEFT JOIN users u ON u.id = e.user_id
         LEFT JOIN payments p ON p.enrollment_id = e.id
         ORDER BY c.id, e.id`,
        [limit, offset]
    )
});
