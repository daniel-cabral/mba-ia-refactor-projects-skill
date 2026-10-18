const crypto = require('crypto');
const { ForbiddenError } = require('../utils/errors');

// Guards dangerous routes: 403 unless ADMIN_TOKEN is configured and sent in x-admin-token.
module.exports = (adminToken) => (req, res, next) => {
    const sent = Buffer.from(String(req.get('x-admin-token') || ''));
    const expected = Buffer.from(adminToken);
    const allowed = expected.length > 0 && sent.length === expected.length && crypto.timingSafeEqual(sent, expected);
    return allowed ? next() : next(new ForbiddenError());
};
