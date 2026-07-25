const settings = {
    dbUser: process.env.DB_USER || 'dev_user',
    dbPass: process.env.DB_PASS || 'dev_pass',
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || 'pk_test_dev_only',
    smtpUser: process.env.SMTP_USER || 'dev@example.com',
    port: process.env.PORT || 3000,
};

module.exports = settings;
