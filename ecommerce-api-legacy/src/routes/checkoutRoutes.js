const express = require('express');

const checkoutController = require('../controllers/checkoutController');

const router = express.Router();

router.post('/api/checkout', async (req, res, next) => {
    try {
        const { usr, eml, pwd, c_id: cId, card } = req.body;
        const result = await checkoutController.checkout({
            nome: usr,
            email: eml,
            senha: pwd,
            cursoId: cId,
            cartao: card,
        });
        res.status(200).json({ msg: 'Sucesso', enrollment_id: result.enrollmentId });
    } catch (err) {
        next(err);
    }
});

module.exports = router;
