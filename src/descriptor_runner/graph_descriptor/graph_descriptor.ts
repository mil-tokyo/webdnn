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
         * Encoding algorithm of weight binary data.
         */
        weight_encoding: string;
    }
}
