const enrollmentModel = require('../models/enrollmentModel');
const paymentModel = require('../models/paymentModel');
const userModel = require('../models/userModel');

async function deleteUser(userId) {
    const enrollments = await enrollmentModel.getByUser(userId);
    const enrollmentIds = enrollments.map((e) => e.id);

    await paymentModel.removeByEnrollments(enrollmentIds);
    await enrollmentModel.removeByUser(userId);
    await userModel.remove(userId);

    return { message: 'Usuário deletado com sucesso.' };
}

module.exports = { deleteUser };
