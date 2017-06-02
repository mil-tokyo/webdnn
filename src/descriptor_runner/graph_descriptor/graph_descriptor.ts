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

        memory_layout: MemoryLayout,

        /**
         * Allocation information for each variable.
         */
        weight_allocation: {
            allocations: { [name: string]: any }
        };

        /**
         * Allocation information for each variable.
         */
        variable_allocation: {
            allocations: { [name: string]: any }
        };

        /**
         * Encoding algorithm of weight binary data.
         */
        weight_encoding: string;
    }
}
