const PAYMENT_STATUS = { PAID: 'PAID', DENIED: 'DENIED' };

// Simulated gateway: cards starting with this digit are approved.
const APPROVED_CARD_PREFIX = '4';

module.exports = { PAYMENT_STATUS, APPROVED_CARD_PREFIX };
