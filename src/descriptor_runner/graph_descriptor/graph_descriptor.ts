namespace WebDNN {
    /**
     * Graph Descriptor
     */
    export interface GraphDescriptor {
        /**
         * input variables' name
         */
        inputs: string[];

        /**
         * output variables' name
         */
        outputs: string[];

        /**
         * Allocation information for each variable.
         */
        weight_allocation: {
            allocation: { [name: string]: any }
        };

        /**
         * Allocation information for each variable.
         */
        variable_allocation: {
            allocation: { [name: string]: any }
        };

        /**
         * Encoding algorithm of weight binary data.
         */
        weight_encoding: string;
    }
}
