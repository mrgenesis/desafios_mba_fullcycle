const express = require('express');

const settings = require('./config/settings');
const { initDb } = require('./config/database');
const { errorHandler } = require('./middlewares/errorHandler');

const checkoutRoutes = require('./routes/checkoutRoutes');
const financialReportRoutes = require('./routes/financialReportRoutes');
const userRoutes = require('./routes/userRoutes');

async function createApp() {
    const app = express();
    app.use(express.json());

    await initDb();

    app.use(checkoutRoutes);
    app.use(financialReportRoutes);
    app.use(userRoutes);

    app.use(errorHandler);

    return app;
}

if (require.main === module) {
    createApp().then((app) => {
        app.listen(settings.port, () => {
            console.log(`Frankenstein LMS rodando na porta ${settings.port}...`);
        });
    });
}

module.exports = { createApp };
