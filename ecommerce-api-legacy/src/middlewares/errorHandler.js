const logger = require('../utils/logger');
const { NotFoundError } = require('../utils/errors');

const asyncHandler = (fn) => (req, res, next) => Promise.resolve(fn(req, res, next)).catch(next);

const notFoundHandler = (req, res, next) => next(new NotFoundError('Route not found'));

// eslint-disable-next-line no-unused-vars
const errorHandler = (err, req, res, next) => {
    const status = err.status || 500;
    if (status >= 500) logger.error('Unhandled error', { message: err.message, path: req.path });
    res.status(status).json({ error: status >= 500 ? 'Internal server error' : err.message });
};

module.exports = { asyncHandler, notFoundHandler, errorHandler };
