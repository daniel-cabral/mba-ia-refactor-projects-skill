const format = (level, message, meta) =>
    `[${new Date().toISOString()}] ${level} ${message}${meta ? ` ${JSON.stringify(meta)}` : ''}`;

module.exports = {
    info: (message, meta) => console.log(format('INFO', message, meta)),
    warn: (message, meta) => console.warn(format('WARN', message, meta)),
    error: (message, meta) => console.error(format('ERROR', message, meta))
};
