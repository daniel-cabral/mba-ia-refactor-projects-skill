const express = require('express');
const { asyncHandler } = require('../middlewares/errorHandler');

module.exports = ({ checkoutController, reportController, userController, adminOnly, checkoutRateLimit }) => {
    const router = express.Router();

    router.post('/api/checkout', checkoutRateLimit, asyncHandler(async (req, res) => {
        res.status(200).json(await checkoutController.checkout(req.body));
    }));

    router.get('/api/admin/financial-report', adminOnly, asyncHandler(async (req, res) => {
        res.json(await reportController.financialReport(req.query));
    }));

    router.delete('/api/users/:id', adminOnly, asyncHandler(async (req, res) => {
        await userController.remove(req.params.id);
        res.send('Usuário deletado.');
    }));

    return router;
};
