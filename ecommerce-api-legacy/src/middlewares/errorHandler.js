class ApiError extends Error {
    constructor(statusCode, message) {
        super(message);
        this.statusCode = statusCode;
    }
}

// eslint-disable-next-line no-unused-vars
function errorHandler(err, req, res, next) {
    const statusCode = err instanceof ApiError ? err.statusCode : 500;
    const message = err instanceof ApiError ? err.message : 'Erro interno do servidor';
    res.status(statusCode).send(message);
}

module.exports = { ApiError, errorHandler };
