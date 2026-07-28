import * as $protobuf from "protobufjs";
import Long = require("long");

/** Namespace onnx. */
export namespace onnx {

    /** Version enum. */
    enum Version {

        /** _START_VERSION value */
        _START_VERSION = 0,

        /** IR_VERSION_2017_10_10 value */
        IR_VERSION_2017_10_10 = 1,

        /** IR_VERSION_2017_10_30 value */
        IR_VERSION_2017_10_30 = 2,

        /** IR_VERSION_2017_11_3 value */
        IR_VERSION_2017_11_3 = 3,

        /** IR_VERSION_2019_1_22 value */
        IR_VERSION_2019_1_22 = 4,

        /** IR_VERSION_2019_3_18 value */
        IR_VERSION_2019_3_18 = 5,

        /** IR_VERSION_2019_9_19 value */
        IR_VERSION_2019_9_19 = 6,

        /** IR_VERSION_2020_5_8 value */
        IR_VERSION_2020_5_8 = 7,

        /** IR_VERSION_2021_7_30 value */
        IR_VERSION_2021_7_30 = 8,

        /** IR_VERSION_2023_5_5 value */
        IR_VERSION_2023_5_5 = 9,

        /** IR_VERSION value */
        IR_VERSION = 10
    }

    /**
     * Properties of an AttributeProto.
     * @deprecated Use onnx.AttributeProto.$Properties instead.
     */
    interface IAttributeProto extends onnx.AttributeProto.$Properties {
    }

    /** Represents an AttributeProto. */
    class AttributeProto {

        /**
         * Constructs a new AttributeProto.
         * @param [properties] Properties to set
         */
        constructor(properties?: onnx.AttributeProto.$Properties);

        /** Unknown fields preserved while decoding when enabled */
        $unknowns?: Uint8Array[];

        /** AttributeProto name. */
        name: string;

        /** AttributeProto refAttrName. */
        refAttrName: string;

        /** AttributeProto docString. */
        docString: string;

        /** AttributeProto type. */
        type: onnx.AttributeProto.AttributeType;

        /** AttributeProto f. */
        f: number;

        /** AttributeProto i. */
        i: (number|Long);

        /** AttributeProto s. */
        s: Uint8Array;

        /** AttributeProto t. */
        t?: (onnx.TensorProto.$Properties|null);

        /** AttributeProto g. */
        g?: (onnx.GraphProto.$Properties|null);

        /** AttributeProto sparseTensor. */
        sparseTensor?: (onnx.SparseTensorProto.$Properties|null);

        /** AttributeProto tp. */
        tp?: (onnx.TypeProto.$Properties|null);

        /** AttributeProto floats. */
        floats: number[];

        /** AttributeProto ints. */
        ints: (number|Long)[];

        /** AttributeProto strings. */
        strings: Uint8Array[];

        /** AttributeProto tensors. */
        tensors: onnx.TensorProto.$Properties[];

        /** AttributeProto graphs. */
        graphs: onnx.GraphProto.$Properties[];

        /** AttributeProto sparseTensors. */
        sparseTensors: onnx.SparseTensorProto.$Properties[];

        /** AttributeProto typeProtos. */
        typeProtos: onnx.TypeProto.$Properties[];

        /**
         * Creates a new AttributeProto instance using the specified properties.
         * @param [properties] Properties to set
         * @returns AttributeProto instance
         */
        static create(properties: onnx.AttributeProto.$Shape): onnx.AttributeProto & onnx.AttributeProto.$Shape;
        static create(properties?: onnx.AttributeProto.$Properties): onnx.AttributeProto;

        /**
         * Encodes the specified AttributeProto message. Does not implicitly {@link onnx.AttributeProto.verify|verify} messages.
         * @param message AttributeProto message or plain object to encode
         * @param [writer] Writer to encode to
         * @returns Writer
         */
        static encode(message: onnx.AttributeProto.$Properties, writer?: $protobuf.Writer): $protobuf.Writer;

        /**
         * Encodes the specified AttributeProto message, length delimited. Does not implicitly {@link onnx.AttributeProto.verify|verify} messages.
         * @param message AttributeProto message or plain object to encode
         * @param [writer] Writer to encode to
         * @returns Writer
         */
        static encodeDelimited(message: onnx.AttributeProto.$Properties, writer?: $protobuf.Writer): $protobuf.Writer;

        /**
         * Decodes an AttributeProto message from the specified reader or buffer.
         * @param reader Reader or buffer to decode from
         * @param [length] Message length if known beforehand
         * @returns {onnx.AttributeProto & onnx.AttributeProto.$Shape} AttributeProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): onnx.AttributeProto & onnx.AttributeProto.$Shape;

        /**
         * Decodes an AttributeProto message from the specified reader or buffer, length delimited.
         * @param reader Reader or buffer to decode from
         * @returns {onnx.AttributeProto & onnx.AttributeProto.$Shape} AttributeProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): onnx.AttributeProto & onnx.AttributeProto.$Shape;

        /**
         * Verifies an AttributeProto message.
         * @param message Plain object to verify
         * @returns `null` if valid, otherwise the reason why it is not
         */
        static verify(message: { [k: string]: any }): (string|null);

        /**
         * Creates an AttributeProto message from a plain object. Also converts values to their respective internal types.
         * @param object Plain object
         * @returns AttributeProto
         */
        static fromObject(object: { [k: string]: any }): onnx.AttributeProto;

        /**
         * Creates a plain object from an AttributeProto message. Also converts values to other types if specified.
         * @param message AttributeProto
         * @param [options] Conversion options
         * @returns Plain object
         */
        static toObject(message: onnx.AttributeProto, options?: $protobuf.IConversionOptions): { [k: string]: any };

        /**
         * Converts this AttributeProto to JSON.
         * @returns JSON object
         */
        toJSON(): { [k: string]: any };

        /**
         * Gets the type url for AttributeProto
         * @param [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
         * @returns The type url
         */
        static getTypeUrl(prefix?: string): string;
    }

    namespace AttributeProto {

        /** Properties of an AttributeProto. */
        interface $Properties {

            /** AttributeProto name */
            name?: (string|null);

            /** AttributeProto refAttrName */
            refAttrName?: (string|null);

            /** AttributeProto docString */
            docString?: (string|null);

            /** AttributeProto type */
            type?: (onnx.AttributeProto.AttributeType|null);

            /** AttributeProto f */
            f?: (number|null);

            /** AttributeProto i */
            i?: (number|Long|null);

            /** AttributeProto s */
            s?: (Uint8Array|null);

            /** AttributeProto t */
            t?: (onnx.TensorProto.$Properties|null);

            /** AttributeProto g */
            g?: (onnx.GraphProto.$Properties|null);

            /** AttributeProto sparseTensor */
            sparseTensor?: (onnx.SparseTensorProto.$Properties|null);

            /** AttributeProto tp */
            tp?: (onnx.TypeProto.$Properties|null);

            /** AttributeProto floats */
            floats?: (number[]|null);

            /** AttributeProto ints */
            ints?: ((number|Long)[]|null);

            /** AttributeProto strings */
            strings?: (Uint8Array[]|null);

            /** AttributeProto tensors */
            tensors?: (onnx.TensorProto.$Properties[]|null);

            /** AttributeProto graphs */
            graphs?: (onnx.GraphProto.$Properties[]|null);

            /** AttributeProto sparseTensors */
            sparseTensors?: (onnx.SparseTensorProto.$Properties[]|null);

            /** AttributeProto typeProtos */
            typeProtos?: (onnx.TypeProto.$Properties[]|null);

            /** Unknown fields preserved while decoding when enabled */
            $unknowns?: Uint8Array[];
        }

        /** Shape of an AttributeProto. */
        type $Shape = {
          name?: string|null;
          refAttrName?: string|null;
          docString?: string|null;
          type?: onnx.AttributeProto.AttributeType|null;
          f?: number|null;
          i?: number|Long|null;
          s?: Uint8Array|null;
          t?: onnx.TensorProto.$Shape|null;
          g?: onnx.GraphProto.$Shape|null;
          sparseTensor?: onnx.SparseTensorProto.$Shape|null;
          tp?: onnx.TypeProto.$Shape|null;
          floats?: number[]|null;
          ints?: (number|Long)[]|null;
          strings?: Uint8Array[]|null;
          tensors?: onnx.TensorProto.$Shape[]|null;
          graphs?: onnx.GraphProto.$Shape[]|null;
          sparseTensors?: onnx.SparseTensorProto.$Shape[]|null;
          typeProtos?: onnx.TypeProto.$Shape[]|null;
          $unknowns?: Uint8Array[];
        };

        /** AttributeType enum. */
        enum AttributeType {

            /** UNDEFINED value */
            UNDEFINED = 0,

            /** FLOAT value */
            FLOAT = 1,

            /** INT value */
            INT = 2,

            /** STRING value */
            STRING = 3,

            /** TENSOR value */
            TENSOR = 4,

            /** GRAPH value */
            GRAPH = 5,

            /** SPARSE_TENSOR value */
            SPARSE_TENSOR = 11,

            /** TYPE_PROTO value */
            TYPE_PROTO = 13,

            /** FLOATS value */
            FLOATS = 6,

            /** INTS value */
            INTS = 7,

            /** STRINGS value */
            STRINGS = 8,

            /** TENSORS value */
            TENSORS = 9,

            /** GRAPHS value */
            GRAPHS = 10,

            /** SPARSE_TENSORS value */
            SPARSE_TENSORS = 12,

            /** TYPE_PROTOS value */
            TYPE_PROTOS = 14
        }
    }

    /**
     * Properties of a ValueInfoProto.
     * @deprecated Use onnx.ValueInfoProto.$Properties instead.
     */
    interface IValueInfoProto extends onnx.ValueInfoProto.$Properties {
    }

    /** Represents a ValueInfoProto. */
    class ValueInfoProto {

        /**
         * Constructs a new ValueInfoProto.
         * @param [properties] Properties to set
         */
        constructor(properties?: onnx.ValueInfoProto.$Properties);

        /** Unknown fields preserved while decoding when enabled */
        $unknowns?: Uint8Array[];

        /** ValueInfoProto name. */
        name: string;

        /** ValueInfoProto type. */
        type?: (onnx.TypeProto.$Properties|null);

        /** ValueInfoProto docString. */
        docString: string;

        /** ValueInfoProto metadataProps. */
        metadataProps: onnx.StringStringEntryProto.$Properties[];

        /**
         * Creates a new ValueInfoProto instance using the specified properties.
         * @param [properties] Properties to set
         * @returns ValueInfoProto instance
         */
        static create(properties: onnx.ValueInfoProto.$Shape): onnx.ValueInfoProto & onnx.ValueInfoProto.$Shape;
        static create(properties?: onnx.ValueInfoProto.$Properties): onnx.ValueInfoProto;

        /**
         * Encodes the specified ValueInfoProto message. Does not implicitly {@link onnx.ValueInfoProto.verify|verify} messages.
         * @param message ValueInfoProto message or plain object to encode
         * @param [writer] Writer to encode to
         * @returns Writer
         */
        static encode(message: onnx.ValueInfoProto.$Properties, writer?: $protobuf.Writer): $protobuf.Writer;

        /**
         * Encodes the specified ValueInfoProto message, length delimited. Does not implicitly {@link onnx.ValueInfoProto.verify|verify} messages.
         * @param message ValueInfoProto message or plain object to encode
         * @param [writer] Writer to encode to
         * @returns Writer
         */
        static encodeDelimited(message: onnx.ValueInfoProto.$Properties, writer?: $protobuf.Writer): $protobuf.Writer;

        /**
         * Decodes a ValueInfoProto message from the specified reader or buffer.
         * @param reader Reader or buffer to decode from
         * @param [length] Message length if known beforehand
         * @returns {onnx.ValueInfoProto & onnx.ValueInfoProto.$Shape} ValueInfoProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): onnx.ValueInfoProto & onnx.ValueInfoProto.$Shape;

        /**
         * Decodes a ValueInfoProto message from the specified reader or buffer, length delimited.
         * @param reader Reader or buffer to decode from
         * @returns {onnx.ValueInfoProto & onnx.ValueInfoProto.$Shape} ValueInfoProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): onnx.ValueInfoProto & onnx.ValueInfoProto.$Shape;

        /**
         * Verifies a ValueInfoProto message.
         * @param message Plain object to verify
         * @returns `null` if valid, otherwise the reason why it is not
         */
        static verify(message: { [k: string]: any }): (string|null);

        /**
         * Creates a ValueInfoProto message from a plain object. Also converts values to their respective internal types.
         * @param object Plain object
         * @returns ValueInfoProto
         */
        static fromObject(object: { [k: string]: any }): onnx.ValueInfoProto;

        /**
         * Creates a plain object from a ValueInfoProto message. Also converts values to other types if specified.
         * @param message ValueInfoProto
         * @param [options] Conversion options
         * @returns Plain object
         */
        static toObject(message: onnx.ValueInfoProto, options?: $protobuf.IConversionOptions): { [k: string]: any };

        /**
         * Converts this ValueInfoProto to JSON.
         * @returns JSON object
         */
        toJSON(): { [k: string]: any };

        /**
         * Gets the type url for ValueInfoProto
         * @param [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
         * @returns The type url
         */
        static getTypeUrl(prefix?: string): string;
    }

    namespace ValueInfoProto {

        /** Properties of a ValueInfoProto. */
        interface $Properties {

            /** ValueInfoProto name */
            name?: (string|null);

            /** ValueInfoProto type */
            type?: (onnx.TypeProto.$Properties|null);

            /** ValueInfoProto docString */
            docString?: (string|null);

            /** ValueInfoProto metadataProps */
            metadataProps?: (onnx.StringStringEntryProto.$Properties[]|null);

            /** Unknown fields preserved while decoding when enabled */
            $unknowns?: Uint8Array[];
        }

        /** Shape of a ValueInfoProto. */
        type $Shape = {
          name?: string|null;
          type?: onnx.TypeProto.$Shape|null;
          docString?: string|null;
          metadataProps?: onnx.StringStringEntryProto.$Shape[]|null;
          $unknowns?: Uint8Array[];
        };
    }

    /**
     * Properties of a NodeProto.
     * @deprecated Use onnx.NodeProto.$Properties instead.
     */
    interface INodeProto extends onnx.NodeProto.$Properties {
    }

    /** Represents a NodeProto. */
    class NodeProto {

        /**
         * Constructs a new NodeProto.
         * @param [properties] Properties to set
         */
        constructor(properties?: onnx.NodeProto.$Properties);

        /** Unknown fields preserved while decoding when enabled */
        $unknowns?: Uint8Array[];

        /** NodeProto input. */
        input: string[];

        /** NodeProto output. */
        output: string[];

        /** NodeProto name. */
        name: string;

        /** NodeProto opType. */
        opType: string;

        /** NodeProto domain. */
        domain: string;

        /** NodeProto overload. */
        overload: string;

        /** NodeProto attribute. */
        attribute: onnx.AttributeProto.$Properties[];

        /** NodeProto docString. */
        docString: string;

        /** NodeProto metadataProps. */
        metadataProps: onnx.StringStringEntryProto.$Properties[];

        /**
         * Creates a new NodeProto instance using the specified properties.
         * @param [properties] Properties to set
         * @returns NodeProto instance
         */
        static create(properties: onnx.NodeProto.$Shape): onnx.NodeProto & onnx.NodeProto.$Shape;
        static create(properties?: onnx.NodeProto.$Properties): onnx.NodeProto;

        /**
         * Encodes the specified NodeProto message. Does not implicitly {@link onnx.NodeProto.verify|verify} messages.
         * @param message NodeProto message or plain object to encode
         * @param [writer] Writer to encode to
         * @returns Writer
         */
        static encode(message: onnx.NodeProto.$Properties, writer?: $protobuf.Writer): $protobuf.Writer;

        /**
         * Encodes the specified NodeProto message, length delimited. Does not implicitly {@link onnx.NodeProto.verify|verify} messages.
         * @param message NodeProto message or plain object to encode
         * @param [writer] Writer to encode to
         * @returns Writer
         */
        static encodeDelimited(message: onnx.NodeProto.$Properties, writer?: $protobuf.Writer): $protobuf.Writer;

        /**
         * Decodes a NodeProto message from the specified reader or buffer.
         * @param reader Reader or buffer to decode from
         * @param [length] Message length if known beforehand
         * @returns {onnx.NodeProto & onnx.NodeProto.$Shape} NodeProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): onnx.NodeProto & onnx.NodeProto.$Shape;

        /**
         * Decodes a NodeProto message from the specified reader or buffer, length delimited.
         * @param reader Reader or buffer to decode from
         * @returns {onnx.NodeProto & onnx.NodeProto.$Shape} NodeProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): onnx.NodeProto & onnx.NodeProto.$Shape;

        /**
         * Verifies a NodeProto message.
         * @param message Plain object to verify
         * @returns `null` if valid, otherwise the reason why it is not
         */
        static verify(message: { [k: string]: any }): (string|null);

        /**
         * Creates a NodeProto message from a plain object. Also converts values to their respective internal types.
         * @param object Plain object
         * @returns NodeProto
         */
        static fromObject(object: { [k: string]: any }): onnx.NodeProto;

        /**
         * Creates a plain object from a NodeProto message. Also converts values to other types if specified.
         * @param message NodeProto
         * @param [options] Conversion options
         * @returns Plain object
         */
        static toObject(message: onnx.NodeProto, options?: $protobuf.IConversionOptions): { [k: string]: any };

        /**
         * Converts this NodeProto to JSON.
         * @returns JSON object
         */
        toJSON(): { [k: string]: any };

        /**
         * Gets the type url for NodeProto
         * @param [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
         * @returns The type url
         */
        static getTypeUrl(prefix?: string): string;
    }

    namespace NodeProto {

        /** Properties of a NodeProto. */
        interface $Properties {

            /** NodeProto input */
            input?: (string[]|null);

            /** NodeProto output */
            output?: (string[]|null);

            /** NodeProto name */
            name?: (string|null);

            /** NodeProto opType */
            opType?: (string|null);

            /** NodeProto domain */
            domain?: (string|null);

            /** NodeProto overload */
            overload?: (string|null);

            /** NodeProto attribute */
            attribute?: (onnx.AttributeProto.$Properties[]|null);

            /** NodeProto docString */
            docString?: (string|null);

            /** NodeProto metadataProps */
            metadataProps?: (onnx.StringStringEntryProto.$Properties[]|null);

            /** Unknown fields preserved while decoding when enabled */
            $unknowns?: Uint8Array[];
        }

        /** Shape of a NodeProto. */
        type $Shape = {
          input?: string[]|null;
          output?: string[]|null;
          name?: string|null;
          opType?: string|null;
          domain?: string|null;
          overload?: string|null;
          attribute?: onnx.AttributeProto.$Shape[]|null;
          docString?: string|null;
          metadataProps?: onnx.StringStringEntryProto.$Shape[]|null;
          $unknowns?: Uint8Array[];
        };
    }

    /**
     * Properties of a TrainingInfoProto.
     * @deprecated Use onnx.TrainingInfoProto.$Properties instead.
     */
    interface ITrainingInfoProto extends onnx.TrainingInfoProto.$Properties {
    }

    /** Represents a TrainingInfoProto. */
    class TrainingInfoProto {

        /**
         * Constructs a new TrainingInfoProto.
         * @param [properties] Properties to set
         */
        constructor(properties?: onnx.TrainingInfoProto.$Properties);

        /** Unknown fields preserved while decoding when enabled */
        $unknowns?: Uint8Array[];

        /** TrainingInfoProto initialization. */
        initialization?: (onnx.GraphProto.$Properties|null);

        /** TrainingInfoProto algorithm. */
        algorithm?: (onnx.GraphProto.$Properties|null);

        /** TrainingInfoProto initializationBinding. */
        initializationBinding: onnx.StringStringEntryProto.$Properties[];

        /** TrainingInfoProto updateBinding. */
        updateBinding: onnx.StringStringEntryProto.$Properties[];

        /**
         * Creates a new TrainingInfoProto instance using the specified properties.
         * @param [properties] Properties to set
         * @returns TrainingInfoProto instance
         */
        static create(properties: onnx.TrainingInfoProto.$Shape): onnx.TrainingInfoProto & onnx.TrainingInfoProto.$Shape;
        static create(properties?: onnx.TrainingInfoProto.$Properties): onnx.TrainingInfoProto;

        /**
         * Encodes the specified TrainingInfoProto message. Does not implicitly {@link onnx.TrainingInfoProto.verify|verify} messages.
         * @param message TrainingInfoProto message or plain object to encode
         * @param [writer] Writer to encode to
         * @returns Writer
         */
        static encode(message: onnx.TrainingInfoProto.$Properties, writer?: $protobuf.Writer): $protobuf.Writer;

        /**
         * Encodes the specified TrainingInfoProto message, length delimited. Does not implicitly {@link onnx.TrainingInfoProto.verify|verify} messages.
         * @param message TrainingInfoProto message or plain object to encode
         * @param [writer] Writer to encode to
         * @returns Writer
         */
        static encodeDelimited(message: onnx.TrainingInfoProto.$Properties, writer?: $protobuf.Writer): $protobuf.Writer;

        /**
         * Decodes a TrainingInfoProto message from the specified reader or buffer.
         * @param reader Reader or buffer to decode from
         * @param [length] Message length if known beforehand
         * @returns {onnx.TrainingInfoProto & onnx.TrainingInfoProto.$Shape} TrainingInfoProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): onnx.TrainingInfoProto & onnx.TrainingInfoProto.$Shape;

        /**
         * Decodes a TrainingInfoProto message from the specified reader or buffer, length delimited.
         * @param reader Reader or buffer to decode from
         * @returns {onnx.TrainingInfoProto & onnx.TrainingInfoProto.$Shape} TrainingInfoProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): onnx.TrainingInfoProto & onnx.TrainingInfoProto.$Shape;

        /**
         * Verifies a TrainingInfoProto message.
         * @param message Plain object to verify
         * @returns `null` if valid, otherwise the reason why it is not
         */
        static verify(message: { [k: string]: any }): (string|null);

        /**
         * Creates a TrainingInfoProto message from a plain object. Also converts values to their respective internal types.
         * @param object Plain object
         * @returns TrainingInfoProto
         */
        static fromObject(object: { [k: string]: any }): onnx.TrainingInfoProto;

        /**
         * Creates a plain object from a TrainingInfoProto message. Also converts values to other types if specified.
         * @param message TrainingInfoProto
         * @param [options] Conversion options
         * @returns Plain object
         */
        static toObject(message: onnx.TrainingInfoProto, options?: $protobuf.IConversionOptions): { [k: string]: any };

        /**
         * Converts this TrainingInfoProto to JSON.
         * @returns JSON object
         */
        toJSON(): { [k: string]: any };

        /**
         * Gets the type url for TrainingInfoProto
         * @param [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
         * @returns The type url
         */
        static getTypeUrl(prefix?: string): string;
    }

    namespace TrainingInfoProto {

        /** Properties of a TrainingInfoProto. */
        interface $Properties {

            /** TrainingInfoProto initialization */
            initialization?: (onnx.GraphProto.$Properties|null);

            /** TrainingInfoProto algorithm */
            algorithm?: (onnx.GraphProto.$Properties|null);

            /** TrainingInfoProto initializationBinding */
            initializationBinding?: (onnx.StringStringEntryProto.$Properties[]|null);

            /** TrainingInfoProto updateBinding */
            updateBinding?: (onnx.StringStringEntryProto.$Properties[]|null);

            /** Unknown fields preserved while decoding when enabled */
            $unknowns?: Uint8Array[];
        }

        /** Shape of a TrainingInfoProto. */
        type $Shape = {
          initialization?: onnx.GraphProto.$Shape|null;
          algorithm?: onnx.GraphProto.$Shape|null;
          initializationBinding?: onnx.StringStringEntryProto.$Shape[]|null;
          updateBinding?: onnx.StringStringEntryProto.$Shape[]|null;
          $unknowns?: Uint8Array[];
        };
    }

    /**
     * Properties of a ModelProto.
     * @deprecated Use onnx.ModelProto.$Properties instead.
     */
    interface IModelProto extends onnx.ModelProto.$Properties {
    }

    /** Represents a ModelProto. */
    class ModelProto {

        /**
         * Constructs a new ModelProto.
         * @param [properties] Properties to set
         */
        constructor(properties?: onnx.ModelProto.$Properties);

        /** Unknown fields preserved while decoding when enabled */
        $unknowns?: Uint8Array[];

        /** ModelProto irVersion. */
        irVersion: (number|Long);

        /** ModelProto opsetImport. */
        opsetImport: onnx.OperatorSetIdProto.$Properties[];

        /** ModelProto producerName. */
        producerName: string;

        /** ModelProto producerVersion. */
        producerVersion: string;

        /** ModelProto domain. */
        domain: string;

        /** ModelProto modelVersion. */
        modelVersion: (number|Long);

        /** ModelProto docString. */
        docString: string;

        /** ModelProto graph. */
        graph?: (onnx.GraphProto.$Properties|null);

        /** ModelProto metadataProps. */
        metadataProps: onnx.StringStringEntryProto.$Properties[];

        /** ModelProto trainingInfo. */
        trainingInfo: onnx.TrainingInfoProto.$Properties[];

        /** ModelProto functions. */
        functions: onnx.FunctionProto.$Properties[];

        /**
         * Creates a new ModelProto instance using the specified properties.
         * @param [properties] Properties to set
         * @returns ModelProto instance
         */
        static create(properties: onnx.ModelProto.$Shape): onnx.ModelProto & onnx.ModelProto.$Shape;
        static create(properties?: onnx.ModelProto.$Properties): onnx.ModelProto;

        /**
         * Encodes the specified ModelProto message. Does not implicitly {@link onnx.ModelProto.verify|verify} messages.
         * @param message ModelProto message or plain object to encode
         * @param [writer] Writer to encode to
         * @returns Writer
         */
        static encode(message: onnx.ModelProto.$Properties, writer?: $protobuf.Writer): $protobuf.Writer;

        /**
         * Encodes the specified ModelProto message, length delimited. Does not implicitly {@link onnx.ModelProto.verify|verify} messages.
         * @param message ModelProto message or plain object to encode
         * @param [writer] Writer to encode to
         * @returns Writer
         */
        static encodeDelimited(message: onnx.ModelProto.$Properties, writer?: $protobuf.Writer): $protobuf.Writer;

        /**
         * Decodes a ModelProto message from the specified reader or buffer.
         * @param reader Reader or buffer to decode from
         * @param [length] Message length if known beforehand
         * @returns {onnx.ModelProto & onnx.ModelProto.$Shape} ModelProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): onnx.ModelProto & onnx.ModelProto.$Shape;

        /**
         * Decodes a ModelProto message from the specified reader or buffer, length delimited.
         * @param reader Reader or buffer to decode from
         * @returns {onnx.ModelProto & onnx.ModelProto.$Shape} ModelProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): onnx.ModelProto & onnx.ModelProto.$Shape;

        /**
         * Verifies a ModelProto message.
         * @param message Plain object to verify
         * @returns `null` if valid, otherwise the reason why it is not
         */
        static verify(message: { [k: string]: any }): (string|null);

        /**
         * Creates a ModelProto message from a plain object. Also converts values to their respective internal types.
         * @param object Plain object
         * @returns ModelProto
         */
        static fromObject(object: { [k: string]: any }): onnx.ModelProto;

        /**
         * Creates a plain object from a ModelProto message. Also converts values to other types if specified.
         * @param message ModelProto
         * @param [options] Conversion options
         * @returns Plain object
         */
        static toObject(message: onnx.ModelProto, options?: $protobuf.IConversionOptions): { [k: string]: any };

        /**
         * Converts this ModelProto to JSON.
         * @returns JSON object
         */
        toJSON(): { [k: string]: any };

        /**
         * Gets the type url for ModelProto
         * @param [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
         * @returns The type url
         */
        static getTypeUrl(prefix?: string): string;
    }

    namespace ModelProto {

        /** Properties of a ModelProto. */
        interface $Properties {

            /** ModelProto irVersion */
            irVersion?: (number|Long|null);

            /** ModelProto opsetImport */
            opsetImport?: (onnx.OperatorSetIdProto.$Properties[]|null);

            /** ModelProto producerName */
            producerName?: (string|null);

            /** ModelProto producerVersion */
            producerVersion?: (string|null);

            /** ModelProto domain */
            domain?: (string|null);

            /** ModelProto modelVersion */
            modelVersion?: (number|Long|null);

            /** ModelProto docString */
            docString?: (string|null);

            /** ModelProto graph */
            graph?: (onnx.GraphProto.$Properties|null);

            /** ModelProto metadataProps */
            metadataProps?: (onnx.StringStringEntryProto.$Properties[]|null);

            /** ModelProto trainingInfo */
            trainingInfo?: (onnx.TrainingInfoProto.$Properties[]|null);

            /** ModelProto functions */
            functions?: (onnx.FunctionProto.$Properties[]|null);

            /** Unknown fields preserved while decoding when enabled */
            $unknowns?: Uint8Array[];
        }

        /** Shape of a ModelProto. */
        type $Shape = {
          irVersion?: number|Long|null;
          opsetImport?: onnx.OperatorSetIdProto.$Shape[]|null;
          producerName?: string|null;
          producerVersion?: string|null;
          domain?: string|null;
          modelVersion?: number|Long|null;
          docString?: string|null;
          graph?: onnx.GraphProto.$Shape|null;
          metadataProps?: onnx.StringStringEntryProto.$Shape[]|null;
          trainingInfo?: onnx.TrainingInfoProto.$Shape[]|null;
          functions?: onnx.FunctionProto.$Shape[]|null;
          $unknowns?: Uint8Array[];
        };
    }

    /**
     * Properties of a StringStringEntryProto.
     * @deprecated Use onnx.StringStringEntryProto.$Properties instead.
     */
    interface IStringStringEntryProto extends onnx.StringStringEntryProto.$Properties {
    }

    /** Represents a StringStringEntryProto. */
    class StringStringEntryProto {

        /**
         * Constructs a new StringStringEntryProto.
         * @param [properties] Properties to set
         */
        constructor(properties?: onnx.StringStringEntryProto.$Properties);

        /** Unknown fields preserved while decoding when enabled */
        $unknowns?: Uint8Array[];

        /** StringStringEntryProto key. */
        key: string;

        /** StringStringEntryProto value. */
        value: string;

        /**
         * Creates a new StringStringEntryProto instance using the specified properties.
         * @param [properties] Properties to set
         * @returns StringStringEntryProto instance
         */
        static create(properties: onnx.StringStringEntryProto.$Shape): onnx.StringStringEntryProto & onnx.StringStringEntryProto.$Shape;
        static create(properties?: onnx.StringStringEntryProto.$Properties): onnx.StringStringEntryProto;

        /**
         * Encodes the specified StringStringEntryProto message. Does not implicitly {@link onnx.StringStringEntryProto.verify|verify} messages.
         * @param message StringStringEntryProto message or plain object to encode
         * @param [writer] Writer to encode to
         * @returns Writer
         */
        static encode(message: onnx.StringStringEntryProto.$Properties, writer?: $protobuf.Writer): $protobuf.Writer;

        /**
         * Encodes the specified StringStringEntryProto message, length delimited. Does not implicitly {@link onnx.StringStringEntryProto.verify|verify} messages.
         * @param message StringStringEntryProto message or plain object to encode
         * @param [writer] Writer to encode to
         * @returns Writer
         */
        static encodeDelimited(message: onnx.StringStringEntryProto.$Properties, writer?: $protobuf.Writer): $protobuf.Writer;

        /**
         * Decodes a StringStringEntryProto message from the specified reader or buffer.
         * @param reader Reader or buffer to decode from
         * @param [length] Message length if known beforehand
         * @returns {onnx.StringStringEntryProto & onnx.StringStringEntryProto.$Shape} StringStringEntryProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): onnx.StringStringEntryProto & onnx.StringStringEntryProto.$Shape;

        /**
         * Decodes a StringStringEntryProto message from the specified reader or buffer, length delimited.
         * @param reader Reader or buffer to decode from
         * @returns {onnx.StringStringEntryProto & onnx.StringStringEntryProto.$Shape} StringStringEntryProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): onnx.StringStringEntryProto & onnx.StringStringEntryProto.$Shape;

        /**
         * Verifies a StringStringEntryProto message.
         * @param message Plain object to verify
         * @returns `null` if valid, otherwise the reason why it is not
         */
        static verify(message: { [k: string]: any }): (string|null);

        /**
         * Creates a StringStringEntryProto message from a plain object. Also converts values to their respective internal types.
         * @param object Plain object
         * @returns StringStringEntryProto
         */
        static fromObject(object: { [k: string]: any }): onnx.StringStringEntryProto;

        /**
         * Creates a plain object from a StringStringEntryProto message. Also converts values to other types if specified.
         * @param message StringStringEntryProto
         * @param [options] Conversion options
         * @returns Plain object
         */
        static toObject(message: onnx.StringStringEntryProto, options?: $protobuf.IConversionOptions): { [k: string]: any };

        /**
         * Converts this StringStringEntryProto to JSON.
         * @returns JSON object
         */
        toJSON(): { [k: string]: any };

        /**
         * Gets the type url for StringStringEntryProto
         * @param [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
         * @returns The type url
         */
        static getTypeUrl(prefix?: string): string;
    }

    namespace StringStringEntryProto {

        /** Properties of a StringStringEntryProto. */
        interface $Properties {

            /** StringStringEntryProto key */
            key?: (string|null);

            /** StringStringEntryProto value */
            value?: (string|null);

            /** Unknown fields preserved while decoding when enabled */
            $unknowns?: Uint8Array[];
        }

        /** Shape of a StringStringEntryProto. */
        type $Shape = onnx.StringStringEntryProto.$Properties;
    }

    /**
     * Properties of a TensorAnnotation.
     * @deprecated Use onnx.TensorAnnotation.$Properties instead.
     */
    interface ITensorAnnotation extends onnx.TensorAnnotation.$Properties {
    }

    /** Represents a TensorAnnotation. */
    class TensorAnnotation {

        /**
         * Constructs a new TensorAnnotation.
         * @param [properties] Properties to set
         */
        constructor(properties?: onnx.TensorAnnotation.$Properties);

        /** Unknown fields preserved while decoding when enabled */
        $unknowns?: Uint8Array[];

        /** TensorAnnotation tensorName. */
        tensorName: string;

        /** TensorAnnotation quantParameterTensorNames. */
        quantParameterTensorNames: onnx.StringStringEntryProto.$Properties[];

        /**
         * Creates a new TensorAnnotation instance using the specified properties.
         * @param [properties] Properties to set
         * @returns TensorAnnotation instance
         */
        static create(properties: onnx.TensorAnnotation.$Shape): onnx.TensorAnnotation & onnx.TensorAnnotation.$Shape;
        static create(properties?: onnx.TensorAnnotation.$Properties): onnx.TensorAnnotation;

        /**
         * Encodes the specified TensorAnnotation message. Does not implicitly {@link onnx.TensorAnnotation.verify|verify} messages.
         * @param message TensorAnnotation message or plain object to encode
         * @param [writer] Writer to encode to
         * @returns Writer
         */
        static encode(message: onnx.TensorAnnotation.$Properties, writer?: $protobuf.Writer): $protobuf.Writer;

        /**
         * Encodes the specified TensorAnnotation message, length delimited. Does not implicitly {@link onnx.TensorAnnotation.verify|verify} messages.
         * @param message TensorAnnotation message or plain object to encode
         * @param [writer] Writer to encode to
         * @returns Writer
         */
        static encodeDelimited(message: onnx.TensorAnnotation.$Properties, writer?: $protobuf.Writer): $protobuf.Writer;

        /**
         * Decodes a TensorAnnotation message from the specified reader or buffer.
         * @param reader Reader or buffer to decode from
         * @param [length] Message length if known beforehand
         * @returns {onnx.TensorAnnotation & onnx.TensorAnnotation.$Shape} TensorAnnotation
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): onnx.TensorAnnotation & onnx.TensorAnnotation.$Shape;

        /**
         * Decodes a TensorAnnotation message from the specified reader or buffer, length delimited.
         * @param reader Reader or buffer to decode from
         * @returns {onnx.TensorAnnotation & onnx.TensorAnnotation.$Shape} TensorAnnotation
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): onnx.TensorAnnotation & onnx.TensorAnnotation.$Shape;

        /**
         * Verifies a TensorAnnotation message.
         * @param message Plain object to verify
         * @returns `null` if valid, otherwise the reason why it is not
         */
        static verify(message: { [k: string]: any }): (string|null);

        /**
         * Creates a TensorAnnotation message from a plain object. Also converts values to their respective internal types.
         * @param object Plain object
         * @returns TensorAnnotation
         */
        static fromObject(object: { [k: string]: any }): onnx.TensorAnnotation;

        /**
         * Creates a plain object from a TensorAnnotation message. Also converts values to other types if specified.
         * @param message TensorAnnotation
         * @param [options] Conversion options
         * @returns Plain object
         */
        static toObject(message: onnx.TensorAnnotation, options?: $protobuf.IConversionOptions): { [k: string]: any };

        /**
         * Converts this TensorAnnotation to JSON.
         * @returns JSON object
         */
        toJSON(): { [k: string]: any };

        /**
         * Gets the type url for TensorAnnotation
         * @param [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
         * @returns The type url
         */
        static getTypeUrl(prefix?: string): string;
    }

    namespace TensorAnnotation {

        /** Properties of a TensorAnnotation. */
        interface $Properties {

            /** TensorAnnotation tensorName */
            tensorName?: (string|null);

            /** TensorAnnotation quantParameterTensorNames */
            quantParameterTensorNames?: (onnx.StringStringEntryProto.$Properties[]|null);

            /** Unknown fields preserved while decoding when enabled */
            $unknowns?: Uint8Array[];
        }

        /** Shape of a TensorAnnotation. */
        type $Shape = onnx.TensorAnnotation.$Properties;
    }

    /**
     * Properties of a GraphProto.
     * @deprecated Use onnx.GraphProto.$Properties instead.
     */
    interface IGraphProto extends onnx.GraphProto.$Properties {
    }

    /** Represents a GraphProto. */
    class GraphProto {

        /**
         * Constructs a new GraphProto.
         * @param [properties] Properties to set
         */
        constructor(properties?: onnx.GraphProto.$Properties);

        /** Unknown fields preserved while decoding when enabled */
        $unknowns?: Uint8Array[];

        /** GraphProto node. */
        node: onnx.NodeProto.$Properties[];

        /** GraphProto name. */
        name: string;

        /** GraphProto initializer. */
        initializer: onnx.TensorProto.$Properties[];

        /** GraphProto sparseInitializer. */
        sparseInitializer: onnx.SparseTensorProto.$Properties[];

        /** GraphProto docString. */
        docString: string;

        /** GraphProto input. */
        input: onnx.ValueInfoProto.$Properties[];

        /** GraphProto output. */
        output: onnx.ValueInfoProto.$Properties[];

        /** GraphProto valueInfo. */
        valueInfo: onnx.ValueInfoProto.$Properties[];

        /** GraphProto quantizationAnnotation. */
        quantizationAnnotation: onnx.TensorAnnotation.$Properties[];

        /** GraphProto metadataProps. */
        metadataProps: onnx.StringStringEntryProto.$Properties[];

        /**
         * Creates a new GraphProto instance using the specified properties.
         * @param [properties] Properties to set
         * @returns GraphProto instance
         */
        static create(properties: onnx.GraphProto.$Shape): onnx.GraphProto & onnx.GraphProto.$Shape;
        static create(properties?: onnx.GraphProto.$Properties): onnx.GraphProto;

        /**
         * Encodes the specified GraphProto message. Does not implicitly {@link onnx.GraphProto.verify|verify} messages.
         * @param message GraphProto message or plain object to encode
         * @param [writer] Writer to encode to
         * @returns Writer
         */
        static encode(message: onnx.GraphProto.$Properties, writer?: $protobuf.Writer): $protobuf.Writer;

        /**
         * Encodes the specified GraphProto message, length delimited. Does not implicitly {@link onnx.GraphProto.verify|verify} messages.
         * @param message GraphProto message or plain object to encode
         * @param [writer] Writer to encode to
         * @returns Writer
         */
        static encodeDelimited(message: onnx.GraphProto.$Properties, writer?: $protobuf.Writer): $protobuf.Writer;

        /**
         * Decodes a GraphProto message from the specified reader or buffer.
         * @param reader Reader or buffer to decode from
         * @param [length] Message length if known beforehand
         * @returns {onnx.GraphProto & onnx.GraphProto.$Shape} GraphProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): onnx.GraphProto & onnx.GraphProto.$Shape;

        /**
         * Decodes a GraphProto message from the specified reader or buffer, length delimited.
         * @param reader Reader or buffer to decode from
         * @returns {onnx.GraphProto & onnx.GraphProto.$Shape} GraphProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): onnx.GraphProto & onnx.GraphProto.$Shape;

        /**
         * Verifies a GraphProto message.
         * @param message Plain object to verify
         * @returns `null` if valid, otherwise the reason why it is not
         */
        static verify(message: { [k: string]: any }): (string|null);

        /**
         * Creates a GraphProto message from a plain object. Also converts values to their respective internal types.
         * @param object Plain object
         * @returns GraphProto
         */
        static fromObject(object: { [k: string]: any }): onnx.GraphProto;

        /**
         * Creates a plain object from a GraphProto message. Also converts values to other types if specified.
         * @param message GraphProto
         * @param [options] Conversion options
         * @returns Plain object
         */
        static toObject(message: onnx.GraphProto, options?: $protobuf.IConversionOptions): { [k: string]: any };

        /**
         * Converts this GraphProto to JSON.
         * @returns JSON object
         */
        toJSON(): { [k: string]: any };

        /**
         * Gets the type url for GraphProto
         * @param [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
         * @returns The type url
         */
        static getTypeUrl(prefix?: string): string;
    }

    namespace GraphProto {

        /** Properties of a GraphProto. */
        interface $Properties {

            /** GraphProto node */
            node?: (onnx.NodeProto.$Properties[]|null);

            /** GraphProto name */
            name?: (string|null);

            /** GraphProto initializer */
            initializer?: (onnx.TensorProto.$Properties[]|null);

            /** GraphProto sparseInitializer */
            sparseInitializer?: (onnx.SparseTensorProto.$Properties[]|null);

            /** GraphProto docString */
            docString?: (string|null);

            /** GraphProto input */
            input?: (onnx.ValueInfoProto.$Properties[]|null);

            /** GraphProto output */
            output?: (onnx.ValueInfoProto.$Properties[]|null);

            /** GraphProto valueInfo */
            valueInfo?: (onnx.ValueInfoProto.$Properties[]|null);

            /** GraphProto quantizationAnnotation */
            quantizationAnnotation?: (onnx.TensorAnnotation.$Properties[]|null);

            /** GraphProto metadataProps */
            metadataProps?: (onnx.StringStringEntryProto.$Properties[]|null);

            /** Unknown fields preserved while decoding when enabled */
            $unknowns?: Uint8Array[];
        }

        /** Shape of a GraphProto. */
        type $Shape = {
          node?: onnx.NodeProto.$Shape[]|null;
          name?: string|null;
          initializer?: onnx.TensorProto.$Shape[]|null;
          sparseInitializer?: onnx.SparseTensorProto.$Shape[]|null;
          docString?: string|null;
          input?: onnx.ValueInfoProto.$Shape[]|null;
          output?: onnx.ValueInfoProto.$Shape[]|null;
          valueInfo?: onnx.ValueInfoProto.$Shape[]|null;
          quantizationAnnotation?: onnx.TensorAnnotation.$Shape[]|null;
          metadataProps?: onnx.StringStringEntryProto.$Shape[]|null;
          $unknowns?: Uint8Array[];
        };
    }

    /**
     * Properties of a TensorProto.
     * @deprecated Use onnx.TensorProto.$Properties instead.
     */
    interface ITensorProto extends onnx.TensorProto.$Properties {
    }

    /** Represents a TensorProto. */
    class TensorProto {

        /**
         * Constructs a new TensorProto.
         * @param [properties] Properties to set
         */
        constructor(properties?: onnx.TensorProto.$Properties);

        /** Unknown fields preserved while decoding when enabled */
        $unknowns?: Uint8Array[];

        /** TensorProto dims. */
        dims: (number|Long)[];

        /** TensorProto dataType. */
        dataType: number;

        /** TensorProto segment. */
        segment?: (onnx.TensorProto.Segment.$Properties|null);

        /** TensorProto floatData. */
        floatData: number[];

        /** TensorProto int32Data. */
        int32Data: number[];

        /** TensorProto stringData. */
        stringData: Uint8Array[];

        /** TensorProto int64Data. */
        int64Data: (number|Long)[];

        /** TensorProto name. */
        name: string;

        /** TensorProto docString. */
        docString: string;

        /** TensorProto rawData. */
        rawData: Uint8Array;

        /** TensorProto externalData. */
        externalData: onnx.StringStringEntryProto.$Properties[];

        /** TensorProto dataLocation. */
        dataLocation: onnx.TensorProto.DataLocation;

        /** TensorProto doubleData. */
        doubleData: number[];

        /** TensorProto uint64Data. */
        uint64Data: (number|Long)[];

        /** TensorProto metadataProps. */
        metadataProps: onnx.StringStringEntryProto.$Properties[];

        /**
         * Creates a new TensorProto instance using the specified properties.
         * @param [properties] Properties to set
         * @returns TensorProto instance
         */
        static create(properties: onnx.TensorProto.$Shape): onnx.TensorProto & onnx.TensorProto.$Shape;
        static create(properties?: onnx.TensorProto.$Properties): onnx.TensorProto;

        /**
         * Encodes the specified TensorProto message. Does not implicitly {@link onnx.TensorProto.verify|verify} messages.
         * @param message TensorProto message or plain object to encode
         * @param [writer] Writer to encode to
         * @returns Writer
         */
        static encode(message: onnx.TensorProto.$Properties, writer?: $protobuf.Writer): $protobuf.Writer;

        /**
         * Encodes the specified TensorProto message, length delimited. Does not implicitly {@link onnx.TensorProto.verify|verify} messages.
         * @param message TensorProto message or plain object to encode
         * @param [writer] Writer to encode to
         * @returns Writer
         */
        static encodeDelimited(message: onnx.TensorProto.$Properties, writer?: $protobuf.Writer): $protobuf.Writer;

        /**
         * Decodes a TensorProto message from the specified reader or buffer.
         * @param reader Reader or buffer to decode from
         * @param [length] Message length if known beforehand
         * @returns {onnx.TensorProto & onnx.TensorProto.$Shape} TensorProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): onnx.TensorProto & onnx.TensorProto.$Shape;

        /**
         * Decodes a TensorProto message from the specified reader or buffer, length delimited.
         * @param reader Reader or buffer to decode from
         * @returns {onnx.TensorProto & onnx.TensorProto.$Shape} TensorProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): onnx.TensorProto & onnx.TensorProto.$Shape;

        /**
         * Verifies a TensorProto message.
         * @param message Plain object to verify
         * @returns `null` if valid, otherwise the reason why it is not
         */
        static verify(message: { [k: string]: any }): (string|null);

        /**
         * Creates a TensorProto message from a plain object. Also converts values to their respective internal types.
         * @param object Plain object
         * @returns TensorProto
         */
        static fromObject(object: { [k: string]: any }): onnx.TensorProto;

        /**
         * Creates a plain object from a TensorProto message. Also converts values to other types if specified.
         * @param message TensorProto
         * @param [options] Conversion options
         * @returns Plain object
         */
        static toObject(message: onnx.TensorProto, options?: $protobuf.IConversionOptions): { [k: string]: any };

        /**
         * Converts this TensorProto to JSON.
         * @returns JSON object
         */
        toJSON(): { [k: string]: any };

        /**
         * Gets the type url for TensorProto
         * @param [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
         * @returns The type url
         */
        static getTypeUrl(prefix?: string): string;
    }

    namespace TensorProto {

        /** Properties of a TensorProto. */
        interface $Properties {

            /** TensorProto dims */
            dims?: ((number|Long)[]|null);

            /** TensorProto dataType */
            dataType?: (number|null);

            /** TensorProto segment */
            segment?: (onnx.TensorProto.Segment.$Properties|null);

            /** TensorProto floatData */
            floatData?: (number[]|null);

            /** TensorProto int32Data */
            int32Data?: (number[]|null);

            /** TensorProto stringData */
            stringData?: (Uint8Array[]|null);

            /** TensorProto int64Data */
            int64Data?: ((number|Long)[]|null);

            /** TensorProto name */
            name?: (string|null);

            /** TensorProto docString */
            docString?: (string|null);

            /** TensorProto rawData */
            rawData?: (Uint8Array|null);

            /** TensorProto externalData */
            externalData?: (onnx.StringStringEntryProto.$Properties[]|null);

            /** TensorProto dataLocation */
            dataLocation?: (onnx.TensorProto.DataLocation|null);

            /** TensorProto doubleData */
            doubleData?: (number[]|null);

            /** TensorProto uint64Data */
            uint64Data?: ((number|Long)[]|null);

            /** TensorProto metadataProps */
            metadataProps?: (onnx.StringStringEntryProto.$Properties[]|null);

            /** Unknown fields preserved while decoding when enabled */
            $unknowns?: Uint8Array[];
        }

        /** Shape of a TensorProto. */
        type $Shape = onnx.TensorProto.$Properties;

        /** DataType enum. */
        enum DataType {

            /** UNDEFINED value */
            UNDEFINED = 0,

            /** FLOAT value */
            FLOAT = 1,

            /** UINT8 value */
            UINT8 = 2,

            /** INT8 value */
            INT8 = 3,

            /** UINT16 value */
            UINT16 = 4,

            /** INT16 value */
            INT16 = 5,

            /** INT32 value */
            INT32 = 6,

            /** INT64 value */
            INT64 = 7,

            /** STRING value */
            STRING = 8,

            /** BOOL value */
            BOOL = 9,

            /** FLOAT16 value */
            FLOAT16 = 10,

            /** DOUBLE value */
            DOUBLE = 11,

            /** UINT32 value */
            UINT32 = 12,

            /** UINT64 value */
            UINT64 = 13,

            /** COMPLEX64 value */
            COMPLEX64 = 14,

            /** COMPLEX128 value */
            COMPLEX128 = 15,

            /** BFLOAT16 value */
            BFLOAT16 = 16,

            /** FLOAT8E4M3FN value */
            FLOAT8E4M3FN = 17,

            /** FLOAT8E4M3FNUZ value */
            FLOAT8E4M3FNUZ = 18,

            /** FLOAT8E5M2 value */
            FLOAT8E5M2 = 19,

            /** FLOAT8E5M2FNUZ value */
            FLOAT8E5M2FNUZ = 20,

            /** UINT4 value */
            UINT4 = 21,

            /** INT4 value */
            INT4 = 22
        }

        /**
         * Properties of a Segment.
         * @deprecated Use onnx.TensorProto.Segment.$Properties instead.
         */
        interface ISegment extends onnx.TensorProto.Segment.$Properties {
        }

        /** Represents a Segment. */
        class Segment {

            /**
             * Constructs a new Segment.
             * @param [properties] Properties to set
             */
            constructor(properties?: onnx.TensorProto.Segment.$Properties);

            /** Unknown fields preserved while decoding when enabled */
            $unknowns?: Uint8Array[];

            /** Segment begin. */
            begin: (number|Long);

            /** Segment end. */
            end: (number|Long);

            /**
             * Creates a new Segment instance using the specified properties.
             * @param [properties] Properties to set
             * @returns Segment instance
             */
            static create(properties: onnx.TensorProto.Segment.$Shape): onnx.TensorProto.Segment & onnx.TensorProto.Segment.$Shape;
            static create(properties?: onnx.TensorProto.Segment.$Properties): onnx.TensorProto.Segment;

            /**
             * Encodes the specified Segment message. Does not implicitly {@link onnx.TensorProto.Segment.verify|verify} messages.
             * @param message Segment message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            static encode(message: onnx.TensorProto.Segment.$Properties, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified Segment message, length delimited. Does not implicitly {@link onnx.TensorProto.Segment.verify|verify} messages.
             * @param message Segment message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            static encodeDelimited(message: onnx.TensorProto.Segment.$Properties, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a Segment message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns {onnx.TensorProto.Segment & onnx.TensorProto.Segment.$Shape} Segment
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): onnx.TensorProto.Segment & onnx.TensorProto.Segment.$Shape;

            /**
             * Decodes a Segment message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns {onnx.TensorProto.Segment & onnx.TensorProto.Segment.$Shape} Segment
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): onnx.TensorProto.Segment & onnx.TensorProto.Segment.$Shape;

            /**
             * Verifies a Segment message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates a Segment message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns Segment
             */
            static fromObject(object: { [k: string]: any }): onnx.TensorProto.Segment;

            /**
             * Creates a plain object from a Segment message. Also converts values to other types if specified.
             * @param message Segment
             * @param [options] Conversion options
             * @returns Plain object
             */
            static toObject(message: onnx.TensorProto.Segment, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this Segment to JSON.
             * @returns JSON object
             */
            toJSON(): { [k: string]: any };

            /**
             * Gets the type url for Segment
             * @param [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
             * @returns The type url
             */
            static getTypeUrl(prefix?: string): string;
        }

        namespace Segment {

            /** Properties of a Segment. */
            interface $Properties {

                /** Segment begin */
                begin?: (number|Long|null);

                /** Segment end */
                end?: (number|Long|null);

                /** Unknown fields preserved while decoding when enabled */
                $unknowns?: Uint8Array[];
            }

            /** Shape of a Segment. */
            type $Shape = onnx.TensorProto.Segment.$Properties;
        }

        /** DataLocation enum. */
        enum DataLocation {

            /** DEFAULT value */
            DEFAULT = 0,

            /** EXTERNAL value */
            EXTERNAL = 1
        }
    }

    /**
     * Properties of a SparseTensorProto.
     * @deprecated Use onnx.SparseTensorProto.$Properties instead.
     */
    interface ISparseTensorProto extends onnx.SparseTensorProto.$Properties {
    }

    /** Represents a SparseTensorProto. */
    class SparseTensorProto {

        /**
         * Constructs a new SparseTensorProto.
         * @param [properties] Properties to set
         */
        constructor(properties?: onnx.SparseTensorProto.$Properties);

        /** Unknown fields preserved while decoding when enabled */
        $unknowns?: Uint8Array[];

        /** SparseTensorProto values. */
        values?: (onnx.TensorProto.$Properties|null);

        /** SparseTensorProto indices. */
        indices?: (onnx.TensorProto.$Properties|null);

        /** SparseTensorProto dims. */
        dims: (number|Long)[];

        /**
         * Creates a new SparseTensorProto instance using the specified properties.
         * @param [properties] Properties to set
         * @returns SparseTensorProto instance
         */
        static create(properties: onnx.SparseTensorProto.$Shape): onnx.SparseTensorProto & onnx.SparseTensorProto.$Shape;
        static create(properties?: onnx.SparseTensorProto.$Properties): onnx.SparseTensorProto;

        /**
         * Encodes the specified SparseTensorProto message. Does not implicitly {@link onnx.SparseTensorProto.verify|verify} messages.
         * @param message SparseTensorProto message or plain object to encode
         * @param [writer] Writer to encode to
         * @returns Writer
         */
        static encode(message: onnx.SparseTensorProto.$Properties, writer?: $protobuf.Writer): $protobuf.Writer;

        /**
         * Encodes the specified SparseTensorProto message, length delimited. Does not implicitly {@link onnx.SparseTensorProto.verify|verify} messages.
         * @param message SparseTensorProto message or plain object to encode
         * @param [writer] Writer to encode to
         * @returns Writer
         */
        static encodeDelimited(message: onnx.SparseTensorProto.$Properties, writer?: $protobuf.Writer): $protobuf.Writer;

        /**
         * Decodes a SparseTensorProto message from the specified reader or buffer.
         * @param reader Reader or buffer to decode from
         * @param [length] Message length if known beforehand
         * @returns {onnx.SparseTensorProto & onnx.SparseTensorProto.$Shape} SparseTensorProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): onnx.SparseTensorProto & onnx.SparseTensorProto.$Shape;

        /**
         * Decodes a SparseTensorProto message from the specified reader or buffer, length delimited.
         * @param reader Reader or buffer to decode from
         * @returns {onnx.SparseTensorProto & onnx.SparseTensorProto.$Shape} SparseTensorProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): onnx.SparseTensorProto & onnx.SparseTensorProto.$Shape;

        /**
         * Verifies a SparseTensorProto message.
         * @param message Plain object to verify
         * @returns `null` if valid, otherwise the reason why it is not
         */
        static verify(message: { [k: string]: any }): (string|null);

        /**
         * Creates a SparseTensorProto message from a plain object. Also converts values to their respective internal types.
         * @param object Plain object
         * @returns SparseTensorProto
         */
        static fromObject(object: { [k: string]: any }): onnx.SparseTensorProto;

        /**
         * Creates a plain object from a SparseTensorProto message. Also converts values to other types if specified.
         * @param message SparseTensorProto
         * @param [options] Conversion options
         * @returns Plain object
         */
        static toObject(message: onnx.SparseTensorProto, options?: $protobuf.IConversionOptions): { [k: string]: any };

        /**
         * Converts this SparseTensorProto to JSON.
         * @returns JSON object
         */
        toJSON(): { [k: string]: any };

        /**
         * Gets the type url for SparseTensorProto
         * @param [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
         * @returns The type url
         */
        static getTypeUrl(prefix?: string): string;
    }

    namespace SparseTensorProto {

        /** Properties of a SparseTensorProto. */
        interface $Properties {

            /** SparseTensorProto values */
            values?: (onnx.TensorProto.$Properties|null);

            /** SparseTensorProto indices */
            indices?: (onnx.TensorProto.$Properties|null);

            /** SparseTensorProto dims */
            dims?: ((number|Long)[]|null);

            /** Unknown fields preserved while decoding when enabled */
            $unknowns?: Uint8Array[];
        }

        /** Shape of a SparseTensorProto. */
        type $Shape = onnx.SparseTensorProto.$Properties;
    }

    /**
     * Properties of a TensorShapeProto.
     * @deprecated Use onnx.TensorShapeProto.$Properties instead.
     */
    interface ITensorShapeProto extends onnx.TensorShapeProto.$Properties {
    }

    /** Represents a TensorShapeProto. */
    class TensorShapeProto {

        /**
         * Constructs a new TensorShapeProto.
         * @param [properties] Properties to set
         */
        constructor(properties?: onnx.TensorShapeProto.$Properties);

        /** Unknown fields preserved while decoding when enabled */
        $unknowns?: Uint8Array[];

        /** TensorShapeProto dim. */
        dim: onnx.TensorShapeProto.Dimension.$Properties[];

        /**
         * Creates a new TensorShapeProto instance using the specified properties.
         * @param [properties] Properties to set
         * @returns TensorShapeProto instance
         */
        static create(properties: onnx.TensorShapeProto.$Shape): onnx.TensorShapeProto & onnx.TensorShapeProto.$Shape;
        static create(properties?: onnx.TensorShapeProto.$Properties): onnx.TensorShapeProto;

        /**
         * Encodes the specified TensorShapeProto message. Does not implicitly {@link onnx.TensorShapeProto.verify|verify} messages.
         * @param message TensorShapeProto message or plain object to encode
         * @param [writer] Writer to encode to
         * @returns Writer
         */
        static encode(message: onnx.TensorShapeProto.$Properties, writer?: $protobuf.Writer): $protobuf.Writer;

        /**
         * Encodes the specified TensorShapeProto message, length delimited. Does not implicitly {@link onnx.TensorShapeProto.verify|verify} messages.
         * @param message TensorShapeProto message or plain object to encode
         * @param [writer] Writer to encode to
         * @returns Writer
         */
        static encodeDelimited(message: onnx.TensorShapeProto.$Properties, writer?: $protobuf.Writer): $protobuf.Writer;

        /**
         * Decodes a TensorShapeProto message from the specified reader or buffer.
         * @param reader Reader or buffer to decode from
         * @param [length] Message length if known beforehand
         * @returns {onnx.TensorShapeProto & onnx.TensorShapeProto.$Shape} TensorShapeProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): onnx.TensorShapeProto & onnx.TensorShapeProto.$Shape;

        /**
         * Decodes a TensorShapeProto message from the specified reader or buffer, length delimited.
         * @param reader Reader or buffer to decode from
         * @returns {onnx.TensorShapeProto & onnx.TensorShapeProto.$Shape} TensorShapeProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): onnx.TensorShapeProto & onnx.TensorShapeProto.$Shape;

        /**
         * Verifies a TensorShapeProto message.
         * @param message Plain object to verify
         * @returns `null` if valid, otherwise the reason why it is not
         */
        static verify(message: { [k: string]: any }): (string|null);

        /**
         * Creates a TensorShapeProto message from a plain object. Also converts values to their respective internal types.
         * @param object Plain object
         * @returns TensorShapeProto
         */
        static fromObject(object: { [k: string]: any }): onnx.TensorShapeProto;

        /**
         * Creates a plain object from a TensorShapeProto message. Also converts values to other types if specified.
         * @param message TensorShapeProto
         * @param [options] Conversion options
         * @returns Plain object
         */
        static toObject(message: onnx.TensorShapeProto, options?: $protobuf.IConversionOptions): { [k: string]: any };

        /**
         * Converts this TensorShapeProto to JSON.
         * @returns JSON object
         */
        toJSON(): { [k: string]: any };

        /**
         * Gets the type url for TensorShapeProto
         * @param [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
         * @returns The type url
         */
        static getTypeUrl(prefix?: string): string;
    }

    namespace TensorShapeProto {

        /** Properties of a TensorShapeProto. */
        interface $Properties {

            /** TensorShapeProto dim */
            dim?: (onnx.TensorShapeProto.Dimension.$Properties[]|null);

            /** Unknown fields preserved while decoding when enabled */
            $unknowns?: Uint8Array[];
        }

        /** Shape of a TensorShapeProto. */
        type $Shape = {
          dim?: onnx.TensorShapeProto.Dimension.$Shape[]|null;
          $unknowns?: Uint8Array[];
        };

        /**
         * Properties of a Dimension.
         * @deprecated Use onnx.TensorShapeProto.Dimension.$Properties instead.
         */
        interface IDimension extends onnx.TensorShapeProto.Dimension.$Properties {
        }

        /** Represents a Dimension. */
        class Dimension {

            /**
             * Constructs a new Dimension.
             * @param [properties] Properties to set
             */
            constructor(properties?: onnx.TensorShapeProto.Dimension.$Properties);

            /** Unknown fields preserved while decoding when enabled */
            $unknowns?: Uint8Array[];

            /** Dimension dimValue. */
            dimValue?: (number|Long|null);

            /** Dimension dimParam. */
            dimParam?: (string|null);

            /** Dimension denotation. */
            denotation: string;

            /** Dimension value. */
            value?: ("dimValue"|"dimParam");

            /**
             * Creates a new Dimension instance using the specified properties.
             * @param [properties] Properties to set
             * @returns Dimension instance
             */
            static create(properties: onnx.TensorShapeProto.Dimension.$Shape): onnx.TensorShapeProto.Dimension & onnx.TensorShapeProto.Dimension.$Shape;
            static create(properties?: onnx.TensorShapeProto.Dimension.$Properties): onnx.TensorShapeProto.Dimension;

            /**
             * Encodes the specified Dimension message. Does not implicitly {@link onnx.TensorShapeProto.Dimension.verify|verify} messages.
             * @param message Dimension message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            static encode(message: onnx.TensorShapeProto.Dimension.$Properties, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified Dimension message, length delimited. Does not implicitly {@link onnx.TensorShapeProto.Dimension.verify|verify} messages.
             * @param message Dimension message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            static encodeDelimited(message: onnx.TensorShapeProto.Dimension.$Properties, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a Dimension message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns {onnx.TensorShapeProto.Dimension & onnx.TensorShapeProto.Dimension.$Shape} Dimension
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): onnx.TensorShapeProto.Dimension & onnx.TensorShapeProto.Dimension.$Shape;

            /**
             * Decodes a Dimension message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns {onnx.TensorShapeProto.Dimension & onnx.TensorShapeProto.Dimension.$Shape} Dimension
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): onnx.TensorShapeProto.Dimension & onnx.TensorShapeProto.Dimension.$Shape;

            /**
             * Verifies a Dimension message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates a Dimension message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns Dimension
             */
            static fromObject(object: { [k: string]: any }): onnx.TensorShapeProto.Dimension;

            /**
             * Creates a plain object from a Dimension message. Also converts values to other types if specified.
             * @param message Dimension
             * @param [options] Conversion options
             * @returns Plain object
             */
            static toObject(message: onnx.TensorShapeProto.Dimension, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this Dimension to JSON.
             * @returns JSON object
             */
            toJSON(): { [k: string]: any };

            /**
             * Gets the type url for Dimension
             * @param [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
             * @returns The type url
             */
            static getTypeUrl(prefix?: string): string;
        }

        namespace Dimension {

            /** Properties of a Dimension. */
            interface $Properties {

                /** Dimension dimValue */
                dimValue?: (number|Long|null);

                /** Dimension dimParam */
                dimParam?: (string|null);

                /** Dimension denotation */
                denotation?: (string|null);

                /** Dimension value */
                value?: ("dimValue"|"dimParam");

                /** Unknown fields preserved while decoding when enabled */
                $unknowns?: Uint8Array[];
            }

            /** Narrowed shape of a Dimension. */
            type $Shape = {
              dimValue?: number|Long|null;
              dimParam?: string|null;
              denotation?: string|null;
              $unknowns?: Uint8Array[];
            } & (
              ({ value?: undefined; dimValue?: null; dimParam?: null }|{ value?: "dimValue"; dimValue: number|Long; dimParam?: null }|{ value?: "dimParam"; dimValue?: null; dimParam: string })
            );
        }
    }

    /**
     * Properties of a TypeProto.
     * @deprecated Use onnx.TypeProto.$Properties instead.
     */
    interface ITypeProto extends onnx.TypeProto.$Properties {
    }

    /** Represents a TypeProto. */
    class TypeProto {

        /**
         * Constructs a new TypeProto.
         * @param [properties] Properties to set
         */
        constructor(properties?: onnx.TypeProto.$Properties);

        /** Unknown fields preserved while decoding when enabled */
        $unknowns?: Uint8Array[];

        /** TypeProto tensorType. */
        tensorType?: (onnx.TypeProto.Tensor.$Properties|null);

        /** TypeProto sequenceType. */
        sequenceType?: (onnx.TypeProto.Sequence.$Properties|null);

        /** TypeProto mapType. */
        mapType?: (onnx.TypeProto.Map.$Properties|null);

        /** TypeProto optionalType. */
        optionalType?: (onnx.TypeProto.Optional.$Properties|null);

        /** TypeProto sparseTensorType. */
        sparseTensorType?: (onnx.TypeProto.SparseTensor.$Properties|null);

        /** TypeProto denotation. */
        denotation: string;

        /** TypeProto value. */
        value?: ("tensorType"|"sequenceType"|"mapType"|"optionalType"|"sparseTensorType");

        /**
         * Creates a new TypeProto instance using the specified properties.
         * @param [properties] Properties to set
         * @returns TypeProto instance
         */
        static create(properties: onnx.TypeProto.$Shape): onnx.TypeProto & onnx.TypeProto.$Shape;
        static create(properties?: onnx.TypeProto.$Properties): onnx.TypeProto;

        /**
         * Encodes the specified TypeProto message. Does not implicitly {@link onnx.TypeProto.verify|verify} messages.
         * @param message TypeProto message or plain object to encode
         * @param [writer] Writer to encode to
         * @returns Writer
         */
        static encode(message: onnx.TypeProto.$Properties, writer?: $protobuf.Writer): $protobuf.Writer;

        /**
         * Encodes the specified TypeProto message, length delimited. Does not implicitly {@link onnx.TypeProto.verify|verify} messages.
         * @param message TypeProto message or plain object to encode
         * @param [writer] Writer to encode to
         * @returns Writer
         */
        static encodeDelimited(message: onnx.TypeProto.$Properties, writer?: $protobuf.Writer): $protobuf.Writer;

        /**
         * Decodes a TypeProto message from the specified reader or buffer.
         * @param reader Reader or buffer to decode from
         * @param [length] Message length if known beforehand
         * @returns {onnx.TypeProto & onnx.TypeProto.$Shape} TypeProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): onnx.TypeProto & onnx.TypeProto.$Shape;

        /**
         * Decodes a TypeProto message from the specified reader or buffer, length delimited.
         * @param reader Reader or buffer to decode from
         * @returns {onnx.TypeProto & onnx.TypeProto.$Shape} TypeProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): onnx.TypeProto & onnx.TypeProto.$Shape;

        /**
         * Verifies a TypeProto message.
         * @param message Plain object to verify
         * @returns `null` if valid, otherwise the reason why it is not
         */
        static verify(message: { [k: string]: any }): (string|null);

        /**
         * Creates a TypeProto message from a plain object. Also converts values to their respective internal types.
         * @param object Plain object
         * @returns TypeProto
         */
        static fromObject(object: { [k: string]: any }): onnx.TypeProto;

        /**
         * Creates a plain object from a TypeProto message. Also converts values to other types if specified.
         * @param message TypeProto
         * @param [options] Conversion options
         * @returns Plain object
         */
        static toObject(message: onnx.TypeProto, options?: $protobuf.IConversionOptions): { [k: string]: any };

        /**
         * Converts this TypeProto to JSON.
         * @returns JSON object
         */
        toJSON(): { [k: string]: any };

        /**
         * Gets the type url for TypeProto
         * @param [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
         * @returns The type url
         */
        static getTypeUrl(prefix?: string): string;
    }

    namespace TypeProto {

        /** Properties of a TypeProto. */
        interface $Properties {

            /** TypeProto tensorType */
            tensorType?: (onnx.TypeProto.Tensor.$Properties|null);

            /** TypeProto sequenceType */
            sequenceType?: (onnx.TypeProto.Sequence.$Properties|null);

            /** TypeProto mapType */
            mapType?: (onnx.TypeProto.Map.$Properties|null);

            /** TypeProto optionalType */
            optionalType?: (onnx.TypeProto.Optional.$Properties|null);

            /** TypeProto sparseTensorType */
            sparseTensorType?: (onnx.TypeProto.SparseTensor.$Properties|null);

            /** TypeProto denotation */
            denotation?: (string|null);

            /** TypeProto value */
            value?: ("tensorType"|"sequenceType"|"mapType"|"optionalType"|"sparseTensorType");

            /** Unknown fields preserved while decoding when enabled */
            $unknowns?: Uint8Array[];
        }

        /** Narrowed shape of a TypeProto. */
        type $Shape = {
          tensorType?: onnx.TypeProto.Tensor.$Shape|null;
          sequenceType?: onnx.TypeProto.Sequence.$Shape|null;
          mapType?: onnx.TypeProto.Map.$Shape|null;
          optionalType?: onnx.TypeProto.Optional.$Shape|null;
          sparseTensorType?: onnx.TypeProto.SparseTensor.$Shape|null;
          denotation?: string|null;
          $unknowns?: Uint8Array[];
        } & (
          ({ value?: undefined; tensorType?: null; sequenceType?: null; mapType?: null; optionalType?: null; sparseTensorType?: null }|{ value?: "tensorType"; tensorType: onnx.TypeProto.Tensor.$Shape; sequenceType?: null; mapType?: null; optionalType?: null; sparseTensorType?: null }|{ value?: "sequenceType"; tensorType?: null; sequenceType: onnx.TypeProto.Sequence.$Shape; mapType?: null; optionalType?: null; sparseTensorType?: null }|{ value?: "mapType"; tensorType?: null; sequenceType?: null; mapType: onnx.TypeProto.Map.$Shape; optionalType?: null; sparseTensorType?: null }|{ value?: "optionalType"; tensorType?: null; sequenceType?: null; mapType?: null; optionalType: onnx.TypeProto.Optional.$Shape; sparseTensorType?: null }|{ value?: "sparseTensorType"; tensorType?: null; sequenceType?: null; mapType?: null; optionalType?: null; sparseTensorType: onnx.TypeProto.SparseTensor.$Shape })
        );

        /**
         * Properties of a Tensor.
         * @deprecated Use onnx.TypeProto.Tensor.$Properties instead.
         */
        interface ITensor extends onnx.TypeProto.Tensor.$Properties {
        }

        /** Represents a Tensor. */
        class Tensor {

            /**
             * Constructs a new Tensor.
             * @param [properties] Properties to set
             */
            constructor(properties?: onnx.TypeProto.Tensor.$Properties);

            /** Unknown fields preserved while decoding when enabled */
            $unknowns?: Uint8Array[];

            /** Tensor elemType. */
            elemType: number;

            /** Tensor shape. */
            shape?: (onnx.TensorShapeProto.$Properties|null);

            /**
             * Creates a new Tensor instance using the specified properties.
             * @param [properties] Properties to set
             * @returns Tensor instance
             */
            static create(properties: onnx.TypeProto.Tensor.$Shape): onnx.TypeProto.Tensor & onnx.TypeProto.Tensor.$Shape;
            static create(properties?: onnx.TypeProto.Tensor.$Properties): onnx.TypeProto.Tensor;

            /**
             * Encodes the specified Tensor message. Does not implicitly {@link onnx.TypeProto.Tensor.verify|verify} messages.
             * @param message Tensor message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            static encode(message: onnx.TypeProto.Tensor.$Properties, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified Tensor message, length delimited. Does not implicitly {@link onnx.TypeProto.Tensor.verify|verify} messages.
             * @param message Tensor message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            static encodeDelimited(message: onnx.TypeProto.Tensor.$Properties, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a Tensor message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns {onnx.TypeProto.Tensor & onnx.TypeProto.Tensor.$Shape} Tensor
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): onnx.TypeProto.Tensor & onnx.TypeProto.Tensor.$Shape;

            /**
             * Decodes a Tensor message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns {onnx.TypeProto.Tensor & onnx.TypeProto.Tensor.$Shape} Tensor
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): onnx.TypeProto.Tensor & onnx.TypeProto.Tensor.$Shape;

            /**
             * Verifies a Tensor message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates a Tensor message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns Tensor
             */
            static fromObject(object: { [k: string]: any }): onnx.TypeProto.Tensor;

            /**
             * Creates a plain object from a Tensor message. Also converts values to other types if specified.
             * @param message Tensor
             * @param [options] Conversion options
             * @returns Plain object
             */
            static toObject(message: onnx.TypeProto.Tensor, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this Tensor to JSON.
             * @returns JSON object
             */
            toJSON(): { [k: string]: any };

            /**
             * Gets the type url for Tensor
             * @param [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
             * @returns The type url
             */
            static getTypeUrl(prefix?: string): string;
        }

        namespace Tensor {

            /** Properties of a Tensor. */
            interface $Properties {

                /** Tensor elemType */
                elemType?: (number|null);

                /** Tensor shape */
                shape?: (onnx.TensorShapeProto.$Properties|null);

                /** Unknown fields preserved while decoding when enabled */
                $unknowns?: Uint8Array[];
            }

            /** Shape of a Tensor. */
            type $Shape = {
              elemType?: number|null;
              shape?: onnx.TensorShapeProto.$Shape|null;
              $unknowns?: Uint8Array[];
            };
        }

        /**
         * Properties of a Sequence.
         * @deprecated Use onnx.TypeProto.Sequence.$Properties instead.
         */
        interface ISequence extends onnx.TypeProto.Sequence.$Properties {
        }

        /** Represents a Sequence. */
        class Sequence {

            /**
             * Constructs a new Sequence.
             * @param [properties] Properties to set
             */
            constructor(properties?: onnx.TypeProto.Sequence.$Properties);

            /** Unknown fields preserved while decoding when enabled */
            $unknowns?: Uint8Array[];

            /** Sequence elemType. */
            elemType?: (onnx.TypeProto.$Properties|null);

            /**
             * Creates a new Sequence instance using the specified properties.
             * @param [properties] Properties to set
             * @returns Sequence instance
             */
            static create(properties: onnx.TypeProto.Sequence.$Shape): onnx.TypeProto.Sequence & onnx.TypeProto.Sequence.$Shape;
            static create(properties?: onnx.TypeProto.Sequence.$Properties): onnx.TypeProto.Sequence;

            /**
             * Encodes the specified Sequence message. Does not implicitly {@link onnx.TypeProto.Sequence.verify|verify} messages.
             * @param message Sequence message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            static encode(message: onnx.TypeProto.Sequence.$Properties, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified Sequence message, length delimited. Does not implicitly {@link onnx.TypeProto.Sequence.verify|verify} messages.
             * @param message Sequence message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            static encodeDelimited(message: onnx.TypeProto.Sequence.$Properties, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a Sequence message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns {onnx.TypeProto.Sequence & onnx.TypeProto.Sequence.$Shape} Sequence
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): onnx.TypeProto.Sequence & onnx.TypeProto.Sequence.$Shape;

            /**
             * Decodes a Sequence message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns {onnx.TypeProto.Sequence & onnx.TypeProto.Sequence.$Shape} Sequence
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): onnx.TypeProto.Sequence & onnx.TypeProto.Sequence.$Shape;

            /**
             * Verifies a Sequence message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates a Sequence message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns Sequence
             */
            static fromObject(object: { [k: string]: any }): onnx.TypeProto.Sequence;

            /**
             * Creates a plain object from a Sequence message. Also converts values to other types if specified.
             * @param message Sequence
             * @param [options] Conversion options
             * @returns Plain object
             */
            static toObject(message: onnx.TypeProto.Sequence, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this Sequence to JSON.
             * @returns JSON object
             */
            toJSON(): { [k: string]: any };

            /**
             * Gets the type url for Sequence
             * @param [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
             * @returns The type url
             */
            static getTypeUrl(prefix?: string): string;
        }

        namespace Sequence {

            /** Properties of a Sequence. */
            interface $Properties {

                /** Sequence elemType */
                elemType?: (onnx.TypeProto.$Properties|null);

                /** Unknown fields preserved while decoding when enabled */
                $unknowns?: Uint8Array[];
            }

            /** Shape of a Sequence. */
            type $Shape = {
              elemType?: onnx.TypeProto.$Shape|null;
              $unknowns?: Uint8Array[];
            };
        }

        /**
         * Properties of a Map.
         * @deprecated Use onnx.TypeProto.Map.$Properties instead.
         */
        interface IMap extends onnx.TypeProto.Map.$Properties {
        }

        /** Represents a Map. */
        class Map {

            /**
             * Constructs a new Map.
             * @param [properties] Properties to set
             */
            constructor(properties?: onnx.TypeProto.Map.$Properties);

            /** Unknown fields preserved while decoding when enabled */
            $unknowns?: Uint8Array[];

            /** Map keyType. */
            keyType: number;

            /** Map valueType. */
            valueType?: (onnx.TypeProto.$Properties|null);

            /**
             * Creates a new Map instance using the specified properties.
             * @param [properties] Properties to set
             * @returns Map instance
             */
            static create(properties: onnx.TypeProto.Map.$Shape): onnx.TypeProto.Map & onnx.TypeProto.Map.$Shape;
            static create(properties?: onnx.TypeProto.Map.$Properties): onnx.TypeProto.Map;

            /**
             * Encodes the specified Map message. Does not implicitly {@link onnx.TypeProto.Map.verify|verify} messages.
             * @param message Map message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            static encode(message: onnx.TypeProto.Map.$Properties, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified Map message, length delimited. Does not implicitly {@link onnx.TypeProto.Map.verify|verify} messages.
             * @param message Map message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            static encodeDelimited(message: onnx.TypeProto.Map.$Properties, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a Map message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns {onnx.TypeProto.Map & onnx.TypeProto.Map.$Shape} Map
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): onnx.TypeProto.Map & onnx.TypeProto.Map.$Shape;

            /**
             * Decodes a Map message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns {onnx.TypeProto.Map & onnx.TypeProto.Map.$Shape} Map
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): onnx.TypeProto.Map & onnx.TypeProto.Map.$Shape;

            /**
             * Verifies a Map message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates a Map message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns Map
             */
            static fromObject(object: { [k: string]: any }): onnx.TypeProto.Map;

            /**
             * Creates a plain object from a Map message. Also converts values to other types if specified.
             * @param message Map
             * @param [options] Conversion options
             * @returns Plain object
             */
            static toObject(message: onnx.TypeProto.Map, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this Map to JSON.
             * @returns JSON object
             */
            toJSON(): { [k: string]: any };

            /**
             * Gets the type url for Map
             * @param [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
             * @returns The type url
             */
            static getTypeUrl(prefix?: string): string;
        }

        namespace Map {

            /** Properties of a Map. */
            interface $Properties {

                /** Map keyType */
                keyType?: (number|null);

                /** Map valueType */
                valueType?: (onnx.TypeProto.$Properties|null);

                /** Unknown fields preserved while decoding when enabled */
                $unknowns?: Uint8Array[];
            }

            /** Shape of a Map. */
            type $Shape = {
              keyType?: number|null;
              valueType?: onnx.TypeProto.$Shape|null;
              $unknowns?: Uint8Array[];
            };
        }

        /**
         * Properties of an Optional.
         * @deprecated Use onnx.TypeProto.Optional.$Properties instead.
         */
        interface IOptional extends onnx.TypeProto.Optional.$Properties {
        }

        /** Represents an Optional. */
        class Optional {

            /**
             * Constructs a new Optional.
             * @param [properties] Properties to set
             */
            constructor(properties?: onnx.TypeProto.Optional.$Properties);

            /** Unknown fields preserved while decoding when enabled */
            $unknowns?: Uint8Array[];

            /** Optional elemType. */
            elemType?: (onnx.TypeProto.$Properties|null);

            /**
             * Creates a new Optional instance using the specified properties.
             * @param [properties] Properties to set
             * @returns Optional instance
             */
            static create(properties: onnx.TypeProto.Optional.$Shape): onnx.TypeProto.Optional & onnx.TypeProto.Optional.$Shape;
            static create(properties?: onnx.TypeProto.Optional.$Properties): onnx.TypeProto.Optional;

            /**
             * Encodes the specified Optional message. Does not implicitly {@link onnx.TypeProto.Optional.verify|verify} messages.
             * @param message Optional message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            static encode(message: onnx.TypeProto.Optional.$Properties, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified Optional message, length delimited. Does not implicitly {@link onnx.TypeProto.Optional.verify|verify} messages.
             * @param message Optional message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            static encodeDelimited(message: onnx.TypeProto.Optional.$Properties, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes an Optional message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns {onnx.TypeProto.Optional & onnx.TypeProto.Optional.$Shape} Optional
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): onnx.TypeProto.Optional & onnx.TypeProto.Optional.$Shape;

            /**
             * Decodes an Optional message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns {onnx.TypeProto.Optional & onnx.TypeProto.Optional.$Shape} Optional
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): onnx.TypeProto.Optional & onnx.TypeProto.Optional.$Shape;

            /**
             * Verifies an Optional message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates an Optional message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns Optional
             */
            static fromObject(object: { [k: string]: any }): onnx.TypeProto.Optional;

            /**
             * Creates a plain object from an Optional message. Also converts values to other types if specified.
             * @param message Optional
             * @param [options] Conversion options
             * @returns Plain object
             */
            static toObject(message: onnx.TypeProto.Optional, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this Optional to JSON.
             * @returns JSON object
             */
            toJSON(): { [k: string]: any };

            /**
             * Gets the type url for Optional
             * @param [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
             * @returns The type url
             */
            static getTypeUrl(prefix?: string): string;
        }

        namespace Optional {

            /** Properties of an Optional. */
            interface $Properties {

                /** Optional elemType */
                elemType?: (onnx.TypeProto.$Properties|null);

                /** Unknown fields preserved while decoding when enabled */
                $unknowns?: Uint8Array[];
            }

            /** Shape of an Optional. */
            type $Shape = {
              elemType?: onnx.TypeProto.$Shape|null;
              $unknowns?: Uint8Array[];
            };
        }

        /**
         * Properties of a SparseTensor.
         * @deprecated Use onnx.TypeProto.SparseTensor.$Properties instead.
         */
        interface ISparseTensor extends onnx.TypeProto.SparseTensor.$Properties {
        }

        /** Represents a SparseTensor. */
        class SparseTensor {

            /**
             * Constructs a new SparseTensor.
             * @param [properties] Properties to set
             */
            constructor(properties?: onnx.TypeProto.SparseTensor.$Properties);

            /** Unknown fields preserved while decoding when enabled */
            $unknowns?: Uint8Array[];

            /** SparseTensor elemType. */
            elemType: number;

            /** SparseTensor shape. */
            shape?: (onnx.TensorShapeProto.$Properties|null);

            /**
             * Creates a new SparseTensor instance using the specified properties.
             * @param [properties] Properties to set
             * @returns SparseTensor instance
             */
            static create(properties: onnx.TypeProto.SparseTensor.$Shape): onnx.TypeProto.SparseTensor & onnx.TypeProto.SparseTensor.$Shape;
            static create(properties?: onnx.TypeProto.SparseTensor.$Properties): onnx.TypeProto.SparseTensor;

            /**
             * Encodes the specified SparseTensor message. Does not implicitly {@link onnx.TypeProto.SparseTensor.verify|verify} messages.
             * @param message SparseTensor message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            static encode(message: onnx.TypeProto.SparseTensor.$Properties, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Encodes the specified SparseTensor message, length delimited. Does not implicitly {@link onnx.TypeProto.SparseTensor.verify|verify} messages.
             * @param message SparseTensor message or plain object to encode
             * @param [writer] Writer to encode to
             * @returns Writer
             */
            static encodeDelimited(message: onnx.TypeProto.SparseTensor.$Properties, writer?: $protobuf.Writer): $protobuf.Writer;

            /**
             * Decodes a SparseTensor message from the specified reader or buffer.
             * @param reader Reader or buffer to decode from
             * @param [length] Message length if known beforehand
             * @returns {onnx.TypeProto.SparseTensor & onnx.TypeProto.SparseTensor.$Shape} SparseTensor
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): onnx.TypeProto.SparseTensor & onnx.TypeProto.SparseTensor.$Shape;

            /**
             * Decodes a SparseTensor message from the specified reader or buffer, length delimited.
             * @param reader Reader or buffer to decode from
             * @returns {onnx.TypeProto.SparseTensor & onnx.TypeProto.SparseTensor.$Shape} SparseTensor
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): onnx.TypeProto.SparseTensor & onnx.TypeProto.SparseTensor.$Shape;

            /**
             * Verifies a SparseTensor message.
             * @param message Plain object to verify
             * @returns `null` if valid, otherwise the reason why it is not
             */
            static verify(message: { [k: string]: any }): (string|null);

            /**
             * Creates a SparseTensor message from a plain object. Also converts values to their respective internal types.
             * @param object Plain object
             * @returns SparseTensor
             */
            static fromObject(object: { [k: string]: any }): onnx.TypeProto.SparseTensor;

            /**
             * Creates a plain object from a SparseTensor message. Also converts values to other types if specified.
             * @param message SparseTensor
             * @param [options] Conversion options
             * @returns Plain object
             */
            static toObject(message: onnx.TypeProto.SparseTensor, options?: $protobuf.IConversionOptions): { [k: string]: any };

            /**
             * Converts this SparseTensor to JSON.
             * @returns JSON object
             */
            toJSON(): { [k: string]: any };

            /**
             * Gets the type url for SparseTensor
             * @param [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
             * @returns The type url
             */
            static getTypeUrl(prefix?: string): string;
        }

        namespace SparseTensor {

            /** Properties of a SparseTensor. */
            interface $Properties {

                /** SparseTensor elemType */
                elemType?: (number|null);

                /** SparseTensor shape */
                shape?: (onnx.TensorShapeProto.$Properties|null);

                /** Unknown fields preserved while decoding when enabled */
                $unknowns?: Uint8Array[];
            }

            /** Shape of a SparseTensor. */
            type $Shape = {
              elemType?: number|null;
              shape?: onnx.TensorShapeProto.$Shape|null;
              $unknowns?: Uint8Array[];
            };
        }
    }

    /**
     * Properties of an OperatorSetIdProto.
     * @deprecated Use onnx.OperatorSetIdProto.$Properties instead.
     */
    interface IOperatorSetIdProto extends onnx.OperatorSetIdProto.$Properties {
    }

    /** Represents an OperatorSetIdProto. */
    class OperatorSetIdProto {

        /**
         * Constructs a new OperatorSetIdProto.
         * @param [properties] Properties to set
         */
        constructor(properties?: onnx.OperatorSetIdProto.$Properties);

        /** Unknown fields preserved while decoding when enabled */
        $unknowns?: Uint8Array[];

        /** OperatorSetIdProto domain. */
        domain: string;

        /** OperatorSetIdProto version. */
        version: (number|Long);

        /**
         * Creates a new OperatorSetIdProto instance using the specified properties.
         * @param [properties] Properties to set
         * @returns OperatorSetIdProto instance
         */
        static create(properties: onnx.OperatorSetIdProto.$Shape): onnx.OperatorSetIdProto & onnx.OperatorSetIdProto.$Shape;
        static create(properties?: onnx.OperatorSetIdProto.$Properties): onnx.OperatorSetIdProto;

        /**
         * Encodes the specified OperatorSetIdProto message. Does not implicitly {@link onnx.OperatorSetIdProto.verify|verify} messages.
         * @param message OperatorSetIdProto message or plain object to encode
         * @param [writer] Writer to encode to
         * @returns Writer
         */
        static encode(message: onnx.OperatorSetIdProto.$Properties, writer?: $protobuf.Writer): $protobuf.Writer;

        /**
         * Encodes the specified OperatorSetIdProto message, length delimited. Does not implicitly {@link onnx.OperatorSetIdProto.verify|verify} messages.
         * @param message OperatorSetIdProto message or plain object to encode
         * @param [writer] Writer to encode to
         * @returns Writer
         */
        static encodeDelimited(message: onnx.OperatorSetIdProto.$Properties, writer?: $protobuf.Writer): $protobuf.Writer;

        /**
         * Decodes an OperatorSetIdProto message from the specified reader or buffer.
         * @param reader Reader or buffer to decode from
         * @param [length] Message length if known beforehand
         * @returns {onnx.OperatorSetIdProto & onnx.OperatorSetIdProto.$Shape} OperatorSetIdProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): onnx.OperatorSetIdProto & onnx.OperatorSetIdProto.$Shape;

        /**
         * Decodes an OperatorSetIdProto message from the specified reader or buffer, length delimited.
         * @param reader Reader or buffer to decode from
         * @returns {onnx.OperatorSetIdProto & onnx.OperatorSetIdProto.$Shape} OperatorSetIdProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): onnx.OperatorSetIdProto & onnx.OperatorSetIdProto.$Shape;

        /**
         * Verifies an OperatorSetIdProto message.
         * @param message Plain object to verify
         * @returns `null` if valid, otherwise the reason why it is not
         */
        static verify(message: { [k: string]: any }): (string|null);

        /**
         * Creates an OperatorSetIdProto message from a plain object. Also converts values to their respective internal types.
         * @param object Plain object
         * @returns OperatorSetIdProto
         */
        static fromObject(object: { [k: string]: any }): onnx.OperatorSetIdProto;

        /**
         * Creates a plain object from an OperatorSetIdProto message. Also converts values to other types if specified.
         * @param message OperatorSetIdProto
         * @param [options] Conversion options
         * @returns Plain object
         */
        static toObject(message: onnx.OperatorSetIdProto, options?: $protobuf.IConversionOptions): { [k: string]: any };

        /**
         * Converts this OperatorSetIdProto to JSON.
         * @returns JSON object
         */
        toJSON(): { [k: string]: any };

        /**
         * Gets the type url for OperatorSetIdProto
         * @param [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
         * @returns The type url
         */
        static getTypeUrl(prefix?: string): string;
    }

    namespace OperatorSetIdProto {

        /** Properties of an OperatorSetIdProto. */
        interface $Properties {

            /** OperatorSetIdProto domain */
            domain?: (string|null);

            /** OperatorSetIdProto version */
            version?: (number|Long|null);

            /** Unknown fields preserved while decoding when enabled */
            $unknowns?: Uint8Array[];
        }

        /** Shape of an OperatorSetIdProto. */
        type $Shape = onnx.OperatorSetIdProto.$Properties;
    }

    /** OperatorStatus enum. */
    enum OperatorStatus {

        /** EXPERIMENTAL value */
        EXPERIMENTAL = 0,

        /** STABLE value */
        STABLE = 1
    }

    /**
     * Properties of a FunctionProto.
     * @deprecated Use onnx.FunctionProto.$Properties instead.
     */
    interface IFunctionProto extends onnx.FunctionProto.$Properties {
    }

    /** Represents a FunctionProto. */
    class FunctionProto {

        /**
         * Constructs a new FunctionProto.
         * @param [properties] Properties to set
         */
        constructor(properties?: onnx.FunctionProto.$Properties);

        /** Unknown fields preserved while decoding when enabled */
        $unknowns?: Uint8Array[];

        /** FunctionProto name. */
        name: string;

        /** FunctionProto input. */
        input: string[];

        /** FunctionProto output. */
        output: string[];

        /** FunctionProto attribute. */
        attribute: string[];

        /** FunctionProto attributeProto. */
        attributeProto: onnx.AttributeProto.$Properties[];

        /** FunctionProto node. */
        node: onnx.NodeProto.$Properties[];

        /** FunctionProto docString. */
        docString: string;

        /** FunctionProto opsetImport. */
        opsetImport: onnx.OperatorSetIdProto.$Properties[];

        /** FunctionProto domain. */
        domain: string;

        /** FunctionProto overload. */
        overload: string;

        /** FunctionProto valueInfo. */
        valueInfo: onnx.ValueInfoProto.$Properties[];

        /** FunctionProto metadataProps. */
        metadataProps: onnx.StringStringEntryProto.$Properties[];

        /**
         * Creates a new FunctionProto instance using the specified properties.
         * @param [properties] Properties to set
         * @returns FunctionProto instance
         */
        static create(properties: onnx.FunctionProto.$Shape): onnx.FunctionProto & onnx.FunctionProto.$Shape;
        static create(properties?: onnx.FunctionProto.$Properties): onnx.FunctionProto;

        /**
         * Encodes the specified FunctionProto message. Does not implicitly {@link onnx.FunctionProto.verify|verify} messages.
         * @param message FunctionProto message or plain object to encode
         * @param [writer] Writer to encode to
         * @returns Writer
         */
        static encode(message: onnx.FunctionProto.$Properties, writer?: $protobuf.Writer): $protobuf.Writer;

        /**
         * Encodes the specified FunctionProto message, length delimited. Does not implicitly {@link onnx.FunctionProto.verify|verify} messages.
         * @param message FunctionProto message or plain object to encode
         * @param [writer] Writer to encode to
         * @returns Writer
         */
        static encodeDelimited(message: onnx.FunctionProto.$Properties, writer?: $protobuf.Writer): $protobuf.Writer;

        /**
         * Decodes a FunctionProto message from the specified reader or buffer.
         * @param reader Reader or buffer to decode from
         * @param [length] Message length if known beforehand
         * @returns {onnx.FunctionProto & onnx.FunctionProto.$Shape} FunctionProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        static decode(reader: ($protobuf.Reader|Uint8Array), length?: number): onnx.FunctionProto & onnx.FunctionProto.$Shape;

        /**
         * Decodes a FunctionProto message from the specified reader or buffer, length delimited.
         * @param reader Reader or buffer to decode from
         * @returns {onnx.FunctionProto & onnx.FunctionProto.$Shape} FunctionProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        static decodeDelimited(reader: ($protobuf.Reader|Uint8Array)): onnx.FunctionProto & onnx.FunctionProto.$Shape;

        /**
         * Verifies a FunctionProto message.
         * @param message Plain object to verify
         * @returns `null` if valid, otherwise the reason why it is not
         */
        static verify(message: { [k: string]: any }): (string|null);

        /**
         * Creates a FunctionProto message from a plain object. Also converts values to their respective internal types.
         * @param object Plain object
         * @returns FunctionProto
         */
        static fromObject(object: { [k: string]: any }): onnx.FunctionProto;

        /**
         * Creates a plain object from a FunctionProto message. Also converts values to other types if specified.
         * @param message FunctionProto
         * @param [options] Conversion options
         * @returns Plain object
         */
        static toObject(message: onnx.FunctionProto, options?: $protobuf.IConversionOptions): { [k: string]: any };

        /**
         * Converts this FunctionProto to JSON.
         * @returns JSON object
         */
        toJSON(): { [k: string]: any };

        /**
         * Gets the type url for FunctionProto
         * @param [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
         * @returns The type url
         */
        static getTypeUrl(prefix?: string): string;
    }

    namespace FunctionProto {

        /** Properties of a FunctionProto. */
        interface $Properties {

            /** FunctionProto name */
            name?: (string|null);

            /** FunctionProto input */
            input?: (string[]|null);

            /** FunctionProto output */
            output?: (string[]|null);

            /** FunctionProto attribute */
            attribute?: (string[]|null);

            /** FunctionProto attributeProto */
            attributeProto?: (onnx.AttributeProto.$Properties[]|null);

            /** FunctionProto node */
            node?: (onnx.NodeProto.$Properties[]|null);

            /** FunctionProto docString */
            docString?: (string|null);

            /** FunctionProto opsetImport */
            opsetImport?: (onnx.OperatorSetIdProto.$Properties[]|null);

            /** FunctionProto domain */
            domain?: (string|null);

            /** FunctionProto overload */
            overload?: (string|null);

            /** FunctionProto valueInfo */
            valueInfo?: (onnx.ValueInfoProto.$Properties[]|null);

            /** FunctionProto metadataProps */
            metadataProps?: (onnx.StringStringEntryProto.$Properties[]|null);

            /** Unknown fields preserved while decoding when enabled */
            $unknowns?: Uint8Array[];
        }

        /** Shape of a FunctionProto. */
        type $Shape = {
          name?: string|null;
          input?: string[]|null;
          output?: string[]|null;
          attribute?: string[]|null;
          attributeProto?: onnx.AttributeProto.$Shape[]|null;
          node?: onnx.NodeProto.$Shape[]|null;
          docString?: string|null;
          opsetImport?: onnx.OperatorSetIdProto.$Shape[]|null;
          domain?: string|null;
          overload?: string|null;
          valueInfo?: onnx.ValueInfoProto.$Shape[]|null;
          metadataProps?: onnx.StringStringEntryProto.$Shape[]|null;
          $unknowns?: Uint8Array[];
        };
    }
}
