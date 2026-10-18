const crypto = require('crypto');

module.exports = {
    port: Number(process.env.PORT || 3000),
    dbPath: process.env.DB_PATH || ':memory:',
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
    // Empty token keeps the admin routes closed (403) for everybody.
    adminToken: process.env.ADMIN_TOKEN || '',
    jsonBodyLimit: process.env.JSON_BODY_LIMIT || '10kb',
    checkoutRateLimit: {
        windowMs: Number(process.env.CHECKOUT_RATE_WINDOW_MS || 60000),
        max: Number(process.env.CHECKOUT_RATE_MAX || 30)
    },
    reportPageSize: { default: 100, max: 500 },
    // Password of the seeded demo user; random when unset.
    seedUserPassword: process.env.SEED_USER_PASSWORD || crypto.randomBytes(8).toString('hex')
};
