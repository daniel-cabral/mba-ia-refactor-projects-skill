module.exports = (db) => ({
    findByUserAndCourse: (userId, courseId) =>
        db.get('SELECT id FROM enrollments WHERE user_id = ? AND course_id = ?', [userId, courseId]),
    async create(userId, courseId) {
        const result = await db.run('INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)', [userId, courseId]);
        return result.lastID;
    },
    removeByUser: (userId) => db.run('DELETE FROM enrollments WHERE user_id = ?', [userId])
});
