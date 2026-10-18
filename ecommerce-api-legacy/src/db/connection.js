const sqlite3 = require('sqlite3').verbose();
const { hashPassword } = require('../utils/password');

const run = (db, sql, params = []) => new Promise((resolve, reject) => {
    db.run(sql, params, function (err) { err ? reject(err) : resolve({ lastID: this.lastID, changes: this.changes }); });
});
const get = (db, sql, params = []) => new Promise((resolve, reject) => {
    db.get(sql, params, (err, row) => (err ? reject(err) : resolve(row)));
});
const all = (db, sql, params = []) => new Promise((resolve, reject) => {
    db.all(sql, params, (err, rows) => (err ? reject(err) : resolve(rows)));
});

function createConnection(dbPath) {
    const db = new sqlite3.Database(dbPath);
    let queue = Promise.resolve();

    // One connection is shared, so transactions are serialized to avoid interleaved BEGIN/COMMIT.
    function transaction(work) {
        const result = queue.then(async () => {
            await run(db, 'BEGIN');
            try {
                const value = await work();
                await run(db, 'COMMIT');
                return value;
            } catch (err) {
                await run(db, 'ROLLBACK');
                throw err;
            }
        });
        queue = result.catch(() => {});
        return result;
    }

    return {
        run: (sql, params) => run(db, sql, params),
        get: (sql, params) => get(db, sql, params),
        all: (sql, params) => all(db, sql, params),
        transaction,
        close: () => new Promise((resolve) => db.close(resolve))
    };
}

async function initSchema(conn, { seedUserPassword }) {
    await conn.run('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, pass TEXT)');
    await conn.run('CREATE TABLE IF NOT EXISTS courses (id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER)');
    await conn.run('CREATE TABLE IF NOT EXISTS enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER)');
    await conn.run('CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT)');
    await conn.run('CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME)');

    const seeded = await conn.get('SELECT COUNT(*) AS total FROM users');
    if (seeded.total > 0) return;

    await conn.run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
        ['Leonan', 'leonan@fullcycle.com.br', hashPassword(seedUserPassword)]);
    await conn.run("INSERT INTO courses (title, price, active) VALUES ('Clean Architecture', 997.00, 1), ('Docker', 497.00, 1)");
    await conn.run('INSERT INTO enrollments (user_id, course_id) VALUES (1, 1)');
    await conn.run("INSERT INTO payments (enrollment_id, amount, status) VALUES (1, 997.00, 'PAID')");
}

module.exports = { createConnection, initSchema };
