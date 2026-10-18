const express = require('express');
const config = require('./config');
const logger = require('./utils/logger');
const { createConnection, initSchema } = require('./db/connection');
const createUserModel = require('./models/userModel');
const createCourseModel = require('./models/courseModel');
const createEnrollmentModel = require('./models/enrollmentModel');
const createPaymentModel = require('./models/paymentModel');
const createAuditModel = require('./models/auditModel');
const createCheckoutController = require('./controllers/checkoutController');
const createReportController = require('./controllers/reportController');
const createUserController = require('./controllers/userController');
const createRoutes = require('./routes');
const createAdminOnly = require('./middlewares/adminOnly');
const createRateLimit = require('./middlewares/rateLimit');
const securityHeaders = require('./middlewares/securityHeaders');
const { notFoundHandler, errorHandler } = require('./middlewares/errorHandler');

async function start() {
    const db = createConnection(config.dbPath);
    await initSchema(db, config);

    const userModel = createUserModel(db);
    const courseModel = createCourseModel(db);
    const enrollmentModel = createEnrollmentModel(db);
    const paymentModel = createPaymentModel(db);
    const auditModel = createAuditModel(db);

    const app = express();
    app.disable('x-powered-by');
    app.use(securityHeaders);
    app.use(express.json({ limit: config.jsonBodyLimit }));

    app.use(createRoutes({
        checkoutController: createCheckoutController({ db, userModel, courseModel, enrollmentModel, paymentModel, auditModel, logger }),
        reportController: createReportController({ courseModel, pageSize: config.reportPageSize }),
        userController: createUserController({ db, userModel, enrollmentModel, paymentModel }),
        adminOnly: createAdminOnly(config.adminToken),
        checkoutRateLimit: createRateLimit(config.checkoutRateLimit)
    }));

    app.use(notFoundHandler);
    app.use(errorHandler);

    app.listen(config.port, () => {
        logger.info(`LMS API listening on port ${config.port}`);
    });
}

start().catch((err) => {
    logger.error('Failed to start application', { message: err.message });
    process.exit(1);
});
