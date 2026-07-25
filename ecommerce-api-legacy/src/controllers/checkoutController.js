const bcrypt = require('bcryptjs');

const auditLogModel = require('../models/auditLogModel');
const courseModel = require('../models/courseModel');
const enrollmentModel = require('../models/enrollmentModel');
const paymentModel = require('../models/paymentModel');
const userModel = require('../models/userModel');
const { ApiError } = require('../middlewares/errorHandler');

async function checkout({ nome, email, senha, cursoId, cartao }) {
    if (!nome || !email || !cursoId || !cartao) {
        throw new ApiError(400, 'Bad Request');
    }
    if (!senha) {
        throw new ApiError(400, 'Senha é obrigatória');
    }

    const course = await courseModel.getById(cursoId);
    if (!course) {
        throw new ApiError(404, 'Curso não encontrado');
    }

    const existingUser = await userModel.getByEmail(email);
    let userId;
    if (existingUser) {
        userId = existingUser.id;
    } else {
        const senhaHash = await bcrypt.hash(senha, 10);
        userId = await userModel.create(nome, email, senhaHash);
    }

    // Simulação de gateway de pagamento — substituir por integração real antes de produção.
    const status = cartao.startsWith('4') ? 'PAID' : 'DENIED';
    if (status === 'DENIED') {
        throw new ApiError(400, 'Pagamento recusado');
    }

    const enrollmentId = await enrollmentModel.create(userId, cursoId);
    await paymentModel.create(enrollmentId, course.price, status);
    await auditLogModel.record(`Checkout curso ${cursoId} por ${userId}`);

    return { enrollmentId };
}

module.exports = { checkout };
