module.exports = {
    normalizeKind: function(kind) {
        if (kind === 'External module') {
            return 'module';
        } else {
            return kind;
        }
    }
};
