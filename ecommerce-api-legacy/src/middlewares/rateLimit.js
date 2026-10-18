const { HttpError } = require('../utils/errors');

// Fixed-window limiter per client IP; the counters live in the closure of each created middleware.
module.exports = ({ windowMs, max }) => {
    const hits = new Map();

    return (req, res, next) => {
        const now = Date.now();
        const entry = hits.get(req.ip);

        if (!entry || now >= entry.resetAt) {
            hits.set(req.ip, { count: 1, resetAt: now + windowMs });
            return next();
        }
        entry.count += 1;
        if (entry.count > max) return next(new HttpError(429, 'Too many requests'));
        return next();
    };
};
