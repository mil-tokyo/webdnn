function isPrivate(object) {
    return (object && object.flags && (
        object.flags.indexOf('Private') >= 0 ||
        object.flags.indexOf('Protected') >= 0
    ));
}

module.exports = {
    isPrivate: isPrivate,
    isPrivateAll: function(object) {
        return (object && object.children && object.children.every(child => isPrivate(child)));
    }
};
