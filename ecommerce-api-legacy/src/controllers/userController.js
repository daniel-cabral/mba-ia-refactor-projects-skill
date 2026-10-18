const { ValidationError, NotFoundError } = require('../utils/errors');

module.exports = ({ db, userModel, enrollmentModel, paymentModel }) => ({
    async remove(rawId) {
        const id = Number(rawId);
        if (!Number.isInteger(id) || id <= 0) throw new ValidationError('id must be a positive integer');

        const removed = await db.transaction(async () => {
            await paymentModel.removeByUser(id);
            await enrollmentModel.removeByUser(id);
            return userModel.remove(id);
        });
        if (!removed) throw new NotFoundError('Usuário não encontrado');
    }
});
