const { PAYMENT_STATUS, APPROVED_CARD_PREFIX } = require('../utils/constants');
const { hashPassword, verifyPassword } = require('../utils/password');
const { ValidationError, UnauthorizedError, NotFoundError, ConflictError } = require('../utils/errors');

const EMAIL_PATTERN = /^\S+@\S+\.\S+$/;
const CARD_PATTERN = /^\d{12,19}$/;

function validateCheckout(body) {
    const { usr: name, eml: email, pwd: password, c_id: courseId, card: cardNumber } = body || {};

    if (typeof name !== 'string' || !name.trim()) throw new ValidationError('usr is required');
    if (typeof email !== 'string' || !EMAIL_PATTERN.test(email)) throw new ValidationError('eml must be a valid email');
    if (!Number.isInteger(Number(courseId)) || Number(courseId) <= 0) throw new ValidationError('c_id must be a positive integer');
    if (typeof cardNumber !== 'string' || !CARD_PATTERN.test(cardNumber)) throw new ValidationError('card must contain 12 to 19 digits');
    if (typeof password !== 'string' || !password) throw new ValidationError('pwd is required');

    return { name: name.trim(), email, password, courseId: Number(courseId), cardNumber };
}

module.exports = ({ db, userModel, courseModel, enrollmentModel, paymentModel, auditModel, logger }) => ({
    async checkout(body) {
        const { name, email, password, courseId, cardNumber } = validateCheckout(body);

        const course = await courseModel.findActiveById(courseId);
        if (!course) throw new NotFoundError('Curso não encontrado');

        const existingUser = await userModel.findByEmail(email);
        if (existingUser) {
            if (!verifyPassword(password, existingUser.pass)) throw new UnauthorizedError('Invalid credentials');
            if (await enrollmentModel.findByUserAndCourse(existingUser.id, courseId)) {
                throw new ConflictError('Usuário já matriculado neste curso');
            }
        }

        logger.info('Processing payment', { courseId, cardLast4: cardNumber.slice(-4) });
        const status = cardNumber.startsWith(APPROVED_CARD_PREFIX) ? PAYMENT_STATUS.PAID : PAYMENT_STATUS.DENIED;
        if (status === PAYMENT_STATUS.DENIED) throw new ValidationError('Pagamento recusado');

        const enrollmentId = await db.transaction(async () => {
            const userId = existingUser
                ? existingUser.id
                : await userModel.create({ name, email, passwordHash: hashPassword(password) });
            const newEnrollmentId = await enrollmentModel.create(userId, courseId);
            await paymentModel.create(newEnrollmentId, course.price, status);
            await auditModel.record(`Checkout curso ${courseId} por ${userId}`);
            return newEnrollmentId;
        });

        return { msg: 'Sucesso', enrollment_id: enrollmentId };
    }
});
