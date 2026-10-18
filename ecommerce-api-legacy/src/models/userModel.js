module.exports = (db) => ({
    findByEmail: (email) => db.get('SELECT id, name, email, pass FROM users WHERE email = ?', [email]),
    findById: (id) => db.get('SELECT id FROM users WHERE id = ?', [id]),
    async create({ name, email, passwordHash }) {
        const result = await db.run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', [name, email, passwordHash]);
        return result.lastID;
    },
    async remove(id) {
        const result = await db.run('DELETE FROM users WHERE id = ?', [id]);
        return result.changes;
    }
});
