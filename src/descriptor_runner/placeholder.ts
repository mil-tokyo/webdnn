namespace WebDNN {
    export type Placeholder = {
        eval: string
    };

    /**
     * PlaceholderContext manages the placeholders
     */
    export class PlaceholderContext {
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
            Object.assign(this.values, values);
        }

        resolve(placeholder: number | Placeholder) {
            if (typeof placeholder == 'number') return placeholder;

            if (!this.isResolved) throw Error(`Not all placeholders are resolved: ${this}`);
            return ((placeholders) => eval(placeholder.eval))(this.values);
        }

        toString() {
            return JSON.stringify(this.values);
        }
    }
}
