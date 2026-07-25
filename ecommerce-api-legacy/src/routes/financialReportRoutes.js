const express = require('express');

const financialReportController = require('../controllers/financialReportController');

const router = express.Router();

router.get('/api/admin/financial-report', async (req, res, next) => {
    try {
        const report = await financialReportController.generate();
        res.json(report);
    } catch (err) {
        next(err);
    }
});

module.exports = router;
