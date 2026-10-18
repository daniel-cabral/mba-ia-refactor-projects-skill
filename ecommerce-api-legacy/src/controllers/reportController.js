const { ValidationError } = require('../utils/errors');

function parseNonNegativeInt(value, fallback, field) {
    if (value === undefined) return fallback;
    const parsed = Number(value);
    if (!Number.isInteger(parsed) || parsed < 0) throw new ValidationError(`${field} must be a non-negative integer`);
    return parsed;
}

module.exports = ({ courseModel, pageSize }) => ({
    async financialReport(query) {
        const limit = Math.min(parseNonNegativeInt(query.limit, pageSize.default, 'limit'), pageSize.max);
        const offset = parseNonNegativeInt(query.offset, 0, 'offset');

        const rows = await courseModel.findReportRows(limit, offset);
        const coursesById = new Map();

        for (const row of rows) {
            if (!coursesById.has(row.course_id)) {
                coursesById.set(row.course_id, { course: row.title, revenue: 0, students: [] });
            }
            if (row.enrollment_id === null) continue;

            const courseData = coursesById.get(row.course_id);
            if (row.payment_status === 'PAID') courseData.revenue += row.payment_amount;
            courseData.students.push({
                student: row.student_name || 'Unknown',
                paid: row.payment_amount || 0
            });
        }

        return [...coursesById.values()];
    }
});
