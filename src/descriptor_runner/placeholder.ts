/**
 * @module webdnn
 */

/** Don't Remove This comment block */

/**
 * @protected
 */
export interface Placeholder {
    eval: string
}

/**
 * PlaceholderContext manages the placeholders
 * @protected
 */
export default class PlaceholderContext {
    private values: { [key: string]: number | null } = {};

    constructor(values?: { [key: string]: number | null }) {
        if (values) {
            this.update(values);
        }
    }

    get isResolved() {
        return Object.values(this.values).every(value => typeof value == 'number');
    }

    update(values: { [key: string]: number | null }) {
        this.values = Object.assign(this.values, values);
    }

    resolve(placeholder: any): any {
        // Literal value => return itself.
        if (typeof placeholder !== 'object') return placeholder;

        // Placeholder object ( { eval: string } ) => resolve
        if (Object.keys(placeholder).length == 1 && 'eval' in placeholder) {
            if (!this.isResolved) throw Error(`Not all placeholders are resolved: ${this}`);

            return ((placeholders) => eval(placeholder.eval))(this.values);
        }

        // Array => deep copy
        if (placeholder instanceof Array) {
            return placeholder.map((value: any) => this.resolve(value));
        }

        // Object => deep copy
        return Object.entries(placeholder)
            .reduce((result: Object, [key, value]: [string, any]) => {
                result[key] = this.resolve(value);
                return result;
            }, {})
    }

    toString() {
        return JSON.stringify(this.values);
    }
}
