const Handlebars = require('handlebars');

module.exports = {
    dump: function(object) {
        let seen = [];
        let content = (JSON.stringify(object, (key, val) => {
            if (val !== null && typeof val === "object") {
                if (seen.indexOf(val) >= 0) return null;
                seen.push(val);
            }
            return val;
        }) || '')
            .replace(/>/g, '&gt;')
            .replace(/</g, '&lt;')
            .replace(/\\/g, '\\\\')
            .replace(/'/g, '\\\'');

        return new Handlebars.SafeString(`<script type="application/javascript">console.log(JSON.parse('${content}'));</script>`);
    }
};
