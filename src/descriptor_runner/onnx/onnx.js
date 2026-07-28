/*eslint-disable block-scoped-var, id-length, no-control-regex, no-magic-numbers, no-mixed-operators, no-prototype-builtins, no-redeclare, no-shadow, no-var, sort-vars, default-case, jsdoc/require-param*/
import $protobuf from "protobufjs/minimal.js";

// Common aliases
const $Reader = $protobuf.Reader, $Writer = $protobuf.Writer, $util = $protobuf.util;
const $Object = $util.global.Object, $undefined = $util.global.undefined, $Error = $util.global.Error, $Array = $util.global.Array, $TypeError = $util.global.TypeError, $String = $util.global.String, $Number = $util.global.Number, $parseInt = $util.global.parseInt, $BigInt = $util.global.BigInt, $isFinite = $util.global.isFinite;

// Exported root namespace
const $root = $protobuf.roots["default"] || ($protobuf.roots["default"] = {});

export const onnx = $root.onnx = (() => {

    /**
     * Namespace onnx.
     * @exports onnx
     * @namespace
     */
    const onnx = {};

    /**
     * Version enum.
     * @name onnx.Version
     * @enum {number}
     * @property {number} _START_VERSION=0 _START_VERSION value
     * @property {number} IR_VERSION_2017_10_10=1 IR_VERSION_2017_10_10 value
     * @property {number} IR_VERSION_2017_10_30=2 IR_VERSION_2017_10_30 value
     * @property {number} IR_VERSION_2017_11_3=3 IR_VERSION_2017_11_3 value
     * @property {number} IR_VERSION_2019_1_22=4 IR_VERSION_2019_1_22 value
     * @property {number} IR_VERSION_2019_3_18=5 IR_VERSION_2019_3_18 value
     * @property {number} IR_VERSION_2019_9_19=6 IR_VERSION_2019_9_19 value
     * @property {number} IR_VERSION_2020_5_8=7 IR_VERSION_2020_5_8 value
     * @property {number} IR_VERSION_2021_7_30=8 IR_VERSION_2021_7_30 value
     * @property {number} IR_VERSION_2023_5_5=9 IR_VERSION_2023_5_5 value
     * @property {number} IR_VERSION=10 IR_VERSION value
     */
    onnx.Version = (function() {
        const valuesById = $Object.create(null), values = $Object.create(valuesById);
        values[valuesById[0] = "_START_VERSION"] = 0;
        values[valuesById[1] = "IR_VERSION_2017_10_10"] = 1;
        values[valuesById[2] = "IR_VERSION_2017_10_30"] = 2;
        values[valuesById[3] = "IR_VERSION_2017_11_3"] = 3;
        values[valuesById[4] = "IR_VERSION_2019_1_22"] = 4;
        values[valuesById[5] = "IR_VERSION_2019_3_18"] = 5;
        values[valuesById[6] = "IR_VERSION_2019_9_19"] = 6;
        values[valuesById[7] = "IR_VERSION_2020_5_8"] = 7;
        values[valuesById[8] = "IR_VERSION_2021_7_30"] = 8;
        values[valuesById[9] = "IR_VERSION_2023_5_5"] = 9;
        values[valuesById[10] = "IR_VERSION"] = 10;
        return values;
    })();

    onnx.AttributeProto = (function() {

        /**
         * Properties of an AttributeProto.
         * @typedef {Object} onnx.AttributeProto.$Properties
         * @property {string|null} [name] AttributeProto name
         * @property {string|null} [refAttrName] AttributeProto refAttrName
         * @property {string|null} [docString] AttributeProto docString
         * @property {onnx.AttributeProto.AttributeType|null} [type] AttributeProto type
         * @property {number|null} [f] AttributeProto f
         * @property {number|Long|null} [i] AttributeProto i
         * @property {Uint8Array|null} [s] AttributeProto s
         * @property {onnx.TensorProto.$Properties|null} [t] AttributeProto t
         * @property {onnx.GraphProto.$Properties|null} [g] AttributeProto g
         * @property {onnx.SparseTensorProto.$Properties|null} [sparseTensor] AttributeProto sparseTensor
         * @property {onnx.TypeProto.$Properties|null} [tp] AttributeProto tp
         * @property {Array.<number>|null} [floats] AttributeProto floats
         * @property {Array.<number|Long>|null} [ints] AttributeProto ints
         * @property {Array.<Uint8Array>|null} [strings] AttributeProto strings
         * @property {Array.<onnx.TensorProto.$Properties>|null} [tensors] AttributeProto tensors
         * @property {Array.<onnx.GraphProto.$Properties>|null} [graphs] AttributeProto graphs
         * @property {Array.<onnx.SparseTensorProto.$Properties>|null} [sparseTensors] AttributeProto sparseTensors
         * @property {Array.<onnx.TypeProto.$Properties>|null} [typeProtos] AttributeProto typeProtos
         * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding when enabled
         */

        /**
         * Properties of an AttributeProto.
         * @memberof onnx
         * @interface IAttributeProto
         * @augments onnx.AttributeProto.$Properties
         * @deprecated Use onnx.AttributeProto.$Properties instead.
         */

        /**
         * Shape of an AttributeProto.
         * @typedef {{
         *   name?: string|null;
         *   refAttrName?: string|null;
         *   docString?: string|null;
         *   type?: onnx.AttributeProto.AttributeType|null;
         *   f?: number|null;
         *   i?: number|Long|null;
         *   s?: Uint8Array|null;
         *   t?: onnx.TensorProto.$Shape|null;
         *   g?: onnx.GraphProto.$Shape|null;
         *   sparseTensor?: onnx.SparseTensorProto.$Shape|null;
         *   tp?: onnx.TypeProto.$Shape|null;
         *   floats?: Array.<number>|null;
         *   ints?: Array.<number|Long>|null;
         *   strings?: Array.<Uint8Array>|null;
         *   tensors?: Array.<onnx.TensorProto.$Shape>|null;
         *   graphs?: Array.<onnx.GraphProto.$Shape>|null;
         *   sparseTensors?: Array.<onnx.SparseTensorProto.$Shape>|null;
         *   typeProtos?: Array.<onnx.TypeProto.$Shape>|null;
         *   $unknowns?: Array.<Uint8Array>;
         * }} onnx.AttributeProto.$Shape
         */

        /**
         * Constructs a new AttributeProto.
         * @memberof onnx
         * @classdesc Represents an AttributeProto.
         * @constructor
         * @param {onnx.AttributeProto.$Properties=} [properties] Properties to set
         * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding when enabled
         */
        const AttributeProto = function (properties) {
            this.floats = [];
            this.ints = [];
            this.strings = [];
            this.tensors = [];
            this.graphs = [];
            this.sparseTensors = [];
            this.typeProtos = [];
            if (properties)
                for (let keys = $Object.keys(properties), i = 0; i < keys.length; ++i)
                    if (properties[keys[i]] != null && keys[i] !== "__proto__")
                        this[keys[i]] = properties[keys[i]];
        };

        /**
         * AttributeProto name.
         * @member {string} name
         * @memberof onnx.AttributeProto
         * @instance
         */
        AttributeProto.prototype.name = "";

        /**
         * AttributeProto refAttrName.
         * @member {string} refAttrName
         * @memberof onnx.AttributeProto
         * @instance
         */
        AttributeProto.prototype.refAttrName = "";

        /**
         * AttributeProto docString.
         * @member {string} docString
         * @memberof onnx.AttributeProto
         * @instance
         */
        AttributeProto.prototype.docString = "";

        /**
         * AttributeProto type.
         * @member {onnx.AttributeProto.AttributeType} type
         * @memberof onnx.AttributeProto
         * @instance
         */
        AttributeProto.prototype.type = 0;

        /**
         * AttributeProto f.
         * @member {number} f
         * @memberof onnx.AttributeProto
         * @instance
         */
        AttributeProto.prototype.f = 0;

        /**
         * AttributeProto i.
         * @member {number|Long} i
         * @memberof onnx.AttributeProto
         * @instance
         */
        AttributeProto.prototype.i = $util.Long ? $util.Long.fromBits(0,0,false) : 0;

        /**
         * AttributeProto s.
         * @member {Uint8Array} s
         * @memberof onnx.AttributeProto
         * @instance
         */
        AttributeProto.prototype.s = $util.newBuffer([]);

        /**
         * AttributeProto t.
         * @member {onnx.TensorProto.$Properties|null|undefined} t
         * @memberof onnx.AttributeProto
         * @instance
         */
        AttributeProto.prototype.t = null;

        /**
         * AttributeProto g.
         * @member {onnx.GraphProto.$Properties|null|undefined} g
         * @memberof onnx.AttributeProto
         * @instance
         */
        AttributeProto.prototype.g = null;

        /**
         * AttributeProto sparseTensor.
         * @member {onnx.SparseTensorProto.$Properties|null|undefined} sparseTensor
         * @memberof onnx.AttributeProto
         * @instance
         */
        AttributeProto.prototype.sparseTensor = null;

        /**
         * AttributeProto tp.
         * @member {onnx.TypeProto.$Properties|null|undefined} tp
         * @memberof onnx.AttributeProto
         * @instance
         */
        AttributeProto.prototype.tp = null;

        /**
         * AttributeProto floats.
         * @member {Array.<number>} floats
         * @memberof onnx.AttributeProto
         * @instance
         */
        AttributeProto.prototype.floats = $util.emptyArray;

        /**
         * AttributeProto ints.
         * @member {Array.<number|Long>} ints
         * @memberof onnx.AttributeProto
         * @instance
         */
        AttributeProto.prototype.ints = $util.emptyArray;

        /**
         * AttributeProto strings.
         * @member {Array.<Uint8Array>} strings
         * @memberof onnx.AttributeProto
         * @instance
         */
        AttributeProto.prototype.strings = $util.emptyArray;

        /**
         * AttributeProto tensors.
         * @member {Array.<onnx.TensorProto.$Properties>} tensors
         * @memberof onnx.AttributeProto
         * @instance
         */
        AttributeProto.prototype.tensors = $util.emptyArray;

        /**
         * AttributeProto graphs.
         * @member {Array.<onnx.GraphProto.$Properties>} graphs
         * @memberof onnx.AttributeProto
         * @instance
         */
        AttributeProto.prototype.graphs = $util.emptyArray;

        /**
         * AttributeProto sparseTensors.
         * @member {Array.<onnx.SparseTensorProto.$Properties>} sparseTensors
         * @memberof onnx.AttributeProto
         * @instance
         */
        AttributeProto.prototype.sparseTensors = $util.emptyArray;

        /**
         * AttributeProto typeProtos.
         * @member {Array.<onnx.TypeProto.$Properties>} typeProtos
         * @memberof onnx.AttributeProto
         * @instance
         */
        AttributeProto.prototype.typeProtos = $util.emptyArray;

        /**
         * Creates a new AttributeProto instance using the specified properties.
         * @function create
         * @memberof onnx.AttributeProto
         * @static
         * @param {onnx.AttributeProto.$Properties=} [properties] Properties to set
         * @returns {onnx.AttributeProto} AttributeProto instance
         * @type {{
         *   (properties: onnx.AttributeProto.$Shape): onnx.AttributeProto & onnx.AttributeProto.$Shape;
         *   (properties?: onnx.AttributeProto.$Properties): onnx.AttributeProto;
         * }}
         */
        AttributeProto.create = function(properties) {
            return new AttributeProto(properties);
        };

        /**
         * Encodes the specified AttributeProto message. Does not implicitly {@link onnx.AttributeProto.verify|verify} messages.
         * @function encode
         * @memberof onnx.AttributeProto
         * @static
         * @param {onnx.AttributeProto.$Properties} message AttributeProto message or plain object to encode
         * @param {$protobuf.Writer} [writer] Writer to encode to
         * @returns {$protobuf.Writer} Writer
         */
        AttributeProto.encode = function (message, writer, _depth) {
            if (!writer)
                writer = $Writer.create();
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                throw $Error("max depth exceeded");
            if (message.name != null && $Object.hasOwnProperty.call(message, "name"))
                writer.uint32(/* id 1, wireType 2 =*/10).string(message.name);
            if (message.f != null && $Object.hasOwnProperty.call(message, "f"))
                writer.uint32(/* id 2, wireType 5 =*/21).float(message.f);
            if (message.i != null && $Object.hasOwnProperty.call(message, "i"))
                writer.uint32(/* id 3, wireType 0 =*/24).int64(message.i);
            if (message.s != null && $Object.hasOwnProperty.call(message, "s"))
                writer.uint32(/* id 4, wireType 2 =*/34).bytes(message.s);
            if (message.t != null && $Object.hasOwnProperty.call(message, "t"))
                $root.onnx.TensorProto.encode(message.t, writer.uint32(/* id 5, wireType 2 =*/42).fork(), _depth + 1).ldelim();
            if (message.g != null && $Object.hasOwnProperty.call(message, "g"))
                $root.onnx.GraphProto.encode(message.g, writer.uint32(/* id 6, wireType 2 =*/50).fork(), _depth + 1).ldelim();
            if (message.floats != null && message.floats.length)
                for (let i = 0; i < message.floats.length; ++i)
                    writer.uint32(/* id 7, wireType 5 =*/61).float(message.floats[i]);
            if (message.ints != null && message.ints.length)
                for (let i = 0; i < message.ints.length; ++i)
                    writer.uint32(/* id 8, wireType 0 =*/64).int64(message.ints[i]);
            if (message.strings != null && message.strings.length)
                for (let i = 0; i < message.strings.length; ++i)
                    writer.uint32(/* id 9, wireType 2 =*/74).bytes(message.strings[i]);
            if (message.tensors != null && message.tensors.length)
                for (let i = 0; i < message.tensors.length; ++i)
                    $root.onnx.TensorProto.encode(message.tensors[i], writer.uint32(/* id 10, wireType 2 =*/82).fork(), _depth + 1).ldelim();
            if (message.graphs != null && message.graphs.length)
                for (let i = 0; i < message.graphs.length; ++i)
                    $root.onnx.GraphProto.encode(message.graphs[i], writer.uint32(/* id 11, wireType 2 =*/90).fork(), _depth + 1).ldelim();
            if (message.docString != null && $Object.hasOwnProperty.call(message, "docString"))
                writer.uint32(/* id 13, wireType 2 =*/106).string(message.docString);
            if (message.tp != null && $Object.hasOwnProperty.call(message, "tp"))
                $root.onnx.TypeProto.encode(message.tp, writer.uint32(/* id 14, wireType 2 =*/114).fork(), _depth + 1).ldelim();
            if (message.typeProtos != null && message.typeProtos.length)
                for (let i = 0; i < message.typeProtos.length; ++i)
                    $root.onnx.TypeProto.encode(message.typeProtos[i], writer.uint32(/* id 15, wireType 2 =*/122).fork(), _depth + 1).ldelim();
            if (message.type != null && $Object.hasOwnProperty.call(message, "type"))
                writer.uint32(/* id 20, wireType 0 =*/160).int32(message.type);
            if (message.refAttrName != null && $Object.hasOwnProperty.call(message, "refAttrName"))
                writer.uint32(/* id 21, wireType 2 =*/170).string(message.refAttrName);
            if (message.sparseTensor != null && $Object.hasOwnProperty.call(message, "sparseTensor"))
                $root.onnx.SparseTensorProto.encode(message.sparseTensor, writer.uint32(/* id 22, wireType 2 =*/178).fork(), _depth + 1).ldelim();
            if (message.sparseTensors != null && message.sparseTensors.length)
                for (let i = 0; i < message.sparseTensors.length; ++i)
                    $root.onnx.SparseTensorProto.encode(message.sparseTensors[i], writer.uint32(/* id 23, wireType 2 =*/186).fork(), _depth + 1).ldelim();
            if (message.$unknowns != null && $Object.hasOwnProperty.call(message, "$unknowns"))
                for (let i = 0; i < message.$unknowns.length; ++i)
                    writer.raw(message.$unknowns[i]);
            return writer;
        };

        /**
         * Encodes the specified AttributeProto message, length delimited. Does not implicitly {@link onnx.AttributeProto.verify|verify} messages.
         * @function encodeDelimited
         * @memberof onnx.AttributeProto
         * @static
         * @param {onnx.AttributeProto.$Properties} message AttributeProto message or plain object to encode
         * @param {$protobuf.Writer} [writer] Writer to encode to
         * @returns {$protobuf.Writer} Writer
         */
        AttributeProto.encodeDelimited = function(message, writer) {
            return this.encode(message, (writer || $Writer.create()).fork()).ldelim();
        };

        /**
         * Decodes an AttributeProto message from the specified reader or buffer.
         * @function decode
         * @memberof onnx.AttributeProto
         * @static
         * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
         * @param {number} [length] Message length if known beforehand
         * @returns {onnx.AttributeProto & onnx.AttributeProto.$Shape} AttributeProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        AttributeProto.decode = function (reader, length, _end, _depth, _target) {
            if (!(reader instanceof $Reader))
                reader = $Reader.create(reader);
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $Reader.recursionLimit)
                throw $Error("max depth exceeded");
            let end = length === $undefined ? reader.len : reader.pos + length, message = _target || new $root.onnx.AttributeProto(), value;
            while (reader.pos < end) {
                let start = reader.pos;
                let tag = reader.tag();
                if (tag === _end) {
                    _end = $undefined;
                    break;
                }
                let wireType = tag & 7;
                switch (tag >>>= 3) {
                case 1: {
                        if (wireType !== 2)
                            break;
                        message.name = reader.string();
                        continue;
                    }
                case 21: {
                        if (wireType !== 2)
                            break;
                        message.refAttrName = reader.string();
                        continue;
                    }
                case 13: {
                        if (wireType !== 2)
                            break;
                        message.docString = reader.string();
                        continue;
                    }
                case 20: {
                        if (wireType !== 0)
                            break;
                        value = reader.int32();
                        if ($root.onnx.AttributeProto.AttributeType[value] !== $undefined)
                            message.type = value;
                        else if (!reader.discardUnknown) {
                            $util.makeProp(message, "$unknowns", false);
                            (message.$unknowns || (message.$unknowns = [])).push(reader.raw(start, reader.pos));
                        }
                        continue;
                    }
                case 2: {
                        if (wireType !== 5)
                            break;
                        message.f = reader.float();
                        continue;
                    }
                case 3: {
                        if (wireType !== 0)
                            break;
                        message.i = reader.int64();
                        continue;
                    }
                case 4: {
                        if (wireType !== 2)
                            break;
                        message.s = reader.bytes();
                        continue;
                    }
                case 5: {
                        if (wireType !== 2)
                            break;
                        message.t = $root.onnx.TensorProto.decode(reader, reader.uint32(), $undefined, _depth + 1, message.t);
                        continue;
                    }
                case 6: {
                        if (wireType !== 2)
                            break;
                        message.g = $root.onnx.GraphProto.decode(reader, reader.uint32(), $undefined, _depth + 1, message.g);
                        continue;
                    }
                case 22: {
                        if (wireType !== 2)
                            break;
                        message.sparseTensor = $root.onnx.SparseTensorProto.decode(reader, reader.uint32(), $undefined, _depth + 1, message.sparseTensor);
                        continue;
                    }
                case 14: {
                        if (wireType !== 2)
                            break;
                        message.tp = $root.onnx.TypeProto.decode(reader, reader.uint32(), $undefined, _depth + 1, message.tp);
                        continue;
                    }
                case 7: {
                        if (wireType === 2) {
                            if (!(message.floats && message.floats.length))
                                message.floats = [];
                            reader.floats(message.floats);
                            continue;
                        }
                        if (wireType !== 5)
                            break;
                        if (!(message.floats && message.floats.length))
                            message.floats = [];
                        message.floats.push(reader.float());
                        continue;
                    }
                case 8: {
                        if (wireType === 2) {
                            if (!(message.ints && message.ints.length))
                                message.ints = [];
                            reader.int64s(message.ints);
                            continue;
                        }
                        if (wireType !== 0)
                            break;
                        if (!(message.ints && message.ints.length))
                            message.ints = [];
                        message.ints.push(reader.int64());
                        continue;
                    }
                case 9: {
                        if (wireType !== 2)
                            break;
                        if (!(message.strings && message.strings.length))
                            message.strings = [];
                        message.strings.push(reader.bytes());
                        continue;
                    }
                case 10: {
                        if (wireType !== 2)
                            break;
                        if (!(message.tensors && message.tensors.length))
                            message.tensors = [];
                        message.tensors.push($root.onnx.TensorProto.decode(reader, reader.uint32(), $undefined, _depth + 1));
                        continue;
                    }
                case 11: {
                        if (wireType !== 2)
                            break;
                        if (!(message.graphs && message.graphs.length))
                            message.graphs = [];
                        message.graphs.push($root.onnx.GraphProto.decode(reader, reader.uint32(), $undefined, _depth + 1));
                        continue;
                    }
                case 23: {
                        if (wireType !== 2)
                            break;
                        if (!(message.sparseTensors && message.sparseTensors.length))
                            message.sparseTensors = [];
                        message.sparseTensors.push($root.onnx.SparseTensorProto.decode(reader, reader.uint32(), $undefined, _depth + 1));
                        continue;
                    }
                case 15: {
                        if (wireType !== 2)
                            break;
                        if (!(message.typeProtos && message.typeProtos.length))
                            message.typeProtos = [];
                        message.typeProtos.push($root.onnx.TypeProto.decode(reader, reader.uint32(), $undefined, _depth + 1));
                        continue;
                    }
                }
                reader.skipType(wireType, _depth, tag);
                if (!reader.discardUnknown) {
                    $util.makeProp(message, "$unknowns", false);
                    (message.$unknowns || (message.$unknowns = [])).push(reader.raw(start, reader.pos));
                }
            }
            if (_end !== $undefined)
                throw $Error("missing end group");
            return message;
        };

        /**
         * Decodes an AttributeProto message from the specified reader or buffer, length delimited.
         * @function decodeDelimited
         * @memberof onnx.AttributeProto
         * @static
         * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
         * @returns {onnx.AttributeProto & onnx.AttributeProto.$Shape} AttributeProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        AttributeProto.decodeDelimited = function(reader) {
            if (!(reader instanceof $Reader))
                reader = new $Reader(reader);
            return this.decode(reader, reader.uint32());
        };

        /**
         * Verifies an AttributeProto message.
         * @function verify
         * @memberof onnx.AttributeProto
         * @static
         * @param {Object.<string,*>} message Plain object to verify
         * @returns {string|null} `null` if valid, otherwise the reason why it is not
         */
        AttributeProto.verify = function (message, _depth) {
            if (typeof message !== "object" || message === null)
                return "object expected";
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                return "max depth exceeded";
            if (message.name != null && $Object.hasOwnProperty.call(message, "name"))
                if (!$util.isString(message.name))
                    return "name: string expected";
            if (message.refAttrName != null && $Object.hasOwnProperty.call(message, "refAttrName"))
                if (!$util.isString(message.refAttrName))
                    return "refAttrName: string expected";
            if (message.docString != null && $Object.hasOwnProperty.call(message, "docString"))
                if (!$util.isString(message.docString))
                    return "docString: string expected";
            if (message.type != null && $Object.hasOwnProperty.call(message, "type"))
                switch (message.type) {
                default:
                    return "type: enum value expected";
                case 0:
                case 1:
                case 2:
                case 3:
                case 4:
                case 5:
                case 11:
                case 13:
                case 6:
                case 7:
                case 8:
                case 9:
                case 10:
                case 12:
                case 14:
                    break;
                }
            if (message.f != null && $Object.hasOwnProperty.call(message, "f"))
                if (typeof message.f !== "number")
                    return "f: number expected";
            if (message.i != null && $Object.hasOwnProperty.call(message, "i"))
                if (!$util.isInteger(message.i) && !(message.i && $util.isInteger(message.i.low) && $util.isInteger(message.i.high)))
                    return "i: integer|Long expected";
            if (message.s != null && $Object.hasOwnProperty.call(message, "s"))
                if (!(message.s && typeof message.s.length === "number" || $util.isString(message.s)))
                    return "s: buffer expected";
            if (message.t != null && $Object.hasOwnProperty.call(message, "t")) {
                let error = $root.onnx.TensorProto.verify(message.t, _depth + 1);
                if (error)
                    return "t." + error;
            }
            if (message.g != null && $Object.hasOwnProperty.call(message, "g")) {
                let error = $root.onnx.GraphProto.verify(message.g, _depth + 1);
                if (error)
                    return "g." + error;
            }
            if (message.sparseTensor != null && $Object.hasOwnProperty.call(message, "sparseTensor")) {
                let error = $root.onnx.SparseTensorProto.verify(message.sparseTensor, _depth + 1);
                if (error)
                    return "sparseTensor." + error;
            }
            if (message.tp != null && $Object.hasOwnProperty.call(message, "tp")) {
                let error = $root.onnx.TypeProto.verify(message.tp, _depth + 1);
                if (error)
                    return "tp." + error;
            }
            if (message.floats != null && $Object.hasOwnProperty.call(message, "floats")) {
                if (!$Array.isArray(message.floats))
                    return "floats: array expected";
                for (let i = 0; i < message.floats.length; ++i)
                    if (typeof message.floats[i] !== "number")
                        return "floats: number[] expected";
            }
            if (message.ints != null && $Object.hasOwnProperty.call(message, "ints")) {
                if (!$Array.isArray(message.ints))
                    return "ints: array expected";
                for (let i = 0; i < message.ints.length; ++i)
                    if (!$util.isInteger(message.ints[i]) && !(message.ints[i] && $util.isInteger(message.ints[i].low) && $util.isInteger(message.ints[i].high)))
                        return "ints: integer|Long[] expected";
            }
            if (message.strings != null && $Object.hasOwnProperty.call(message, "strings")) {
                if (!$Array.isArray(message.strings))
                    return "strings: array expected";
                for (let i = 0; i < message.strings.length; ++i)
                    if (!(message.strings[i] && typeof message.strings[i].length === "number" || $util.isString(message.strings[i])))
                        return "strings: buffer[] expected";
            }
            if (message.tensors != null && $Object.hasOwnProperty.call(message, "tensors")) {
                if (!$Array.isArray(message.tensors))
                    return "tensors: array expected";
                for (let i = 0; i < message.tensors.length; ++i) {
                    let error = $root.onnx.TensorProto.verify(message.tensors[i], _depth + 1);
                    if (error)
                        return "tensors." + error;
                }
            }
            if (message.graphs != null && $Object.hasOwnProperty.call(message, "graphs")) {
                if (!$Array.isArray(message.graphs))
                    return "graphs: array expected";
                for (let i = 0; i < message.graphs.length; ++i) {
                    let error = $root.onnx.GraphProto.verify(message.graphs[i], _depth + 1);
                    if (error)
                        return "graphs." + error;
                }
            }
            if (message.sparseTensors != null && $Object.hasOwnProperty.call(message, "sparseTensors")) {
                if (!$Array.isArray(message.sparseTensors))
                    return "sparseTensors: array expected";
                for (let i = 0; i < message.sparseTensors.length; ++i) {
                    let error = $root.onnx.SparseTensorProto.verify(message.sparseTensors[i], _depth + 1);
                    if (error)
                        return "sparseTensors." + error;
                }
            }
            if (message.typeProtos != null && $Object.hasOwnProperty.call(message, "typeProtos")) {
                if (!$Array.isArray(message.typeProtos))
                    return "typeProtos: array expected";
                for (let i = 0; i < message.typeProtos.length; ++i) {
                    let error = $root.onnx.TypeProto.verify(message.typeProtos[i], _depth + 1);
                    if (error)
                        return "typeProtos." + error;
                }
            }
            return null;
        };

        /**
         * Creates an AttributeProto message from a plain object. Also converts values to their respective internal types.
         * @function fromObject
         * @memberof onnx.AttributeProto
         * @static
         * @param {Object.<string,*>} object Plain object
         * @returns {onnx.AttributeProto} AttributeProto
         */
        AttributeProto.fromObject = function (object, _depth) {
            if (object instanceof $root.onnx.AttributeProto)
                return object;
            if (!$util.isObject(object))
                throw $TypeError(".onnx.AttributeProto: object expected");
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                throw $Error("max depth exceeded");
            let message = new $root.onnx.AttributeProto();
            if (object.name != null)
                message.name = $String(object.name);
            if (object.refAttrName != null)
                message.refAttrName = $String(object.refAttrName);
            if (object.docString != null)
                message.docString = $String(object.docString);
            switch (object.type) {
            case "UNDEFINED":
            case 0:
                message.type = 0;
                break;
            case "FLOAT":
            case 1:
                message.type = 1;
                break;
            case "INT":
            case 2:
                message.type = 2;
                break;
            case "STRING":
            case 3:
                message.type = 3;
                break;
            case "TENSOR":
            case 4:
                message.type = 4;
                break;
            case "GRAPH":
            case 5:
                message.type = 5;
                break;
            case "SPARSE_TENSOR":
            case 11:
                message.type = 11;
                break;
            case "TYPE_PROTO":
            case 13:
                message.type = 13;
                break;
            case "FLOATS":
            case 6:
                message.type = 6;
                break;
            case "INTS":
            case 7:
                message.type = 7;
                break;
            case "STRINGS":
            case 8:
                message.type = 8;
                break;
            case "TENSORS":
            case 9:
                message.type = 9;
                break;
            case "GRAPHS":
            case 10:
                message.type = 10;
                break;
            case "SPARSE_TENSORS":
            case 12:
                message.type = 12;
                break;
            case "TYPE_PROTOS":
            case 14:
                message.type = 14;
                break;
            default:
            }
            if (object.f != null)
                message.f = $Number(object.f);
            if (object.i != null)
                if ($util.Long)
                    message.i = $util.Long.fromValue(object.i, false);
                else if (typeof object.i === "string")
                    message.i = $parseInt(object.i, 10);
                else if (typeof object.i === "number")
                    message.i = object.i;
                else if (typeof object.i === "object")
                    message.i = new $util.LongBits(object.i.low >>> 0, object.i.high >>> 0).toNumber();
            if (object.s != null)
                if (typeof object.s === "string")
                    $util.base64.decode(object.s, message.s = $util.newBuffer($util.base64.length(object.s)), 0);
                else if (object.s.length >= 0)
                    message.s = object.s;
            if (object.t != null) {
                if (!$util.isObject(object.t))
                    throw $TypeError(".onnx.AttributeProto.t: object expected");
                message.t = $root.onnx.TensorProto.fromObject(object.t, _depth + 1);
            }
            if (object.g != null) {
                if (!$util.isObject(object.g))
                    throw $TypeError(".onnx.AttributeProto.g: object expected");
                message.g = $root.onnx.GraphProto.fromObject(object.g, _depth + 1);
            }
            if (object.sparseTensor != null) {
                if (!$util.isObject(object.sparseTensor))
                    throw $TypeError(".onnx.AttributeProto.sparseTensor: object expected");
                message.sparseTensor = $root.onnx.SparseTensorProto.fromObject(object.sparseTensor, _depth + 1);
            }
            if (object.tp != null) {
                if (!$util.isObject(object.tp))
                    throw $TypeError(".onnx.AttributeProto.tp: object expected");
                message.tp = $root.onnx.TypeProto.fromObject(object.tp, _depth + 1);
            }
            if (object.floats) {
                if (!$Array.isArray(object.floats))
                    throw $TypeError(".onnx.AttributeProto.floats: array expected");
                message.floats = $Array(object.floats.length);
                for (let i = 0; i < object.floats.length; ++i)
                    message.floats[i] = $Number(object.floats[i]);
            }
            if (object.ints) {
                if (!$Array.isArray(object.ints))
                    throw $TypeError(".onnx.AttributeProto.ints: array expected");
                message.ints = $Array(object.ints.length);
                for (let i = 0; i < object.ints.length; ++i)
                    if ($util.Long)
                        message.ints[i] = $util.Long.fromValue(object.ints[i], false);
                    else if (typeof object.ints[i] === "string")
                        message.ints[i] = $parseInt(object.ints[i], 10);
                    else if (typeof object.ints[i] === "number")
                        message.ints[i] = object.ints[i];
                    else if (typeof object.ints[i] === "object")
                        message.ints[i] = new $util.LongBits(object.ints[i].low >>> 0, object.ints[i].high >>> 0).toNumber();
            }
            if (object.strings) {
                if (!$Array.isArray(object.strings))
                    throw $TypeError(".onnx.AttributeProto.strings: array expected");
                message.strings = $Array(object.strings.length);
                for (let i = 0; i < object.strings.length; ++i)
                    if (typeof object.strings[i] === "string")
                        $util.base64.decode(object.strings[i], message.strings[i] = $util.newBuffer($util.base64.length(object.strings[i])), 0);
                    else if (object.strings[i].length >= 0)
                        message.strings[i] = object.strings[i];
            }
            if (object.tensors) {
                if (!$Array.isArray(object.tensors))
                    throw $TypeError(".onnx.AttributeProto.tensors: array expected");
                message.tensors = $Array(object.tensors.length);
                for (let i = 0; i < object.tensors.length; ++i) {
                    if (!$util.isObject(object.tensors[i]))
                        throw $TypeError(".onnx.AttributeProto.tensors: object expected");
                    message.tensors[i] = $root.onnx.TensorProto.fromObject(object.tensors[i], _depth + 1);
                }
            }
            if (object.graphs) {
                if (!$Array.isArray(object.graphs))
                    throw $TypeError(".onnx.AttributeProto.graphs: array expected");
                message.graphs = $Array(object.graphs.length);
                for (let i = 0; i < object.graphs.length; ++i) {
                    if (!$util.isObject(object.graphs[i]))
                        throw $TypeError(".onnx.AttributeProto.graphs: object expected");
                    message.graphs[i] = $root.onnx.GraphProto.fromObject(object.graphs[i], _depth + 1);
                }
            }
            if (object.sparseTensors) {
                if (!$Array.isArray(object.sparseTensors))
                    throw $TypeError(".onnx.AttributeProto.sparseTensors: array expected");
                message.sparseTensors = $Array(object.sparseTensors.length);
                for (let i = 0; i < object.sparseTensors.length; ++i) {
                    if (!$util.isObject(object.sparseTensors[i]))
                        throw $TypeError(".onnx.AttributeProto.sparseTensors: object expected");
                    message.sparseTensors[i] = $root.onnx.SparseTensorProto.fromObject(object.sparseTensors[i], _depth + 1);
                }
            }
            if (object.typeProtos) {
                if (!$Array.isArray(object.typeProtos))
                    throw $TypeError(".onnx.AttributeProto.typeProtos: array expected");
                message.typeProtos = $Array(object.typeProtos.length);
                for (let i = 0; i < object.typeProtos.length; ++i) {
                    if (!$util.isObject(object.typeProtos[i]))
                        throw $TypeError(".onnx.AttributeProto.typeProtos: object expected");
                    message.typeProtos[i] = $root.onnx.TypeProto.fromObject(object.typeProtos[i], _depth + 1);
                }
            }
            return message;
        };

        /**
         * Creates a plain object from an AttributeProto message. Also converts values to other types if specified.
         * @function toObject
         * @memberof onnx.AttributeProto
         * @static
         * @param {onnx.AttributeProto} message AttributeProto
         * @param {$protobuf.IConversionOptions} [options] Conversion options
         * @returns {Object.<string,*>} Plain object
         */
        AttributeProto.toObject = function (message, options, _depth) {
            if (!options)
                options = {};
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                throw $Error("max depth exceeded");
            let object = {};
            if (options.arrays || options.defaults) {
                object.floats = [];
                object.ints = [];
                object.strings = [];
                object.tensors = [];
                object.graphs = [];
                object.typeProtos = [];
                object.sparseTensors = [];
            }
            if (options.defaults) {
                object.name = "";
                object.f = 0;
                if ($util.Long) {
                    let long = new $util.Long(0, 0, false);
                    object.i = options.longs === $String ? long.toString() : options.longs === $Number ? long.toNumber() : typeof $BigInt !== "undefined" && options.longs === $BigInt ? long.toBigInt() : long;
                } else
                    object.i = options.longs === $String ? "0" : typeof $BigInt !== "undefined" && options.longs === $BigInt ? $BigInt("0") : 0;
                if (options.bytes === $String)
                    object.s = "";
                else {
                    object.s = [];
                    if (options.bytes !== $Array)
                        object.s = $util.newBuffer(object.s);
                }
                object.t = null;
                object.g = null;
                object.docString = "";
                object.tp = null;
                object.type = options.enums === $String ? "UNDEFINED" : 0;
                object.refAttrName = "";
                object.sparseTensor = null;
            }
            if (message.name != null && $Object.hasOwnProperty.call(message, "name"))
                object.name = message.name;
            if (message.f != null && $Object.hasOwnProperty.call(message, "f"))
                object.f = options.json && !$isFinite(message.f) ? $String(message.f) : message.f;
            if (message.i != null && $Object.hasOwnProperty.call(message, "i"))
                if (typeof $BigInt !== "undefined" && options.longs === $BigInt)
                    object.i = typeof message.i === "number" ? $BigInt(message.i) : $util.Long.fromBits(message.i.low >>> 0, message.i.high >>> 0, false).toBigInt();
                else if (typeof message.i === "number")
                    object.i = options.longs === $String ? $String(message.i) : message.i;
                else
                    object.i = options.longs === $String ? $util.Long.prototype.toString.call(message.i) : options.longs === $Number ? new $util.LongBits(message.i.low >>> 0, message.i.high >>> 0).toNumber() : message.i;
            if (message.s != null && $Object.hasOwnProperty.call(message, "s"))
                object.s = options.bytes === $String ? $util.base64.encode(message.s, 0, message.s.length) : options.bytes === $Array ? $Array.prototype.slice.call(message.s) : message.s;
            if (message.t != null && $Object.hasOwnProperty.call(message, "t"))
                object.t = $root.onnx.TensorProto.toObject(message.t, options, _depth + 1);
            if (message.g != null && $Object.hasOwnProperty.call(message, "g"))
                object.g = $root.onnx.GraphProto.toObject(message.g, options, _depth + 1);
            if (message.floats && message.floats.length) {
                object.floats = $Array(message.floats.length);
                for (let j = 0; j < message.floats.length; ++j)
                    object.floats[j] = options.json && !$isFinite(message.floats[j]) ? $String(message.floats[j]) : message.floats[j];
            }
            if (message.ints && message.ints.length) {
                object.ints = $Array(message.ints.length);
                for (let j = 0; j < message.ints.length; ++j)
                    if (typeof $BigInt !== "undefined" && options.longs === $BigInt)
                        object.ints[j] = typeof message.ints[j] === "number" ? $BigInt(message.ints[j]) : $util.Long.fromBits(message.ints[j].low >>> 0, message.ints[j].high >>> 0, false).toBigInt();
                    else if (typeof message.ints[j] === "number")
                        object.ints[j] = options.longs === $String ? $String(message.ints[j]) : message.ints[j];
                    else
                        object.ints[j] = options.longs === $String ? $util.Long.prototype.toString.call(message.ints[j]) : options.longs === $Number ? new $util.LongBits(message.ints[j].low >>> 0, message.ints[j].high >>> 0).toNumber() : message.ints[j];
            }
            if (message.strings && message.strings.length) {
                object.strings = $Array(message.strings.length);
                for (let j = 0; j < message.strings.length; ++j)
                    object.strings[j] = options.bytes === $String ? $util.base64.encode(message.strings[j], 0, message.strings[j].length) : options.bytes === $Array ? $Array.prototype.slice.call(message.strings[j]) : message.strings[j];
            }
            if (message.tensors && message.tensors.length) {
                object.tensors = $Array(message.tensors.length);
                for (let j = 0; j < message.tensors.length; ++j)
                    object.tensors[j] = $root.onnx.TensorProto.toObject(message.tensors[j], options, _depth + 1);
            }
            if (message.graphs && message.graphs.length) {
                object.graphs = $Array(message.graphs.length);
                for (let j = 0; j < message.graphs.length; ++j)
                    object.graphs[j] = $root.onnx.GraphProto.toObject(message.graphs[j], options, _depth + 1);
            }
            if (message.docString != null && $Object.hasOwnProperty.call(message, "docString"))
                object.docString = message.docString;
            if (message.tp != null && $Object.hasOwnProperty.call(message, "tp"))
                object.tp = $root.onnx.TypeProto.toObject(message.tp, options, _depth + 1);
            if (message.typeProtos && message.typeProtos.length) {
                object.typeProtos = $Array(message.typeProtos.length);
                for (let j = 0; j < message.typeProtos.length; ++j)
                    object.typeProtos[j] = $root.onnx.TypeProto.toObject(message.typeProtos[j], options, _depth + 1);
            }
            if (message.type != null && $Object.hasOwnProperty.call(message, "type"))
                object.type = options.enums === $String ? $root.onnx.AttributeProto.AttributeType[message.type] === $undefined ? message.type : $root.onnx.AttributeProto.AttributeType[message.type] : message.type;
            if (message.refAttrName != null && $Object.hasOwnProperty.call(message, "refAttrName"))
                object.refAttrName = message.refAttrName;
            if (message.sparseTensor != null && $Object.hasOwnProperty.call(message, "sparseTensor"))
                object.sparseTensor = $root.onnx.SparseTensorProto.toObject(message.sparseTensor, options, _depth + 1);
            if (message.sparseTensors && message.sparseTensors.length) {
                object.sparseTensors = $Array(message.sparseTensors.length);
                for (let j = 0; j < message.sparseTensors.length; ++j)
                    object.sparseTensors[j] = $root.onnx.SparseTensorProto.toObject(message.sparseTensors[j], options, _depth + 1);
            }
            return object;
        };

        /**
         * Converts this AttributeProto to JSON.
         * @function toJSON
         * @memberof onnx.AttributeProto
         * @instance
         * @returns {Object.<string,*>} JSON object
         */
        AttributeProto.prototype.toJSON = function() {
            return AttributeProto.toObject(this, $protobuf.util.toJSONOptions);
        };

        /**
         * Gets the type url for AttributeProto
         * @function getTypeUrl
         * @memberof onnx.AttributeProto
         * @static
         * @param {string} [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
         * @returns {string} The type url
         */
        AttributeProto.getTypeUrl = function(prefix) {
            if (prefix === $undefined)
                prefix = "type.googleapis.com";
            return prefix + "/onnx.AttributeProto";
        };

        /**
         * AttributeType enum.
         * @name onnx.AttributeProto.AttributeType
         * @enum {number}
         * @property {number} UNDEFINED=0 UNDEFINED value
         * @property {number} FLOAT=1 FLOAT value
         * @property {number} INT=2 INT value
         * @property {number} STRING=3 STRING value
         * @property {number} TENSOR=4 TENSOR value
         * @property {number} GRAPH=5 GRAPH value
         * @property {number} SPARSE_TENSOR=11 SPARSE_TENSOR value
         * @property {number} TYPE_PROTO=13 TYPE_PROTO value
         * @property {number} FLOATS=6 FLOATS value
         * @property {number} INTS=7 INTS value
         * @property {number} STRINGS=8 STRINGS value
         * @property {number} TENSORS=9 TENSORS value
         * @property {number} GRAPHS=10 GRAPHS value
         * @property {number} SPARSE_TENSORS=12 SPARSE_TENSORS value
         * @property {number} TYPE_PROTOS=14 TYPE_PROTOS value
         */
        AttributeProto.AttributeType = (function() {
            const valuesById = $Object.create(null), values = $Object.create(valuesById);
            values[valuesById[0] = "UNDEFINED"] = 0;
            values[valuesById[1] = "FLOAT"] = 1;
            values[valuesById[2] = "INT"] = 2;
            values[valuesById[3] = "STRING"] = 3;
            values[valuesById[4] = "TENSOR"] = 4;
            values[valuesById[5] = "GRAPH"] = 5;
            values[valuesById[11] = "SPARSE_TENSOR"] = 11;
            values[valuesById[13] = "TYPE_PROTO"] = 13;
            values[valuesById[6] = "FLOATS"] = 6;
            values[valuesById[7] = "INTS"] = 7;
            values[valuesById[8] = "STRINGS"] = 8;
            values[valuesById[9] = "TENSORS"] = 9;
            values[valuesById[10] = "GRAPHS"] = 10;
            values[valuesById[12] = "SPARSE_TENSORS"] = 12;
            values[valuesById[14] = "TYPE_PROTOS"] = 14;
            return values;
        })();

        return AttributeProto;
    })();

    onnx.ValueInfoProto = (function() {

        /**
         * Properties of a ValueInfoProto.
         * @typedef {Object} onnx.ValueInfoProto.$Properties
         * @property {string|null} [name] ValueInfoProto name
         * @property {onnx.TypeProto.$Properties|null} [type] ValueInfoProto type
         * @property {string|null} [docString] ValueInfoProto docString
         * @property {Array.<onnx.StringStringEntryProto.$Properties>|null} [metadataProps] ValueInfoProto metadataProps
         * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding when enabled
         */

        /**
         * Properties of a ValueInfoProto.
         * @memberof onnx
         * @interface IValueInfoProto
         * @augments onnx.ValueInfoProto.$Properties
         * @deprecated Use onnx.ValueInfoProto.$Properties instead.
         */

        /**
         * Shape of a ValueInfoProto.
         * @typedef {{
         *   name?: string|null;
         *   type?: onnx.TypeProto.$Shape|null;
         *   docString?: string|null;
         *   metadataProps?: Array.<onnx.StringStringEntryProto.$Shape>|null;
         *   $unknowns?: Array.<Uint8Array>;
         * }} onnx.ValueInfoProto.$Shape
         */

        /**
         * Constructs a new ValueInfoProto.
         * @memberof onnx
         * @classdesc Represents a ValueInfoProto.
         * @constructor
         * @param {onnx.ValueInfoProto.$Properties=} [properties] Properties to set
         * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding when enabled
         */
        const ValueInfoProto = function (properties) {
            this.metadataProps = [];
            if (properties)
                for (let keys = $Object.keys(properties), i = 0; i < keys.length; ++i)
                    if (properties[keys[i]] != null && keys[i] !== "__proto__")
                        this[keys[i]] = properties[keys[i]];
        };

        /**
         * ValueInfoProto name.
         * @member {string} name
         * @memberof onnx.ValueInfoProto
         * @instance
         */
        ValueInfoProto.prototype.name = "";

        /**
         * ValueInfoProto type.
         * @member {onnx.TypeProto.$Properties|null|undefined} type
         * @memberof onnx.ValueInfoProto
         * @instance
         */
        ValueInfoProto.prototype.type = null;

        /**
         * ValueInfoProto docString.
         * @member {string} docString
         * @memberof onnx.ValueInfoProto
         * @instance
         */
        ValueInfoProto.prototype.docString = "";

        /**
         * ValueInfoProto metadataProps.
         * @member {Array.<onnx.StringStringEntryProto.$Properties>} metadataProps
         * @memberof onnx.ValueInfoProto
         * @instance
         */
        ValueInfoProto.prototype.metadataProps = $util.emptyArray;

        /**
         * Creates a new ValueInfoProto instance using the specified properties.
         * @function create
         * @memberof onnx.ValueInfoProto
         * @static
         * @param {onnx.ValueInfoProto.$Properties=} [properties] Properties to set
         * @returns {onnx.ValueInfoProto} ValueInfoProto instance
         * @type {{
         *   (properties: onnx.ValueInfoProto.$Shape): onnx.ValueInfoProto & onnx.ValueInfoProto.$Shape;
         *   (properties?: onnx.ValueInfoProto.$Properties): onnx.ValueInfoProto;
         * }}
         */
        ValueInfoProto.create = function(properties) {
            return new ValueInfoProto(properties);
        };

        /**
         * Encodes the specified ValueInfoProto message. Does not implicitly {@link onnx.ValueInfoProto.verify|verify} messages.
         * @function encode
         * @memberof onnx.ValueInfoProto
         * @static
         * @param {onnx.ValueInfoProto.$Properties} message ValueInfoProto message or plain object to encode
         * @param {$protobuf.Writer} [writer] Writer to encode to
         * @returns {$protobuf.Writer} Writer
         */
        ValueInfoProto.encode = function (message, writer, _depth) {
            if (!writer)
                writer = $Writer.create();
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                throw $Error("max depth exceeded");
            if (message.name != null && $Object.hasOwnProperty.call(message, "name"))
                writer.uint32(/* id 1, wireType 2 =*/10).string(message.name);
            if (message.type != null && $Object.hasOwnProperty.call(message, "type"))
                $root.onnx.TypeProto.encode(message.type, writer.uint32(/* id 2, wireType 2 =*/18).fork(), _depth + 1).ldelim();
            if (message.docString != null && $Object.hasOwnProperty.call(message, "docString"))
                writer.uint32(/* id 3, wireType 2 =*/26).string(message.docString);
            if (message.metadataProps != null && message.metadataProps.length)
                for (let i = 0; i < message.metadataProps.length; ++i)
                    $root.onnx.StringStringEntryProto.encode(message.metadataProps[i], writer.uint32(/* id 4, wireType 2 =*/34).fork(), _depth + 1).ldelim();
            if (message.$unknowns != null && $Object.hasOwnProperty.call(message, "$unknowns"))
                for (let i = 0; i < message.$unknowns.length; ++i)
                    writer.raw(message.$unknowns[i]);
            return writer;
        };

        /**
         * Encodes the specified ValueInfoProto message, length delimited. Does not implicitly {@link onnx.ValueInfoProto.verify|verify} messages.
         * @function encodeDelimited
         * @memberof onnx.ValueInfoProto
         * @static
         * @param {onnx.ValueInfoProto.$Properties} message ValueInfoProto message or plain object to encode
         * @param {$protobuf.Writer} [writer] Writer to encode to
         * @returns {$protobuf.Writer} Writer
         */
        ValueInfoProto.encodeDelimited = function(message, writer) {
            return this.encode(message, (writer || $Writer.create()).fork()).ldelim();
        };

        /**
         * Decodes a ValueInfoProto message from the specified reader or buffer.
         * @function decode
         * @memberof onnx.ValueInfoProto
         * @static
         * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
         * @param {number} [length] Message length if known beforehand
         * @returns {onnx.ValueInfoProto & onnx.ValueInfoProto.$Shape} ValueInfoProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        ValueInfoProto.decode = function (reader, length, _end, _depth, _target) {
            if (!(reader instanceof $Reader))
                reader = $Reader.create(reader);
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $Reader.recursionLimit)
                throw $Error("max depth exceeded");
            let end = length === $undefined ? reader.len : reader.pos + length, message = _target || new $root.onnx.ValueInfoProto();
            while (reader.pos < end) {
                let start = reader.pos;
                let tag = reader.tag();
                if (tag === _end) {
                    _end = $undefined;
                    break;
                }
                let wireType = tag & 7;
                switch (tag >>>= 3) {
                case 1: {
                        if (wireType !== 2)
                            break;
                        message.name = reader.string();
                        continue;
                    }
                case 2: {
                        if (wireType !== 2)
                            break;
                        message.type = $root.onnx.TypeProto.decode(reader, reader.uint32(), $undefined, _depth + 1, message.type);
                        continue;
                    }
                case 3: {
                        if (wireType !== 2)
                            break;
                        message.docString = reader.string();
                        continue;
                    }
                case 4: {
                        if (wireType !== 2)
                            break;
                        if (!(message.metadataProps && message.metadataProps.length))
                            message.metadataProps = [];
                        message.metadataProps.push($root.onnx.StringStringEntryProto.decode(reader, reader.uint32(), $undefined, _depth + 1));
                        continue;
                    }
                }
                reader.skipType(wireType, _depth, tag);
                if (!reader.discardUnknown) {
                    $util.makeProp(message, "$unknowns", false);
                    (message.$unknowns || (message.$unknowns = [])).push(reader.raw(start, reader.pos));
                }
            }
            if (_end !== $undefined)
                throw $Error("missing end group");
            return message;
        };

        /**
         * Decodes a ValueInfoProto message from the specified reader or buffer, length delimited.
         * @function decodeDelimited
         * @memberof onnx.ValueInfoProto
         * @static
         * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
         * @returns {onnx.ValueInfoProto & onnx.ValueInfoProto.$Shape} ValueInfoProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        ValueInfoProto.decodeDelimited = function(reader) {
            if (!(reader instanceof $Reader))
                reader = new $Reader(reader);
            return this.decode(reader, reader.uint32());
        };

        /**
         * Verifies a ValueInfoProto message.
         * @function verify
         * @memberof onnx.ValueInfoProto
         * @static
         * @param {Object.<string,*>} message Plain object to verify
         * @returns {string|null} `null` if valid, otherwise the reason why it is not
         */
        ValueInfoProto.verify = function (message, _depth) {
            if (typeof message !== "object" || message === null)
                return "object expected";
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                return "max depth exceeded";
            if (message.name != null && $Object.hasOwnProperty.call(message, "name"))
                if (!$util.isString(message.name))
                    return "name: string expected";
            if (message.type != null && $Object.hasOwnProperty.call(message, "type")) {
                let error = $root.onnx.TypeProto.verify(message.type, _depth + 1);
                if (error)
                    return "type." + error;
            }
            if (message.docString != null && $Object.hasOwnProperty.call(message, "docString"))
                if (!$util.isString(message.docString))
                    return "docString: string expected";
            if (message.metadataProps != null && $Object.hasOwnProperty.call(message, "metadataProps")) {
                if (!$Array.isArray(message.metadataProps))
                    return "metadataProps: array expected";
                for (let i = 0; i < message.metadataProps.length; ++i) {
                    let error = $root.onnx.StringStringEntryProto.verify(message.metadataProps[i], _depth + 1);
                    if (error)
                        return "metadataProps." + error;
                }
            }
            return null;
        };

        /**
         * Creates a ValueInfoProto message from a plain object. Also converts values to their respective internal types.
         * @function fromObject
         * @memberof onnx.ValueInfoProto
         * @static
         * @param {Object.<string,*>} object Plain object
         * @returns {onnx.ValueInfoProto} ValueInfoProto
         */
        ValueInfoProto.fromObject = function (object, _depth) {
            if (object instanceof $root.onnx.ValueInfoProto)
                return object;
            if (!$util.isObject(object))
                throw $TypeError(".onnx.ValueInfoProto: object expected");
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                throw $Error("max depth exceeded");
            let message = new $root.onnx.ValueInfoProto();
            if (object.name != null)
                message.name = $String(object.name);
            if (object.type != null) {
                if (!$util.isObject(object.type))
                    throw $TypeError(".onnx.ValueInfoProto.type: object expected");
                message.type = $root.onnx.TypeProto.fromObject(object.type, _depth + 1);
            }
            if (object.docString != null)
                message.docString = $String(object.docString);
            if (object.metadataProps) {
                if (!$Array.isArray(object.metadataProps))
                    throw $TypeError(".onnx.ValueInfoProto.metadataProps: array expected");
                message.metadataProps = $Array(object.metadataProps.length);
                for (let i = 0; i < object.metadataProps.length; ++i) {
                    if (!$util.isObject(object.metadataProps[i]))
                        throw $TypeError(".onnx.ValueInfoProto.metadataProps: object expected");
                    message.metadataProps[i] = $root.onnx.StringStringEntryProto.fromObject(object.metadataProps[i], _depth + 1);
                }
            }
            return message;
        };

        /**
         * Creates a plain object from a ValueInfoProto message. Also converts values to other types if specified.
         * @function toObject
         * @memberof onnx.ValueInfoProto
         * @static
         * @param {onnx.ValueInfoProto} message ValueInfoProto
         * @param {$protobuf.IConversionOptions} [options] Conversion options
         * @returns {Object.<string,*>} Plain object
         */
        ValueInfoProto.toObject = function (message, options, _depth) {
            if (!options)
                options = {};
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                throw $Error("max depth exceeded");
            let object = {};
            if (options.arrays || options.defaults)
                object.metadataProps = [];
            if (options.defaults) {
                object.name = "";
                object.type = null;
                object.docString = "";
            }
            if (message.name != null && $Object.hasOwnProperty.call(message, "name"))
                object.name = message.name;
            if (message.type != null && $Object.hasOwnProperty.call(message, "type"))
                object.type = $root.onnx.TypeProto.toObject(message.type, options, _depth + 1);
            if (message.docString != null && $Object.hasOwnProperty.call(message, "docString"))
                object.docString = message.docString;
            if (message.metadataProps && message.metadataProps.length) {
                object.metadataProps = $Array(message.metadataProps.length);
                for (let j = 0; j < message.metadataProps.length; ++j)
                    object.metadataProps[j] = $root.onnx.StringStringEntryProto.toObject(message.metadataProps[j], options, _depth + 1);
            }
            return object;
        };

        /**
         * Converts this ValueInfoProto to JSON.
         * @function toJSON
         * @memberof onnx.ValueInfoProto
         * @instance
         * @returns {Object.<string,*>} JSON object
         */
        ValueInfoProto.prototype.toJSON = function() {
            return ValueInfoProto.toObject(this, $protobuf.util.toJSONOptions);
        };

        /**
         * Gets the type url for ValueInfoProto
         * @function getTypeUrl
         * @memberof onnx.ValueInfoProto
         * @static
         * @param {string} [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
         * @returns {string} The type url
         */
        ValueInfoProto.getTypeUrl = function(prefix) {
            if (prefix === $undefined)
                prefix = "type.googleapis.com";
            return prefix + "/onnx.ValueInfoProto";
        };

        return ValueInfoProto;
    })();

    onnx.NodeProto = (function() {

        /**
         * Properties of a NodeProto.
         * @typedef {Object} onnx.NodeProto.$Properties
         * @property {Array.<string>|null} [input] NodeProto input
         * @property {Array.<string>|null} [output] NodeProto output
         * @property {string|null} [name] NodeProto name
         * @property {string|null} [opType] NodeProto opType
         * @property {string|null} [domain] NodeProto domain
         * @property {string|null} [overload] NodeProto overload
         * @property {Array.<onnx.AttributeProto.$Properties>|null} [attribute] NodeProto attribute
         * @property {string|null} [docString] NodeProto docString
         * @property {Array.<onnx.StringStringEntryProto.$Properties>|null} [metadataProps] NodeProto metadataProps
         * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding when enabled
         */

        /**
         * Properties of a NodeProto.
         * @memberof onnx
         * @interface INodeProto
         * @augments onnx.NodeProto.$Properties
         * @deprecated Use onnx.NodeProto.$Properties instead.
         */

        /**
         * Shape of a NodeProto.
         * @typedef {{
         *   input?: Array.<string>|null;
         *   output?: Array.<string>|null;
         *   name?: string|null;
         *   opType?: string|null;
         *   domain?: string|null;
         *   overload?: string|null;
         *   attribute?: Array.<onnx.AttributeProto.$Shape>|null;
         *   docString?: string|null;
         *   metadataProps?: Array.<onnx.StringStringEntryProto.$Shape>|null;
         *   $unknowns?: Array.<Uint8Array>;
         * }} onnx.NodeProto.$Shape
         */

        /**
         * Constructs a new NodeProto.
         * @memberof onnx
         * @classdesc Represents a NodeProto.
         * @constructor
         * @param {onnx.NodeProto.$Properties=} [properties] Properties to set
         * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding when enabled
         */
        const NodeProto = function (properties) {
            this.input = [];
            this.output = [];
            this.attribute = [];
            this.metadataProps = [];
            if (properties)
                for (let keys = $Object.keys(properties), i = 0; i < keys.length; ++i)
                    if (properties[keys[i]] != null && keys[i] !== "__proto__")
                        this[keys[i]] = properties[keys[i]];
        };

        /**
         * NodeProto input.
         * @member {Array.<string>} input
         * @memberof onnx.NodeProto
         * @instance
         */
        NodeProto.prototype.input = $util.emptyArray;

        /**
         * NodeProto output.
         * @member {Array.<string>} output
         * @memberof onnx.NodeProto
         * @instance
         */
        NodeProto.prototype.output = $util.emptyArray;

        /**
         * NodeProto name.
         * @member {string} name
         * @memberof onnx.NodeProto
         * @instance
         */
        NodeProto.prototype.name = "";

        /**
         * NodeProto opType.
         * @member {string} opType
         * @memberof onnx.NodeProto
         * @instance
         */
        NodeProto.prototype.opType = "";

        /**
         * NodeProto domain.
         * @member {string} domain
         * @memberof onnx.NodeProto
         * @instance
         */
        NodeProto.prototype.domain = "";

        /**
         * NodeProto overload.
         * @member {string} overload
         * @memberof onnx.NodeProto
         * @instance
         */
        NodeProto.prototype.overload = "";

        /**
         * NodeProto attribute.
         * @member {Array.<onnx.AttributeProto.$Properties>} attribute
         * @memberof onnx.NodeProto
         * @instance
         */
        NodeProto.prototype.attribute = $util.emptyArray;

        /**
         * NodeProto docString.
         * @member {string} docString
         * @memberof onnx.NodeProto
         * @instance
         */
        NodeProto.prototype.docString = "";

        /**
         * NodeProto metadataProps.
         * @member {Array.<onnx.StringStringEntryProto.$Properties>} metadataProps
         * @memberof onnx.NodeProto
         * @instance
         */
        NodeProto.prototype.metadataProps = $util.emptyArray;

        /**
         * Creates a new NodeProto instance using the specified properties.
         * @function create
         * @memberof onnx.NodeProto
         * @static
         * @param {onnx.NodeProto.$Properties=} [properties] Properties to set
         * @returns {onnx.NodeProto} NodeProto instance
         * @type {{
         *   (properties: onnx.NodeProto.$Shape): onnx.NodeProto & onnx.NodeProto.$Shape;
         *   (properties?: onnx.NodeProto.$Properties): onnx.NodeProto;
         * }}
         */
        NodeProto.create = function(properties) {
            return new NodeProto(properties);
        };

        /**
         * Encodes the specified NodeProto message. Does not implicitly {@link onnx.NodeProto.verify|verify} messages.
         * @function encode
         * @memberof onnx.NodeProto
         * @static
         * @param {onnx.NodeProto.$Properties} message NodeProto message or plain object to encode
         * @param {$protobuf.Writer} [writer] Writer to encode to
         * @returns {$protobuf.Writer} Writer
         */
        NodeProto.encode = function (message, writer, _depth) {
            if (!writer)
                writer = $Writer.create();
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                throw $Error("max depth exceeded");
            if (message.input != null && message.input.length)
                for (let i = 0; i < message.input.length; ++i)
                    writer.uint32(/* id 1, wireType 2 =*/10).string(message.input[i]);
            if (message.output != null && message.output.length)
                for (let i = 0; i < message.output.length; ++i)
                    writer.uint32(/* id 2, wireType 2 =*/18).string(message.output[i]);
            if (message.name != null && $Object.hasOwnProperty.call(message, "name"))
                writer.uint32(/* id 3, wireType 2 =*/26).string(message.name);
            if (message.opType != null && $Object.hasOwnProperty.call(message, "opType"))
                writer.uint32(/* id 4, wireType 2 =*/34).string(message.opType);
            if (message.attribute != null && message.attribute.length)
                for (let i = 0; i < message.attribute.length; ++i)
                    $root.onnx.AttributeProto.encode(message.attribute[i], writer.uint32(/* id 5, wireType 2 =*/42).fork(), _depth + 1).ldelim();
            if (message.docString != null && $Object.hasOwnProperty.call(message, "docString"))
                writer.uint32(/* id 6, wireType 2 =*/50).string(message.docString);
            if (message.domain != null && $Object.hasOwnProperty.call(message, "domain"))
                writer.uint32(/* id 7, wireType 2 =*/58).string(message.domain);
            if (message.overload != null && $Object.hasOwnProperty.call(message, "overload"))
                writer.uint32(/* id 8, wireType 2 =*/66).string(message.overload);
            if (message.metadataProps != null && message.metadataProps.length)
                for (let i = 0; i < message.metadataProps.length; ++i)
                    $root.onnx.StringStringEntryProto.encode(message.metadataProps[i], writer.uint32(/* id 9, wireType 2 =*/74).fork(), _depth + 1).ldelim();
            if (message.$unknowns != null && $Object.hasOwnProperty.call(message, "$unknowns"))
                for (let i = 0; i < message.$unknowns.length; ++i)
                    writer.raw(message.$unknowns[i]);
            return writer;
        };

        /**
         * Encodes the specified NodeProto message, length delimited. Does not implicitly {@link onnx.NodeProto.verify|verify} messages.
         * @function encodeDelimited
         * @memberof onnx.NodeProto
         * @static
         * @param {onnx.NodeProto.$Properties} message NodeProto message or plain object to encode
         * @param {$protobuf.Writer} [writer] Writer to encode to
         * @returns {$protobuf.Writer} Writer
         */
        NodeProto.encodeDelimited = function(message, writer) {
            return this.encode(message, (writer || $Writer.create()).fork()).ldelim();
        };

        /**
         * Decodes a NodeProto message from the specified reader or buffer.
         * @function decode
         * @memberof onnx.NodeProto
         * @static
         * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
         * @param {number} [length] Message length if known beforehand
         * @returns {onnx.NodeProto & onnx.NodeProto.$Shape} NodeProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        NodeProto.decode = function (reader, length, _end, _depth, _target) {
            if (!(reader instanceof $Reader))
                reader = $Reader.create(reader);
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $Reader.recursionLimit)
                throw $Error("max depth exceeded");
            let end = length === $undefined ? reader.len : reader.pos + length, message = _target || new $root.onnx.NodeProto();
            while (reader.pos < end) {
                let start = reader.pos;
                let tag = reader.tag();
                if (tag === _end) {
                    _end = $undefined;
                    break;
                }
                let wireType = tag & 7;
                switch (tag >>>= 3) {
                case 1: {
                        if (wireType !== 2)
                            break;
                        if (!(message.input && message.input.length))
                            message.input = [];
                        message.input.push(reader.string());
                        continue;
                    }
                case 2: {
                        if (wireType !== 2)
                            break;
                        if (!(message.output && message.output.length))
                            message.output = [];
                        message.output.push(reader.string());
                        continue;
                    }
                case 3: {
                        if (wireType !== 2)
                            break;
                        message.name = reader.string();
                        continue;
                    }
                case 4: {
                        if (wireType !== 2)
                            break;
                        message.opType = reader.string();
                        continue;
                    }
                case 7: {
                        if (wireType !== 2)
                            break;
                        message.domain = reader.string();
                        continue;
                    }
                case 8: {
                        if (wireType !== 2)
                            break;
                        message.overload = reader.string();
                        continue;
                    }
                case 5: {
                        if (wireType !== 2)
                            break;
                        if (!(message.attribute && message.attribute.length))
                            message.attribute = [];
                        message.attribute.push($root.onnx.AttributeProto.decode(reader, reader.uint32(), $undefined, _depth + 1));
                        continue;
                    }
                case 6: {
                        if (wireType !== 2)
                            break;
                        message.docString = reader.string();
                        continue;
                    }
                case 9: {
                        if (wireType !== 2)
                            break;
                        if (!(message.metadataProps && message.metadataProps.length))
                            message.metadataProps = [];
                        message.metadataProps.push($root.onnx.StringStringEntryProto.decode(reader, reader.uint32(), $undefined, _depth + 1));
                        continue;
                    }
                }
                reader.skipType(wireType, _depth, tag);
                if (!reader.discardUnknown) {
                    $util.makeProp(message, "$unknowns", false);
                    (message.$unknowns || (message.$unknowns = [])).push(reader.raw(start, reader.pos));
                }
            }
            if (_end !== $undefined)
                throw $Error("missing end group");
            return message;
        };

        /**
         * Decodes a NodeProto message from the specified reader or buffer, length delimited.
         * @function decodeDelimited
         * @memberof onnx.NodeProto
         * @static
         * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
         * @returns {onnx.NodeProto & onnx.NodeProto.$Shape} NodeProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        NodeProto.decodeDelimited = function(reader) {
            if (!(reader instanceof $Reader))
                reader = new $Reader(reader);
            return this.decode(reader, reader.uint32());
        };

        /**
         * Verifies a NodeProto message.
         * @function verify
         * @memberof onnx.NodeProto
         * @static
         * @param {Object.<string,*>} message Plain object to verify
         * @returns {string|null} `null` if valid, otherwise the reason why it is not
         */
        NodeProto.verify = function (message, _depth) {
            if (typeof message !== "object" || message === null)
                return "object expected";
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                return "max depth exceeded";
            if (message.input != null && $Object.hasOwnProperty.call(message, "input")) {
                if (!$Array.isArray(message.input))
                    return "input: array expected";
                for (let i = 0; i < message.input.length; ++i)
                    if (!$util.isString(message.input[i]))
                        return "input: string[] expected";
            }
            if (message.output != null && $Object.hasOwnProperty.call(message, "output")) {
                if (!$Array.isArray(message.output))
                    return "output: array expected";
                for (let i = 0; i < message.output.length; ++i)
                    if (!$util.isString(message.output[i]))
                        return "output: string[] expected";
            }
            if (message.name != null && $Object.hasOwnProperty.call(message, "name"))
                if (!$util.isString(message.name))
                    return "name: string expected";
            if (message.opType != null && $Object.hasOwnProperty.call(message, "opType"))
                if (!$util.isString(message.opType))
                    return "opType: string expected";
            if (message.domain != null && $Object.hasOwnProperty.call(message, "domain"))
                if (!$util.isString(message.domain))
                    return "domain: string expected";
            if (message.overload != null && $Object.hasOwnProperty.call(message, "overload"))
                if (!$util.isString(message.overload))
                    return "overload: string expected";
            if (message.attribute != null && $Object.hasOwnProperty.call(message, "attribute")) {
                if (!$Array.isArray(message.attribute))
                    return "attribute: array expected";
                for (let i = 0; i < message.attribute.length; ++i) {
                    let error = $root.onnx.AttributeProto.verify(message.attribute[i], _depth + 1);
                    if (error)
                        return "attribute." + error;
                }
            }
            if (message.docString != null && $Object.hasOwnProperty.call(message, "docString"))
                if (!$util.isString(message.docString))
                    return "docString: string expected";
            if (message.metadataProps != null && $Object.hasOwnProperty.call(message, "metadataProps")) {
                if (!$Array.isArray(message.metadataProps))
                    return "metadataProps: array expected";
                for (let i = 0; i < message.metadataProps.length; ++i) {
                    let error = $root.onnx.StringStringEntryProto.verify(message.metadataProps[i], _depth + 1);
                    if (error)
                        return "metadataProps." + error;
                }
            }
            return null;
        };

        /**
         * Creates a NodeProto message from a plain object. Also converts values to their respective internal types.
         * @function fromObject
         * @memberof onnx.NodeProto
         * @static
         * @param {Object.<string,*>} object Plain object
         * @returns {onnx.NodeProto} NodeProto
         */
        NodeProto.fromObject = function (object, _depth) {
            if (object instanceof $root.onnx.NodeProto)
                return object;
            if (!$util.isObject(object))
                throw $TypeError(".onnx.NodeProto: object expected");
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                throw $Error("max depth exceeded");
            let message = new $root.onnx.NodeProto();
            if (object.input) {
                if (!$Array.isArray(object.input))
                    throw $TypeError(".onnx.NodeProto.input: array expected");
                message.input = $Array(object.input.length);
                for (let i = 0; i < object.input.length; ++i)
                    message.input[i] = $String(object.input[i]);
            }
            if (object.output) {
                if (!$Array.isArray(object.output))
                    throw $TypeError(".onnx.NodeProto.output: array expected");
                message.output = $Array(object.output.length);
                for (let i = 0; i < object.output.length; ++i)
                    message.output[i] = $String(object.output[i]);
            }
            if (object.name != null)
                message.name = $String(object.name);
            if (object.opType != null)
                message.opType = $String(object.opType);
            if (object.domain != null)
                message.domain = $String(object.domain);
            if (object.overload != null)
                message.overload = $String(object.overload);
            if (object.attribute) {
                if (!$Array.isArray(object.attribute))
                    throw $TypeError(".onnx.NodeProto.attribute: array expected");
                message.attribute = $Array(object.attribute.length);
                for (let i = 0; i < object.attribute.length; ++i) {
                    if (!$util.isObject(object.attribute[i]))
                        throw $TypeError(".onnx.NodeProto.attribute: object expected");
                    message.attribute[i] = $root.onnx.AttributeProto.fromObject(object.attribute[i], _depth + 1);
                }
            }
            if (object.docString != null)
                message.docString = $String(object.docString);
            if (object.metadataProps) {
                if (!$Array.isArray(object.metadataProps))
                    throw $TypeError(".onnx.NodeProto.metadataProps: array expected");
                message.metadataProps = $Array(object.metadataProps.length);
                for (let i = 0; i < object.metadataProps.length; ++i) {
                    if (!$util.isObject(object.metadataProps[i]))
                        throw $TypeError(".onnx.NodeProto.metadataProps: object expected");
                    message.metadataProps[i] = $root.onnx.StringStringEntryProto.fromObject(object.metadataProps[i], _depth + 1);
                }
            }
            return message;
        };

        /**
         * Creates a plain object from a NodeProto message. Also converts values to other types if specified.
         * @function toObject
         * @memberof onnx.NodeProto
         * @static
         * @param {onnx.NodeProto} message NodeProto
         * @param {$protobuf.IConversionOptions} [options] Conversion options
         * @returns {Object.<string,*>} Plain object
         */
        NodeProto.toObject = function (message, options, _depth) {
            if (!options)
                options = {};
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                throw $Error("max depth exceeded");
            let object = {};
            if (options.arrays || options.defaults) {
                object.input = [];
                object.output = [];
                object.attribute = [];
                object.metadataProps = [];
            }
            if (options.defaults) {
                object.name = "";
                object.opType = "";
                object.docString = "";
                object.domain = "";
                object.overload = "";
            }
            if (message.input && message.input.length) {
                object.input = $Array(message.input.length);
                for (let j = 0; j < message.input.length; ++j)
                    object.input[j] = message.input[j];
            }
            if (message.output && message.output.length) {
                object.output = $Array(message.output.length);
                for (let j = 0; j < message.output.length; ++j)
                    object.output[j] = message.output[j];
            }
            if (message.name != null && $Object.hasOwnProperty.call(message, "name"))
                object.name = message.name;
            if (message.opType != null && $Object.hasOwnProperty.call(message, "opType"))
                object.opType = message.opType;
            if (message.attribute && message.attribute.length) {
                object.attribute = $Array(message.attribute.length);
                for (let j = 0; j < message.attribute.length; ++j)
                    object.attribute[j] = $root.onnx.AttributeProto.toObject(message.attribute[j], options, _depth + 1);
            }
            if (message.docString != null && $Object.hasOwnProperty.call(message, "docString"))
                object.docString = message.docString;
            if (message.domain != null && $Object.hasOwnProperty.call(message, "domain"))
                object.domain = message.domain;
            if (message.overload != null && $Object.hasOwnProperty.call(message, "overload"))
                object.overload = message.overload;
            if (message.metadataProps && message.metadataProps.length) {
                object.metadataProps = $Array(message.metadataProps.length);
                for (let j = 0; j < message.metadataProps.length; ++j)
                    object.metadataProps[j] = $root.onnx.StringStringEntryProto.toObject(message.metadataProps[j], options, _depth + 1);
            }
            return object;
        };

        /**
         * Converts this NodeProto to JSON.
         * @function toJSON
         * @memberof onnx.NodeProto
         * @instance
         * @returns {Object.<string,*>} JSON object
         */
        NodeProto.prototype.toJSON = function() {
            return NodeProto.toObject(this, $protobuf.util.toJSONOptions);
        };

        /**
         * Gets the type url for NodeProto
         * @function getTypeUrl
         * @memberof onnx.NodeProto
         * @static
         * @param {string} [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
         * @returns {string} The type url
         */
        NodeProto.getTypeUrl = function(prefix) {
            if (prefix === $undefined)
                prefix = "type.googleapis.com";
            return prefix + "/onnx.NodeProto";
        };

        return NodeProto;
    })();

    onnx.TrainingInfoProto = (function() {

        /**
         * Properties of a TrainingInfoProto.
         * @typedef {Object} onnx.TrainingInfoProto.$Properties
         * @property {onnx.GraphProto.$Properties|null} [initialization] TrainingInfoProto initialization
         * @property {onnx.GraphProto.$Properties|null} [algorithm] TrainingInfoProto algorithm
         * @property {Array.<onnx.StringStringEntryProto.$Properties>|null} [initializationBinding] TrainingInfoProto initializationBinding
         * @property {Array.<onnx.StringStringEntryProto.$Properties>|null} [updateBinding] TrainingInfoProto updateBinding
         * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding when enabled
         */

        /**
         * Properties of a TrainingInfoProto.
         * @memberof onnx
         * @interface ITrainingInfoProto
         * @augments onnx.TrainingInfoProto.$Properties
         * @deprecated Use onnx.TrainingInfoProto.$Properties instead.
         */

        /**
         * Shape of a TrainingInfoProto.
         * @typedef {{
         *   initialization?: onnx.GraphProto.$Shape|null;
         *   algorithm?: onnx.GraphProto.$Shape|null;
         *   initializationBinding?: Array.<onnx.StringStringEntryProto.$Shape>|null;
         *   updateBinding?: Array.<onnx.StringStringEntryProto.$Shape>|null;
         *   $unknowns?: Array.<Uint8Array>;
         * }} onnx.TrainingInfoProto.$Shape
         */

        /**
         * Constructs a new TrainingInfoProto.
         * @memberof onnx
         * @classdesc Represents a TrainingInfoProto.
         * @constructor
         * @param {onnx.TrainingInfoProto.$Properties=} [properties] Properties to set
         * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding when enabled
         */
        const TrainingInfoProto = function (properties) {
            this.initializationBinding = [];
            this.updateBinding = [];
            if (properties)
                for (let keys = $Object.keys(properties), i = 0; i < keys.length; ++i)
                    if (properties[keys[i]] != null && keys[i] !== "__proto__")
                        this[keys[i]] = properties[keys[i]];
        };

        /**
         * TrainingInfoProto initialization.
         * @member {onnx.GraphProto.$Properties|null|undefined} initialization
         * @memberof onnx.TrainingInfoProto
         * @instance
         */
        TrainingInfoProto.prototype.initialization = null;

        /**
         * TrainingInfoProto algorithm.
         * @member {onnx.GraphProto.$Properties|null|undefined} algorithm
         * @memberof onnx.TrainingInfoProto
         * @instance
         */
        TrainingInfoProto.prototype.algorithm = null;

        /**
         * TrainingInfoProto initializationBinding.
         * @member {Array.<onnx.StringStringEntryProto.$Properties>} initializationBinding
         * @memberof onnx.TrainingInfoProto
         * @instance
         */
        TrainingInfoProto.prototype.initializationBinding = $util.emptyArray;

        /**
         * TrainingInfoProto updateBinding.
         * @member {Array.<onnx.StringStringEntryProto.$Properties>} updateBinding
         * @memberof onnx.TrainingInfoProto
         * @instance
         */
        TrainingInfoProto.prototype.updateBinding = $util.emptyArray;

        /**
         * Creates a new TrainingInfoProto instance using the specified properties.
         * @function create
         * @memberof onnx.TrainingInfoProto
         * @static
         * @param {onnx.TrainingInfoProto.$Properties=} [properties] Properties to set
         * @returns {onnx.TrainingInfoProto} TrainingInfoProto instance
         * @type {{
         *   (properties: onnx.TrainingInfoProto.$Shape): onnx.TrainingInfoProto & onnx.TrainingInfoProto.$Shape;
         *   (properties?: onnx.TrainingInfoProto.$Properties): onnx.TrainingInfoProto;
         * }}
         */
        TrainingInfoProto.create = function(properties) {
            return new TrainingInfoProto(properties);
        };

        /**
         * Encodes the specified TrainingInfoProto message. Does not implicitly {@link onnx.TrainingInfoProto.verify|verify} messages.
         * @function encode
         * @memberof onnx.TrainingInfoProto
         * @static
         * @param {onnx.TrainingInfoProto.$Properties} message TrainingInfoProto message or plain object to encode
         * @param {$protobuf.Writer} [writer] Writer to encode to
         * @returns {$protobuf.Writer} Writer
         */
        TrainingInfoProto.encode = function (message, writer, _depth) {
            if (!writer)
                writer = $Writer.create();
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                throw $Error("max depth exceeded");
            if (message.initialization != null && $Object.hasOwnProperty.call(message, "initialization"))
                $root.onnx.GraphProto.encode(message.initialization, writer.uint32(/* id 1, wireType 2 =*/10).fork(), _depth + 1).ldelim();
            if (message.algorithm != null && $Object.hasOwnProperty.call(message, "algorithm"))
                $root.onnx.GraphProto.encode(message.algorithm, writer.uint32(/* id 2, wireType 2 =*/18).fork(), _depth + 1).ldelim();
            if (message.initializationBinding != null && message.initializationBinding.length)
                for (let i = 0; i < message.initializationBinding.length; ++i)
                    $root.onnx.StringStringEntryProto.encode(message.initializationBinding[i], writer.uint32(/* id 3, wireType 2 =*/26).fork(), _depth + 1).ldelim();
            if (message.updateBinding != null && message.updateBinding.length)
                for (let i = 0; i < message.updateBinding.length; ++i)
                    $root.onnx.StringStringEntryProto.encode(message.updateBinding[i], writer.uint32(/* id 4, wireType 2 =*/34).fork(), _depth + 1).ldelim();
            if (message.$unknowns != null && $Object.hasOwnProperty.call(message, "$unknowns"))
                for (let i = 0; i < message.$unknowns.length; ++i)
                    writer.raw(message.$unknowns[i]);
            return writer;
        };

        /**
         * Encodes the specified TrainingInfoProto message, length delimited. Does not implicitly {@link onnx.TrainingInfoProto.verify|verify} messages.
         * @function encodeDelimited
         * @memberof onnx.TrainingInfoProto
         * @static
         * @param {onnx.TrainingInfoProto.$Properties} message TrainingInfoProto message or plain object to encode
         * @param {$protobuf.Writer} [writer] Writer to encode to
         * @returns {$protobuf.Writer} Writer
         */
        TrainingInfoProto.encodeDelimited = function(message, writer) {
            return this.encode(message, (writer || $Writer.create()).fork()).ldelim();
        };

        /**
         * Decodes a TrainingInfoProto message from the specified reader or buffer.
         * @function decode
         * @memberof onnx.TrainingInfoProto
         * @static
         * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
         * @param {number} [length] Message length if known beforehand
         * @returns {onnx.TrainingInfoProto & onnx.TrainingInfoProto.$Shape} TrainingInfoProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        TrainingInfoProto.decode = function (reader, length, _end, _depth, _target) {
            if (!(reader instanceof $Reader))
                reader = $Reader.create(reader);
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $Reader.recursionLimit)
                throw $Error("max depth exceeded");
            let end = length === $undefined ? reader.len : reader.pos + length, message = _target || new $root.onnx.TrainingInfoProto();
            while (reader.pos < end) {
                let start = reader.pos;
                let tag = reader.tag();
                if (tag === _end) {
                    _end = $undefined;
                    break;
                }
                let wireType = tag & 7;
                switch (tag >>>= 3) {
                case 1: {
                        if (wireType !== 2)
                            break;
                        message.initialization = $root.onnx.GraphProto.decode(reader, reader.uint32(), $undefined, _depth + 1, message.initialization);
                        continue;
                    }
                case 2: {
                        if (wireType !== 2)
                            break;
                        message.algorithm = $root.onnx.GraphProto.decode(reader, reader.uint32(), $undefined, _depth + 1, message.algorithm);
                        continue;
                    }
                case 3: {
                        if (wireType !== 2)
                            break;
                        if (!(message.initializationBinding && message.initializationBinding.length))
                            message.initializationBinding = [];
                        message.initializationBinding.push($root.onnx.StringStringEntryProto.decode(reader, reader.uint32(), $undefined, _depth + 1));
                        continue;
                    }
                case 4: {
                        if (wireType !== 2)
                            break;
                        if (!(message.updateBinding && message.updateBinding.length))
                            message.updateBinding = [];
                        message.updateBinding.push($root.onnx.StringStringEntryProto.decode(reader, reader.uint32(), $undefined, _depth + 1));
                        continue;
                    }
                }
                reader.skipType(wireType, _depth, tag);
                if (!reader.discardUnknown) {
                    $util.makeProp(message, "$unknowns", false);
                    (message.$unknowns || (message.$unknowns = [])).push(reader.raw(start, reader.pos));
                }
            }
            if (_end !== $undefined)
                throw $Error("missing end group");
            return message;
        };

        /**
         * Decodes a TrainingInfoProto message from the specified reader or buffer, length delimited.
         * @function decodeDelimited
         * @memberof onnx.TrainingInfoProto
         * @static
         * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
         * @returns {onnx.TrainingInfoProto & onnx.TrainingInfoProto.$Shape} TrainingInfoProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        TrainingInfoProto.decodeDelimited = function(reader) {
            if (!(reader instanceof $Reader))
                reader = new $Reader(reader);
            return this.decode(reader, reader.uint32());
        };

        /**
         * Verifies a TrainingInfoProto message.
         * @function verify
         * @memberof onnx.TrainingInfoProto
         * @static
         * @param {Object.<string,*>} message Plain object to verify
         * @returns {string|null} `null` if valid, otherwise the reason why it is not
         */
        TrainingInfoProto.verify = function (message, _depth) {
            if (typeof message !== "object" || message === null)
                return "object expected";
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                return "max depth exceeded";
            if (message.initialization != null && $Object.hasOwnProperty.call(message, "initialization")) {
                let error = $root.onnx.GraphProto.verify(message.initialization, _depth + 1);
                if (error)
                    return "initialization." + error;
            }
            if (message.algorithm != null && $Object.hasOwnProperty.call(message, "algorithm")) {
                let error = $root.onnx.GraphProto.verify(message.algorithm, _depth + 1);
                if (error)
                    return "algorithm." + error;
            }
            if (message.initializationBinding != null && $Object.hasOwnProperty.call(message, "initializationBinding")) {
                if (!$Array.isArray(message.initializationBinding))
                    return "initializationBinding: array expected";
                for (let i = 0; i < message.initializationBinding.length; ++i) {
                    let error = $root.onnx.StringStringEntryProto.verify(message.initializationBinding[i], _depth + 1);
                    if (error)
                        return "initializationBinding." + error;
                }
            }
            if (message.updateBinding != null && $Object.hasOwnProperty.call(message, "updateBinding")) {
                if (!$Array.isArray(message.updateBinding))
                    return "updateBinding: array expected";
                for (let i = 0; i < message.updateBinding.length; ++i) {
                    let error = $root.onnx.StringStringEntryProto.verify(message.updateBinding[i], _depth + 1);
                    if (error)
                        return "updateBinding." + error;
                }
            }
            return null;
        };

        /**
         * Creates a TrainingInfoProto message from a plain object. Also converts values to their respective internal types.
         * @function fromObject
         * @memberof onnx.TrainingInfoProto
         * @static
         * @param {Object.<string,*>} object Plain object
         * @returns {onnx.TrainingInfoProto} TrainingInfoProto
         */
        TrainingInfoProto.fromObject = function (object, _depth) {
            if (object instanceof $root.onnx.TrainingInfoProto)
                return object;
            if (!$util.isObject(object))
                throw $TypeError(".onnx.TrainingInfoProto: object expected");
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                throw $Error("max depth exceeded");
            let message = new $root.onnx.TrainingInfoProto();
            if (object.initialization != null) {
                if (!$util.isObject(object.initialization))
                    throw $TypeError(".onnx.TrainingInfoProto.initialization: object expected");
                message.initialization = $root.onnx.GraphProto.fromObject(object.initialization, _depth + 1);
            }
            if (object.algorithm != null) {
                if (!$util.isObject(object.algorithm))
                    throw $TypeError(".onnx.TrainingInfoProto.algorithm: object expected");
                message.algorithm = $root.onnx.GraphProto.fromObject(object.algorithm, _depth + 1);
            }
            if (object.initializationBinding) {
                if (!$Array.isArray(object.initializationBinding))
                    throw $TypeError(".onnx.TrainingInfoProto.initializationBinding: array expected");
                message.initializationBinding = $Array(object.initializationBinding.length);
                for (let i = 0; i < object.initializationBinding.length; ++i) {
                    if (!$util.isObject(object.initializationBinding[i]))
                        throw $TypeError(".onnx.TrainingInfoProto.initializationBinding: object expected");
                    message.initializationBinding[i] = $root.onnx.StringStringEntryProto.fromObject(object.initializationBinding[i], _depth + 1);
                }
            }
            if (object.updateBinding) {
                if (!$Array.isArray(object.updateBinding))
                    throw $TypeError(".onnx.TrainingInfoProto.updateBinding: array expected");
                message.updateBinding = $Array(object.updateBinding.length);
                for (let i = 0; i < object.updateBinding.length; ++i) {
                    if (!$util.isObject(object.updateBinding[i]))
                        throw $TypeError(".onnx.TrainingInfoProto.updateBinding: object expected");
                    message.updateBinding[i] = $root.onnx.StringStringEntryProto.fromObject(object.updateBinding[i], _depth + 1);
                }
            }
            return message;
        };

        /**
         * Creates a plain object from a TrainingInfoProto message. Also converts values to other types if specified.
         * @function toObject
         * @memberof onnx.TrainingInfoProto
         * @static
         * @param {onnx.TrainingInfoProto} message TrainingInfoProto
         * @param {$protobuf.IConversionOptions} [options] Conversion options
         * @returns {Object.<string,*>} Plain object
         */
        TrainingInfoProto.toObject = function (message, options, _depth) {
            if (!options)
                options = {};
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                throw $Error("max depth exceeded");
            let object = {};
            if (options.arrays || options.defaults) {
                object.initializationBinding = [];
                object.updateBinding = [];
            }
            if (options.defaults) {
                object.initialization = null;
                object.algorithm = null;
            }
            if (message.initialization != null && $Object.hasOwnProperty.call(message, "initialization"))
                object.initialization = $root.onnx.GraphProto.toObject(message.initialization, options, _depth + 1);
            if (message.algorithm != null && $Object.hasOwnProperty.call(message, "algorithm"))
                object.algorithm = $root.onnx.GraphProto.toObject(message.algorithm, options, _depth + 1);
            if (message.initializationBinding && message.initializationBinding.length) {
                object.initializationBinding = $Array(message.initializationBinding.length);
                for (let j = 0; j < message.initializationBinding.length; ++j)
                    object.initializationBinding[j] = $root.onnx.StringStringEntryProto.toObject(message.initializationBinding[j], options, _depth + 1);
            }
            if (message.updateBinding && message.updateBinding.length) {
                object.updateBinding = $Array(message.updateBinding.length);
                for (let j = 0; j < message.updateBinding.length; ++j)
                    object.updateBinding[j] = $root.onnx.StringStringEntryProto.toObject(message.updateBinding[j], options, _depth + 1);
            }
            return object;
        };

        /**
         * Converts this TrainingInfoProto to JSON.
         * @function toJSON
         * @memberof onnx.TrainingInfoProto
         * @instance
         * @returns {Object.<string,*>} JSON object
         */
        TrainingInfoProto.prototype.toJSON = function() {
            return TrainingInfoProto.toObject(this, $protobuf.util.toJSONOptions);
        };

        /**
         * Gets the type url for TrainingInfoProto
         * @function getTypeUrl
         * @memberof onnx.TrainingInfoProto
         * @static
         * @param {string} [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
         * @returns {string} The type url
         */
        TrainingInfoProto.getTypeUrl = function(prefix) {
            if (prefix === $undefined)
                prefix = "type.googleapis.com";
            return prefix + "/onnx.TrainingInfoProto";
        };

        return TrainingInfoProto;
    })();

    onnx.ModelProto = (function() {

        /**
         * Properties of a ModelProto.
         * @typedef {Object} onnx.ModelProto.$Properties
         * @property {number|Long|null} [irVersion] ModelProto irVersion
         * @property {Array.<onnx.OperatorSetIdProto.$Properties>|null} [opsetImport] ModelProto opsetImport
         * @property {string|null} [producerName] ModelProto producerName
         * @property {string|null} [producerVersion] ModelProto producerVersion
         * @property {string|null} [domain] ModelProto domain
         * @property {number|Long|null} [modelVersion] ModelProto modelVersion
         * @property {string|null} [docString] ModelProto docString
         * @property {onnx.GraphProto.$Properties|null} [graph] ModelProto graph
         * @property {Array.<onnx.StringStringEntryProto.$Properties>|null} [metadataProps] ModelProto metadataProps
         * @property {Array.<onnx.TrainingInfoProto.$Properties>|null} [trainingInfo] ModelProto trainingInfo
         * @property {Array.<onnx.FunctionProto.$Properties>|null} [functions] ModelProto functions
         * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding when enabled
         */

        /**
         * Properties of a ModelProto.
         * @memberof onnx
         * @interface IModelProto
         * @augments onnx.ModelProto.$Properties
         * @deprecated Use onnx.ModelProto.$Properties instead.
         */

        /**
         * Shape of a ModelProto.
         * @typedef {{
         *   irVersion?: number|Long|null;
         *   opsetImport?: Array.<onnx.OperatorSetIdProto.$Shape>|null;
         *   producerName?: string|null;
         *   producerVersion?: string|null;
         *   domain?: string|null;
         *   modelVersion?: number|Long|null;
         *   docString?: string|null;
         *   graph?: onnx.GraphProto.$Shape|null;
         *   metadataProps?: Array.<onnx.StringStringEntryProto.$Shape>|null;
         *   trainingInfo?: Array.<onnx.TrainingInfoProto.$Shape>|null;
         *   functions?: Array.<onnx.FunctionProto.$Shape>|null;
         *   $unknowns?: Array.<Uint8Array>;
         * }} onnx.ModelProto.$Shape
         */

        /**
         * Constructs a new ModelProto.
         * @memberof onnx
         * @classdesc Represents a ModelProto.
         * @constructor
         * @param {onnx.ModelProto.$Properties=} [properties] Properties to set
         * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding when enabled
         */
        const ModelProto = function (properties) {
            this.opsetImport = [];
            this.metadataProps = [];
            this.trainingInfo = [];
            this.functions = [];
            if (properties)
                for (let keys = $Object.keys(properties), i = 0; i < keys.length; ++i)
                    if (properties[keys[i]] != null && keys[i] !== "__proto__")
                        this[keys[i]] = properties[keys[i]];
        };

        /**
         * ModelProto irVersion.
         * @member {number|Long} irVersion
         * @memberof onnx.ModelProto
         * @instance
         */
        ModelProto.prototype.irVersion = $util.Long ? $util.Long.fromBits(0,0,false) : 0;

        /**
         * ModelProto opsetImport.
         * @member {Array.<onnx.OperatorSetIdProto.$Properties>} opsetImport
         * @memberof onnx.ModelProto
         * @instance
         */
        ModelProto.prototype.opsetImport = $util.emptyArray;

        /**
         * ModelProto producerName.
         * @member {string} producerName
         * @memberof onnx.ModelProto
         * @instance
         */
        ModelProto.prototype.producerName = "";

        /**
         * ModelProto producerVersion.
         * @member {string} producerVersion
         * @memberof onnx.ModelProto
         * @instance
         */
        ModelProto.prototype.producerVersion = "";

        /**
         * ModelProto domain.
         * @member {string} domain
         * @memberof onnx.ModelProto
         * @instance
         */
        ModelProto.prototype.domain = "";

        /**
         * ModelProto modelVersion.
         * @member {number|Long} modelVersion
         * @memberof onnx.ModelProto
         * @instance
         */
        ModelProto.prototype.modelVersion = $util.Long ? $util.Long.fromBits(0,0,false) : 0;

        /**
         * ModelProto docString.
         * @member {string} docString
         * @memberof onnx.ModelProto
         * @instance
         */
        ModelProto.prototype.docString = "";

        /**
         * ModelProto graph.
         * @member {onnx.GraphProto.$Properties|null|undefined} graph
         * @memberof onnx.ModelProto
         * @instance
         */
        ModelProto.prototype.graph = null;

        /**
         * ModelProto metadataProps.
         * @member {Array.<onnx.StringStringEntryProto.$Properties>} metadataProps
         * @memberof onnx.ModelProto
         * @instance
         */
        ModelProto.prototype.metadataProps = $util.emptyArray;

        /**
         * ModelProto trainingInfo.
         * @member {Array.<onnx.TrainingInfoProto.$Properties>} trainingInfo
         * @memberof onnx.ModelProto
         * @instance
         */
        ModelProto.prototype.trainingInfo = $util.emptyArray;

        /**
         * ModelProto functions.
         * @member {Array.<onnx.FunctionProto.$Properties>} functions
         * @memberof onnx.ModelProto
         * @instance
         */
        ModelProto.prototype.functions = $util.emptyArray;

        /**
         * Creates a new ModelProto instance using the specified properties.
         * @function create
         * @memberof onnx.ModelProto
         * @static
         * @param {onnx.ModelProto.$Properties=} [properties] Properties to set
         * @returns {onnx.ModelProto} ModelProto instance
         * @type {{
         *   (properties: onnx.ModelProto.$Shape): onnx.ModelProto & onnx.ModelProto.$Shape;
         *   (properties?: onnx.ModelProto.$Properties): onnx.ModelProto;
         * }}
         */
        ModelProto.create = function(properties) {
            return new ModelProto(properties);
        };

        /**
         * Encodes the specified ModelProto message. Does not implicitly {@link onnx.ModelProto.verify|verify} messages.
         * @function encode
         * @memberof onnx.ModelProto
         * @static
         * @param {onnx.ModelProto.$Properties} message ModelProto message or plain object to encode
         * @param {$protobuf.Writer} [writer] Writer to encode to
         * @returns {$protobuf.Writer} Writer
         */
        ModelProto.encode = function (message, writer, _depth) {
            if (!writer)
                writer = $Writer.create();
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                throw $Error("max depth exceeded");
            if (message.irVersion != null && $Object.hasOwnProperty.call(message, "irVersion"))
                writer.uint32(/* id 1, wireType 0 =*/8).int64(message.irVersion);
            if (message.producerName != null && $Object.hasOwnProperty.call(message, "producerName"))
                writer.uint32(/* id 2, wireType 2 =*/18).string(message.producerName);
            if (message.producerVersion != null && $Object.hasOwnProperty.call(message, "producerVersion"))
                writer.uint32(/* id 3, wireType 2 =*/26).string(message.producerVersion);
            if (message.domain != null && $Object.hasOwnProperty.call(message, "domain"))
                writer.uint32(/* id 4, wireType 2 =*/34).string(message.domain);
            if (message.modelVersion != null && $Object.hasOwnProperty.call(message, "modelVersion"))
                writer.uint32(/* id 5, wireType 0 =*/40).int64(message.modelVersion);
            if (message.docString != null && $Object.hasOwnProperty.call(message, "docString"))
                writer.uint32(/* id 6, wireType 2 =*/50).string(message.docString);
            if (message.graph != null && $Object.hasOwnProperty.call(message, "graph"))
                $root.onnx.GraphProto.encode(message.graph, writer.uint32(/* id 7, wireType 2 =*/58).fork(), _depth + 1).ldelim();
            if (message.opsetImport != null && message.opsetImport.length)
                for (let i = 0; i < message.opsetImport.length; ++i)
                    $root.onnx.OperatorSetIdProto.encode(message.opsetImport[i], writer.uint32(/* id 8, wireType 2 =*/66).fork(), _depth + 1).ldelim();
            if (message.metadataProps != null && message.metadataProps.length)
                for (let i = 0; i < message.metadataProps.length; ++i)
                    $root.onnx.StringStringEntryProto.encode(message.metadataProps[i], writer.uint32(/* id 14, wireType 2 =*/114).fork(), _depth + 1).ldelim();
            if (message.trainingInfo != null && message.trainingInfo.length)
                for (let i = 0; i < message.trainingInfo.length; ++i)
                    $root.onnx.TrainingInfoProto.encode(message.trainingInfo[i], writer.uint32(/* id 20, wireType 2 =*/162).fork(), _depth + 1).ldelim();
            if (message.functions != null && message.functions.length)
                for (let i = 0; i < message.functions.length; ++i)
                    $root.onnx.FunctionProto.encode(message.functions[i], writer.uint32(/* id 25, wireType 2 =*/202).fork(), _depth + 1).ldelim();
            if (message.$unknowns != null && $Object.hasOwnProperty.call(message, "$unknowns"))
                for (let i = 0; i < message.$unknowns.length; ++i)
                    writer.raw(message.$unknowns[i]);
            return writer;
        };

        /**
         * Encodes the specified ModelProto message, length delimited. Does not implicitly {@link onnx.ModelProto.verify|verify} messages.
         * @function encodeDelimited
         * @memberof onnx.ModelProto
         * @static
         * @param {onnx.ModelProto.$Properties} message ModelProto message or plain object to encode
         * @param {$protobuf.Writer} [writer] Writer to encode to
         * @returns {$protobuf.Writer} Writer
         */
        ModelProto.encodeDelimited = function(message, writer) {
            return this.encode(message, (writer || $Writer.create()).fork()).ldelim();
        };

        /**
         * Decodes a ModelProto message from the specified reader or buffer.
         * @function decode
         * @memberof onnx.ModelProto
         * @static
         * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
         * @param {number} [length] Message length if known beforehand
         * @returns {onnx.ModelProto & onnx.ModelProto.$Shape} ModelProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        ModelProto.decode = function (reader, length, _end, _depth, _target) {
            if (!(reader instanceof $Reader))
                reader = $Reader.create(reader);
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $Reader.recursionLimit)
                throw $Error("max depth exceeded");
            let end = length === $undefined ? reader.len : reader.pos + length, message = _target || new $root.onnx.ModelProto();
            while (reader.pos < end) {
                let start = reader.pos;
                let tag = reader.tag();
                if (tag === _end) {
                    _end = $undefined;
                    break;
                }
                let wireType = tag & 7;
                switch (tag >>>= 3) {
                case 1: {
                        if (wireType !== 0)
                            break;
                        message.irVersion = reader.int64();
                        continue;
                    }
                case 8: {
                        if (wireType !== 2)
                            break;
                        if (!(message.opsetImport && message.opsetImport.length))
                            message.opsetImport = [];
                        message.opsetImport.push($root.onnx.OperatorSetIdProto.decode(reader, reader.uint32(), $undefined, _depth + 1));
                        continue;
                    }
                case 2: {
                        if (wireType !== 2)
                            break;
                        message.producerName = reader.string();
                        continue;
                    }
                case 3: {
                        if (wireType !== 2)
                            break;
                        message.producerVersion = reader.string();
                        continue;
                    }
                case 4: {
                        if (wireType !== 2)
                            break;
                        message.domain = reader.string();
                        continue;
                    }
                case 5: {
                        if (wireType !== 0)
                            break;
                        message.modelVersion = reader.int64();
                        continue;
                    }
                case 6: {
                        if (wireType !== 2)
                            break;
                        message.docString = reader.string();
                        continue;
                    }
                case 7: {
                        if (wireType !== 2)
                            break;
                        message.graph = $root.onnx.GraphProto.decode(reader, reader.uint32(), $undefined, _depth + 1, message.graph);
                        continue;
                    }
                case 14: {
                        if (wireType !== 2)
                            break;
                        if (!(message.metadataProps && message.metadataProps.length))
                            message.metadataProps = [];
                        message.metadataProps.push($root.onnx.StringStringEntryProto.decode(reader, reader.uint32(), $undefined, _depth + 1));
                        continue;
                    }
                case 20: {
                        if (wireType !== 2)
                            break;
                        if (!(message.trainingInfo && message.trainingInfo.length))
                            message.trainingInfo = [];
                        message.trainingInfo.push($root.onnx.TrainingInfoProto.decode(reader, reader.uint32(), $undefined, _depth + 1));
                        continue;
                    }
                case 25: {
                        if (wireType !== 2)
                            break;
                        if (!(message.functions && message.functions.length))
                            message.functions = [];
                        message.functions.push($root.onnx.FunctionProto.decode(reader, reader.uint32(), $undefined, _depth + 1));
                        continue;
                    }
                }
                reader.skipType(wireType, _depth, tag);
                if (!reader.discardUnknown) {
                    $util.makeProp(message, "$unknowns", false);
                    (message.$unknowns || (message.$unknowns = [])).push(reader.raw(start, reader.pos));
                }
            }
            if (_end !== $undefined)
                throw $Error("missing end group");
            return message;
        };

        /**
         * Decodes a ModelProto message from the specified reader or buffer, length delimited.
         * @function decodeDelimited
         * @memberof onnx.ModelProto
         * @static
         * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
         * @returns {onnx.ModelProto & onnx.ModelProto.$Shape} ModelProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        ModelProto.decodeDelimited = function(reader) {
            if (!(reader instanceof $Reader))
                reader = new $Reader(reader);
            return this.decode(reader, reader.uint32());
        };

        /**
         * Verifies a ModelProto message.
         * @function verify
         * @memberof onnx.ModelProto
         * @static
         * @param {Object.<string,*>} message Plain object to verify
         * @returns {string|null} `null` if valid, otherwise the reason why it is not
         */
        ModelProto.verify = function (message, _depth) {
            if (typeof message !== "object" || message === null)
                return "object expected";
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                return "max depth exceeded";
            if (message.irVersion != null && $Object.hasOwnProperty.call(message, "irVersion"))
                if (!$util.isInteger(message.irVersion) && !(message.irVersion && $util.isInteger(message.irVersion.low) && $util.isInteger(message.irVersion.high)))
                    return "irVersion: integer|Long expected";
            if (message.opsetImport != null && $Object.hasOwnProperty.call(message, "opsetImport")) {
                if (!$Array.isArray(message.opsetImport))
                    return "opsetImport: array expected";
                for (let i = 0; i < message.opsetImport.length; ++i) {
                    let error = $root.onnx.OperatorSetIdProto.verify(message.opsetImport[i], _depth + 1);
                    if (error)
                        return "opsetImport." + error;
                }
            }
            if (message.producerName != null && $Object.hasOwnProperty.call(message, "producerName"))
                if (!$util.isString(message.producerName))
                    return "producerName: string expected";
            if (message.producerVersion != null && $Object.hasOwnProperty.call(message, "producerVersion"))
                if (!$util.isString(message.producerVersion))
                    return "producerVersion: string expected";
            if (message.domain != null && $Object.hasOwnProperty.call(message, "domain"))
                if (!$util.isString(message.domain))
                    return "domain: string expected";
            if (message.modelVersion != null && $Object.hasOwnProperty.call(message, "modelVersion"))
                if (!$util.isInteger(message.modelVersion) && !(message.modelVersion && $util.isInteger(message.modelVersion.low) && $util.isInteger(message.modelVersion.high)))
                    return "modelVersion: integer|Long expected";
            if (message.docString != null && $Object.hasOwnProperty.call(message, "docString"))
                if (!$util.isString(message.docString))
                    return "docString: string expected";
            if (message.graph != null && $Object.hasOwnProperty.call(message, "graph")) {
                let error = $root.onnx.GraphProto.verify(message.graph, _depth + 1);
                if (error)
                    return "graph." + error;
            }
            if (message.metadataProps != null && $Object.hasOwnProperty.call(message, "metadataProps")) {
                if (!$Array.isArray(message.metadataProps))
                    return "metadataProps: array expected";
                for (let i = 0; i < message.metadataProps.length; ++i) {
                    let error = $root.onnx.StringStringEntryProto.verify(message.metadataProps[i], _depth + 1);
                    if (error)
                        return "metadataProps." + error;
                }
            }
            if (message.trainingInfo != null && $Object.hasOwnProperty.call(message, "trainingInfo")) {
                if (!$Array.isArray(message.trainingInfo))
                    return "trainingInfo: array expected";
                for (let i = 0; i < message.trainingInfo.length; ++i) {
                    let error = $root.onnx.TrainingInfoProto.verify(message.trainingInfo[i], _depth + 1);
                    if (error)
                        return "trainingInfo." + error;
                }
            }
            if (message.functions != null && $Object.hasOwnProperty.call(message, "functions")) {
                if (!$Array.isArray(message.functions))
                    return "functions: array expected";
                for (let i = 0; i < message.functions.length; ++i) {
                    let error = $root.onnx.FunctionProto.verify(message.functions[i], _depth + 1);
                    if (error)
                        return "functions." + error;
                }
            }
            return null;
        };

        /**
         * Creates a ModelProto message from a plain object. Also converts values to their respective internal types.
         * @function fromObject
         * @memberof onnx.ModelProto
         * @static
         * @param {Object.<string,*>} object Plain object
         * @returns {onnx.ModelProto} ModelProto
         */
        ModelProto.fromObject = function (object, _depth) {
            if (object instanceof $root.onnx.ModelProto)
                return object;
            if (!$util.isObject(object))
                throw $TypeError(".onnx.ModelProto: object expected");
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                throw $Error("max depth exceeded");
            let message = new $root.onnx.ModelProto();
            if (object.irVersion != null)
                if ($util.Long)
                    message.irVersion = $util.Long.fromValue(object.irVersion, false);
                else if (typeof object.irVersion === "string")
                    message.irVersion = $parseInt(object.irVersion, 10);
                else if (typeof object.irVersion === "number")
                    message.irVersion = object.irVersion;
                else if (typeof object.irVersion === "object")
                    message.irVersion = new $util.LongBits(object.irVersion.low >>> 0, object.irVersion.high >>> 0).toNumber();
            if (object.opsetImport) {
                if (!$Array.isArray(object.opsetImport))
                    throw $TypeError(".onnx.ModelProto.opsetImport: array expected");
                message.opsetImport = $Array(object.opsetImport.length);
                for (let i = 0; i < object.opsetImport.length; ++i) {
                    if (!$util.isObject(object.opsetImport[i]))
                        throw $TypeError(".onnx.ModelProto.opsetImport: object expected");
                    message.opsetImport[i] = $root.onnx.OperatorSetIdProto.fromObject(object.opsetImport[i], _depth + 1);
                }
            }
            if (object.producerName != null)
                message.producerName = $String(object.producerName);
            if (object.producerVersion != null)
                message.producerVersion = $String(object.producerVersion);
            if (object.domain != null)
                message.domain = $String(object.domain);
            if (object.modelVersion != null)
                if ($util.Long)
                    message.modelVersion = $util.Long.fromValue(object.modelVersion, false);
                else if (typeof object.modelVersion === "string")
                    message.modelVersion = $parseInt(object.modelVersion, 10);
                else if (typeof object.modelVersion === "number")
                    message.modelVersion = object.modelVersion;
                else if (typeof object.modelVersion === "object")
                    message.modelVersion = new $util.LongBits(object.modelVersion.low >>> 0, object.modelVersion.high >>> 0).toNumber();
            if (object.docString != null)
                message.docString = $String(object.docString);
            if (object.graph != null) {
                if (!$util.isObject(object.graph))
                    throw $TypeError(".onnx.ModelProto.graph: object expected");
                message.graph = $root.onnx.GraphProto.fromObject(object.graph, _depth + 1);
            }
            if (object.metadataProps) {
                if (!$Array.isArray(object.metadataProps))
                    throw $TypeError(".onnx.ModelProto.metadataProps: array expected");
                message.metadataProps = $Array(object.metadataProps.length);
                for (let i = 0; i < object.metadataProps.length; ++i) {
                    if (!$util.isObject(object.metadataProps[i]))
                        throw $TypeError(".onnx.ModelProto.metadataProps: object expected");
                    message.metadataProps[i] = $root.onnx.StringStringEntryProto.fromObject(object.metadataProps[i], _depth + 1);
                }
            }
            if (object.trainingInfo) {
                if (!$Array.isArray(object.trainingInfo))
                    throw $TypeError(".onnx.ModelProto.trainingInfo: array expected");
                message.trainingInfo = $Array(object.trainingInfo.length);
                for (let i = 0; i < object.trainingInfo.length; ++i) {
                    if (!$util.isObject(object.trainingInfo[i]))
                        throw $TypeError(".onnx.ModelProto.trainingInfo: object expected");
                    message.trainingInfo[i] = $root.onnx.TrainingInfoProto.fromObject(object.trainingInfo[i], _depth + 1);
                }
            }
            if (object.functions) {
                if (!$Array.isArray(object.functions))
                    throw $TypeError(".onnx.ModelProto.functions: array expected");
                message.functions = $Array(object.functions.length);
                for (let i = 0; i < object.functions.length; ++i) {
                    if (!$util.isObject(object.functions[i]))
                        throw $TypeError(".onnx.ModelProto.functions: object expected");
                    message.functions[i] = $root.onnx.FunctionProto.fromObject(object.functions[i], _depth + 1);
                }
            }
            return message;
        };

        /**
         * Creates a plain object from a ModelProto message. Also converts values to other types if specified.
         * @function toObject
         * @memberof onnx.ModelProto
         * @static
         * @param {onnx.ModelProto} message ModelProto
         * @param {$protobuf.IConversionOptions} [options] Conversion options
         * @returns {Object.<string,*>} Plain object
         */
        ModelProto.toObject = function (message, options, _depth) {
            if (!options)
                options = {};
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                throw $Error("max depth exceeded");
            let object = {};
            if (options.arrays || options.defaults) {
                object.opsetImport = [];
                object.metadataProps = [];
                object.trainingInfo = [];
                object.functions = [];
            }
            if (options.defaults) {
                if ($util.Long) {
                    let long = new $util.Long(0, 0, false);
                    object.irVersion = options.longs === $String ? long.toString() : options.longs === $Number ? long.toNumber() : typeof $BigInt !== "undefined" && options.longs === $BigInt ? long.toBigInt() : long;
                } else
                    object.irVersion = options.longs === $String ? "0" : typeof $BigInt !== "undefined" && options.longs === $BigInt ? $BigInt("0") : 0;
                object.producerName = "";
                object.producerVersion = "";
                object.domain = "";
                if ($util.Long) {
                    let long = new $util.Long(0, 0, false);
                    object.modelVersion = options.longs === $String ? long.toString() : options.longs === $Number ? long.toNumber() : typeof $BigInt !== "undefined" && options.longs === $BigInt ? long.toBigInt() : long;
                } else
                    object.modelVersion = options.longs === $String ? "0" : typeof $BigInt !== "undefined" && options.longs === $BigInt ? $BigInt("0") : 0;
                object.docString = "";
                object.graph = null;
            }
            if (message.irVersion != null && $Object.hasOwnProperty.call(message, "irVersion"))
                if (typeof $BigInt !== "undefined" && options.longs === $BigInt)
                    object.irVersion = typeof message.irVersion === "number" ? $BigInt(message.irVersion) : $util.Long.fromBits(message.irVersion.low >>> 0, message.irVersion.high >>> 0, false).toBigInt();
                else if (typeof message.irVersion === "number")
                    object.irVersion = options.longs === $String ? $String(message.irVersion) : message.irVersion;
                else
                    object.irVersion = options.longs === $String ? $util.Long.prototype.toString.call(message.irVersion) : options.longs === $Number ? new $util.LongBits(message.irVersion.low >>> 0, message.irVersion.high >>> 0).toNumber() : message.irVersion;
            if (message.producerName != null && $Object.hasOwnProperty.call(message, "producerName"))
                object.producerName = message.producerName;
            if (message.producerVersion != null && $Object.hasOwnProperty.call(message, "producerVersion"))
                object.producerVersion = message.producerVersion;
            if (message.domain != null && $Object.hasOwnProperty.call(message, "domain"))
                object.domain = message.domain;
            if (message.modelVersion != null && $Object.hasOwnProperty.call(message, "modelVersion"))
                if (typeof $BigInt !== "undefined" && options.longs === $BigInt)
                    object.modelVersion = typeof message.modelVersion === "number" ? $BigInt(message.modelVersion) : $util.Long.fromBits(message.modelVersion.low >>> 0, message.modelVersion.high >>> 0, false).toBigInt();
                else if (typeof message.modelVersion === "number")
                    object.modelVersion = options.longs === $String ? $String(message.modelVersion) : message.modelVersion;
                else
                    object.modelVersion = options.longs === $String ? $util.Long.prototype.toString.call(message.modelVersion) : options.longs === $Number ? new $util.LongBits(message.modelVersion.low >>> 0, message.modelVersion.high >>> 0).toNumber() : message.modelVersion;
            if (message.docString != null && $Object.hasOwnProperty.call(message, "docString"))
                object.docString = message.docString;
            if (message.graph != null && $Object.hasOwnProperty.call(message, "graph"))
                object.graph = $root.onnx.GraphProto.toObject(message.graph, options, _depth + 1);
            if (message.opsetImport && message.opsetImport.length) {
                object.opsetImport = $Array(message.opsetImport.length);
                for (let j = 0; j < message.opsetImport.length; ++j)
                    object.opsetImport[j] = $root.onnx.OperatorSetIdProto.toObject(message.opsetImport[j], options, _depth + 1);
            }
            if (message.metadataProps && message.metadataProps.length) {
                object.metadataProps = $Array(message.metadataProps.length);
                for (let j = 0; j < message.metadataProps.length; ++j)
                    object.metadataProps[j] = $root.onnx.StringStringEntryProto.toObject(message.metadataProps[j], options, _depth + 1);
            }
            if (message.trainingInfo && message.trainingInfo.length) {
                object.trainingInfo = $Array(message.trainingInfo.length);
                for (let j = 0; j < message.trainingInfo.length; ++j)
                    object.trainingInfo[j] = $root.onnx.TrainingInfoProto.toObject(message.trainingInfo[j], options, _depth + 1);
            }
            if (message.functions && message.functions.length) {
                object.functions = $Array(message.functions.length);
                for (let j = 0; j < message.functions.length; ++j)
                    object.functions[j] = $root.onnx.FunctionProto.toObject(message.functions[j], options, _depth + 1);
            }
            return object;
        };

        /**
         * Converts this ModelProto to JSON.
         * @function toJSON
         * @memberof onnx.ModelProto
         * @instance
         * @returns {Object.<string,*>} JSON object
         */
        ModelProto.prototype.toJSON = function() {
            return ModelProto.toObject(this, $protobuf.util.toJSONOptions);
        };

        /**
         * Gets the type url for ModelProto
         * @function getTypeUrl
         * @memberof onnx.ModelProto
         * @static
         * @param {string} [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
         * @returns {string} The type url
         */
        ModelProto.getTypeUrl = function(prefix) {
            if (prefix === $undefined)
                prefix = "type.googleapis.com";
            return prefix + "/onnx.ModelProto";
        };

        return ModelProto;
    })();

    onnx.StringStringEntryProto = (function() {

        /**
         * Properties of a StringStringEntryProto.
         * @typedef {Object} onnx.StringStringEntryProto.$Properties
         * @property {string|null} [key] StringStringEntryProto key
         * @property {string|null} [value] StringStringEntryProto value
         * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding when enabled
         */

        /**
         * Properties of a StringStringEntryProto.
         * @memberof onnx
         * @interface IStringStringEntryProto
         * @augments onnx.StringStringEntryProto.$Properties
         * @deprecated Use onnx.StringStringEntryProto.$Properties instead.
         */

        /**
         * Shape of a StringStringEntryProto.
         * @typedef {onnx.StringStringEntryProto.$Properties} onnx.StringStringEntryProto.$Shape
         */

        /**
         * Constructs a new StringStringEntryProto.
         * @memberof onnx
         * @classdesc Represents a StringStringEntryProto.
         * @constructor
         * @param {onnx.StringStringEntryProto.$Properties=} [properties] Properties to set
         * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding when enabled
         */
        const StringStringEntryProto = function (properties) {
            if (properties)
                for (let keys = $Object.keys(properties), i = 0; i < keys.length; ++i)
                    if (properties[keys[i]] != null && keys[i] !== "__proto__")
                        this[keys[i]] = properties[keys[i]];
        };

        /**
         * StringStringEntryProto key.
         * @member {string} key
         * @memberof onnx.StringStringEntryProto
         * @instance
         */
        StringStringEntryProto.prototype.key = "";

        /**
         * StringStringEntryProto value.
         * @member {string} value
         * @memberof onnx.StringStringEntryProto
         * @instance
         */
        StringStringEntryProto.prototype.value = "";

        /**
         * Creates a new StringStringEntryProto instance using the specified properties.
         * @function create
         * @memberof onnx.StringStringEntryProto
         * @static
         * @param {onnx.StringStringEntryProto.$Properties=} [properties] Properties to set
         * @returns {onnx.StringStringEntryProto} StringStringEntryProto instance
         * @type {{
         *   (properties: onnx.StringStringEntryProto.$Shape): onnx.StringStringEntryProto & onnx.StringStringEntryProto.$Shape;
         *   (properties?: onnx.StringStringEntryProto.$Properties): onnx.StringStringEntryProto;
         * }}
         */
        StringStringEntryProto.create = function(properties) {
            return new StringStringEntryProto(properties);
        };

        /**
         * Encodes the specified StringStringEntryProto message. Does not implicitly {@link onnx.StringStringEntryProto.verify|verify} messages.
         * @function encode
         * @memberof onnx.StringStringEntryProto
         * @static
         * @param {onnx.StringStringEntryProto.$Properties} message StringStringEntryProto message or plain object to encode
         * @param {$protobuf.Writer} [writer] Writer to encode to
         * @returns {$protobuf.Writer} Writer
         */
        StringStringEntryProto.encode = function (message, writer, _depth) {
            if (!writer)
                writer = $Writer.create();
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                throw $Error("max depth exceeded");
            if (message.key != null && $Object.hasOwnProperty.call(message, "key"))
                writer.uint32(/* id 1, wireType 2 =*/10).string(message.key);
            if (message.value != null && $Object.hasOwnProperty.call(message, "value"))
                writer.uint32(/* id 2, wireType 2 =*/18).string(message.value);
            if (message.$unknowns != null && $Object.hasOwnProperty.call(message, "$unknowns"))
                for (let i = 0; i < message.$unknowns.length; ++i)
                    writer.raw(message.$unknowns[i]);
            return writer;
        };

        /**
         * Encodes the specified StringStringEntryProto message, length delimited. Does not implicitly {@link onnx.StringStringEntryProto.verify|verify} messages.
         * @function encodeDelimited
         * @memberof onnx.StringStringEntryProto
         * @static
         * @param {onnx.StringStringEntryProto.$Properties} message StringStringEntryProto message or plain object to encode
         * @param {$protobuf.Writer} [writer] Writer to encode to
         * @returns {$protobuf.Writer} Writer
         */
        StringStringEntryProto.encodeDelimited = function(message, writer) {
            return this.encode(message, (writer || $Writer.create()).fork()).ldelim();
        };

        /**
         * Decodes a StringStringEntryProto message from the specified reader or buffer.
         * @function decode
         * @memberof onnx.StringStringEntryProto
         * @static
         * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
         * @param {number} [length] Message length if known beforehand
         * @returns {onnx.StringStringEntryProto & onnx.StringStringEntryProto.$Shape} StringStringEntryProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        StringStringEntryProto.decode = function (reader, length, _end, _depth, _target) {
            if (!(reader instanceof $Reader))
                reader = $Reader.create(reader);
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $Reader.recursionLimit)
                throw $Error("max depth exceeded");
            let end = length === $undefined ? reader.len : reader.pos + length, message = _target || new $root.onnx.StringStringEntryProto();
            while (reader.pos < end) {
                let start = reader.pos;
                let tag = reader.tag();
                if (tag === _end) {
                    _end = $undefined;
                    break;
                }
                let wireType = tag & 7;
                switch (tag >>>= 3) {
                case 1: {
                        if (wireType !== 2)
                            break;
                        message.key = reader.string();
                        continue;
                    }
                case 2: {
                        if (wireType !== 2)
                            break;
                        message.value = reader.string();
                        continue;
                    }
                }
                reader.skipType(wireType, _depth, tag);
                if (!reader.discardUnknown) {
                    $util.makeProp(message, "$unknowns", false);
                    (message.$unknowns || (message.$unknowns = [])).push(reader.raw(start, reader.pos));
                }
            }
            if (_end !== $undefined)
                throw $Error("missing end group");
            return message;
        };

        /**
         * Decodes a StringStringEntryProto message from the specified reader or buffer, length delimited.
         * @function decodeDelimited
         * @memberof onnx.StringStringEntryProto
         * @static
         * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
         * @returns {onnx.StringStringEntryProto & onnx.StringStringEntryProto.$Shape} StringStringEntryProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        StringStringEntryProto.decodeDelimited = function(reader) {
            if (!(reader instanceof $Reader))
                reader = new $Reader(reader);
            return this.decode(reader, reader.uint32());
        };

        /**
         * Verifies a StringStringEntryProto message.
         * @function verify
         * @memberof onnx.StringStringEntryProto
         * @static
         * @param {Object.<string,*>} message Plain object to verify
         * @returns {string|null} `null` if valid, otherwise the reason why it is not
         */
        StringStringEntryProto.verify = function (message, _depth) {
            if (typeof message !== "object" || message === null)
                return "object expected";
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                return "max depth exceeded";
            if (message.key != null && $Object.hasOwnProperty.call(message, "key"))
                if (!$util.isString(message.key))
                    return "key: string expected";
            if (message.value != null && $Object.hasOwnProperty.call(message, "value"))
                if (!$util.isString(message.value))
                    return "value: string expected";
            return null;
        };

        /**
         * Creates a StringStringEntryProto message from a plain object. Also converts values to their respective internal types.
         * @function fromObject
         * @memberof onnx.StringStringEntryProto
         * @static
         * @param {Object.<string,*>} object Plain object
         * @returns {onnx.StringStringEntryProto} StringStringEntryProto
         */
        StringStringEntryProto.fromObject = function (object, _depth) {
            if (object instanceof $root.onnx.StringStringEntryProto)
                return object;
            if (!$util.isObject(object))
                throw $TypeError(".onnx.StringStringEntryProto: object expected");
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                throw $Error("max depth exceeded");
            let message = new $root.onnx.StringStringEntryProto();
            if (object.key != null)
                message.key = $String(object.key);
            if (object.value != null)
                message.value = $String(object.value);
            return message;
        };

        /**
         * Creates a plain object from a StringStringEntryProto message. Also converts values to other types if specified.
         * @function toObject
         * @memberof onnx.StringStringEntryProto
         * @static
         * @param {onnx.StringStringEntryProto} message StringStringEntryProto
         * @param {$protobuf.IConversionOptions} [options] Conversion options
         * @returns {Object.<string,*>} Plain object
         */
        StringStringEntryProto.toObject = function (message, options, _depth) {
            if (!options)
                options = {};
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                throw $Error("max depth exceeded");
            let object = {};
            if (options.defaults) {
                object.key = "";
                object.value = "";
            }
            if (message.key != null && $Object.hasOwnProperty.call(message, "key"))
                object.key = message.key;
            if (message.value != null && $Object.hasOwnProperty.call(message, "value"))
                object.value = message.value;
            return object;
        };

        /**
         * Converts this StringStringEntryProto to JSON.
         * @function toJSON
         * @memberof onnx.StringStringEntryProto
         * @instance
         * @returns {Object.<string,*>} JSON object
         */
        StringStringEntryProto.prototype.toJSON = function() {
            return StringStringEntryProto.toObject(this, $protobuf.util.toJSONOptions);
        };

        /**
         * Gets the type url for StringStringEntryProto
         * @function getTypeUrl
         * @memberof onnx.StringStringEntryProto
         * @static
         * @param {string} [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
         * @returns {string} The type url
         */
        StringStringEntryProto.getTypeUrl = function(prefix) {
            if (prefix === $undefined)
                prefix = "type.googleapis.com";
            return prefix + "/onnx.StringStringEntryProto";
        };

        return StringStringEntryProto;
    })();

    onnx.TensorAnnotation = (function() {

        /**
         * Properties of a TensorAnnotation.
         * @typedef {Object} onnx.TensorAnnotation.$Properties
         * @property {string|null} [tensorName] TensorAnnotation tensorName
         * @property {Array.<onnx.StringStringEntryProto.$Properties>|null} [quantParameterTensorNames] TensorAnnotation quantParameterTensorNames
         * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding when enabled
         */

        /**
         * Properties of a TensorAnnotation.
         * @memberof onnx
         * @interface ITensorAnnotation
         * @augments onnx.TensorAnnotation.$Properties
         * @deprecated Use onnx.TensorAnnotation.$Properties instead.
         */

        /**
         * Shape of a TensorAnnotation.
         * @typedef {onnx.TensorAnnotation.$Properties} onnx.TensorAnnotation.$Shape
         */

        /**
         * Constructs a new TensorAnnotation.
         * @memberof onnx
         * @classdesc Represents a TensorAnnotation.
         * @constructor
         * @param {onnx.TensorAnnotation.$Properties=} [properties] Properties to set
         * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding when enabled
         */
        const TensorAnnotation = function (properties) {
            this.quantParameterTensorNames = [];
            if (properties)
                for (let keys = $Object.keys(properties), i = 0; i < keys.length; ++i)
                    if (properties[keys[i]] != null && keys[i] !== "__proto__")
                        this[keys[i]] = properties[keys[i]];
        };

        /**
         * TensorAnnotation tensorName.
         * @member {string} tensorName
         * @memberof onnx.TensorAnnotation
         * @instance
         */
        TensorAnnotation.prototype.tensorName = "";

        /**
         * TensorAnnotation quantParameterTensorNames.
         * @member {Array.<onnx.StringStringEntryProto.$Properties>} quantParameterTensorNames
         * @memberof onnx.TensorAnnotation
         * @instance
         */
        TensorAnnotation.prototype.quantParameterTensorNames = $util.emptyArray;

        /**
         * Creates a new TensorAnnotation instance using the specified properties.
         * @function create
         * @memberof onnx.TensorAnnotation
         * @static
         * @param {onnx.TensorAnnotation.$Properties=} [properties] Properties to set
         * @returns {onnx.TensorAnnotation} TensorAnnotation instance
         * @type {{
         *   (properties: onnx.TensorAnnotation.$Shape): onnx.TensorAnnotation & onnx.TensorAnnotation.$Shape;
         *   (properties?: onnx.TensorAnnotation.$Properties): onnx.TensorAnnotation;
         * }}
         */
        TensorAnnotation.create = function(properties) {
            return new TensorAnnotation(properties);
        };

        /**
         * Encodes the specified TensorAnnotation message. Does not implicitly {@link onnx.TensorAnnotation.verify|verify} messages.
         * @function encode
         * @memberof onnx.TensorAnnotation
         * @static
         * @param {onnx.TensorAnnotation.$Properties} message TensorAnnotation message or plain object to encode
         * @param {$protobuf.Writer} [writer] Writer to encode to
         * @returns {$protobuf.Writer} Writer
         */
        TensorAnnotation.encode = function (message, writer, _depth) {
            if (!writer)
                writer = $Writer.create();
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                throw $Error("max depth exceeded");
            if (message.tensorName != null && $Object.hasOwnProperty.call(message, "tensorName"))
                writer.uint32(/* id 1, wireType 2 =*/10).string(message.tensorName);
            if (message.quantParameterTensorNames != null && message.quantParameterTensorNames.length)
                for (let i = 0; i < message.quantParameterTensorNames.length; ++i)
                    $root.onnx.StringStringEntryProto.encode(message.quantParameterTensorNames[i], writer.uint32(/* id 2, wireType 2 =*/18).fork(), _depth + 1).ldelim();
            if (message.$unknowns != null && $Object.hasOwnProperty.call(message, "$unknowns"))
                for (let i = 0; i < message.$unknowns.length; ++i)
                    writer.raw(message.$unknowns[i]);
            return writer;
        };

        /**
         * Encodes the specified TensorAnnotation message, length delimited. Does not implicitly {@link onnx.TensorAnnotation.verify|verify} messages.
         * @function encodeDelimited
         * @memberof onnx.TensorAnnotation
         * @static
         * @param {onnx.TensorAnnotation.$Properties} message TensorAnnotation message or plain object to encode
         * @param {$protobuf.Writer} [writer] Writer to encode to
         * @returns {$protobuf.Writer} Writer
         */
        TensorAnnotation.encodeDelimited = function(message, writer) {
            return this.encode(message, (writer || $Writer.create()).fork()).ldelim();
        };

        /**
         * Decodes a TensorAnnotation message from the specified reader or buffer.
         * @function decode
         * @memberof onnx.TensorAnnotation
         * @static
         * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
         * @param {number} [length] Message length if known beforehand
         * @returns {onnx.TensorAnnotation & onnx.TensorAnnotation.$Shape} TensorAnnotation
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        TensorAnnotation.decode = function (reader, length, _end, _depth, _target) {
            if (!(reader instanceof $Reader))
                reader = $Reader.create(reader);
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $Reader.recursionLimit)
                throw $Error("max depth exceeded");
            let end = length === $undefined ? reader.len : reader.pos + length, message = _target || new $root.onnx.TensorAnnotation();
            while (reader.pos < end) {
                let start = reader.pos;
                let tag = reader.tag();
                if (tag === _end) {
                    _end = $undefined;
                    break;
                }
                let wireType = tag & 7;
                switch (tag >>>= 3) {
                case 1: {
                        if (wireType !== 2)
                            break;
                        message.tensorName = reader.string();
                        continue;
                    }
                case 2: {
                        if (wireType !== 2)
                            break;
                        if (!(message.quantParameterTensorNames && message.quantParameterTensorNames.length))
                            message.quantParameterTensorNames = [];
                        message.quantParameterTensorNames.push($root.onnx.StringStringEntryProto.decode(reader, reader.uint32(), $undefined, _depth + 1));
                        continue;
                    }
                }
                reader.skipType(wireType, _depth, tag);
                if (!reader.discardUnknown) {
                    $util.makeProp(message, "$unknowns", false);
                    (message.$unknowns || (message.$unknowns = [])).push(reader.raw(start, reader.pos));
                }
            }
            if (_end !== $undefined)
                throw $Error("missing end group");
            return message;
        };

        /**
         * Decodes a TensorAnnotation message from the specified reader or buffer, length delimited.
         * @function decodeDelimited
         * @memberof onnx.TensorAnnotation
         * @static
         * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
         * @returns {onnx.TensorAnnotation & onnx.TensorAnnotation.$Shape} TensorAnnotation
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        TensorAnnotation.decodeDelimited = function(reader) {
            if (!(reader instanceof $Reader))
                reader = new $Reader(reader);
            return this.decode(reader, reader.uint32());
        };

        /**
         * Verifies a TensorAnnotation message.
         * @function verify
         * @memberof onnx.TensorAnnotation
         * @static
         * @param {Object.<string,*>} message Plain object to verify
         * @returns {string|null} `null` if valid, otherwise the reason why it is not
         */
        TensorAnnotation.verify = function (message, _depth) {
            if (typeof message !== "object" || message === null)
                return "object expected";
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                return "max depth exceeded";
            if (message.tensorName != null && $Object.hasOwnProperty.call(message, "tensorName"))
                if (!$util.isString(message.tensorName))
                    return "tensorName: string expected";
            if (message.quantParameterTensorNames != null && $Object.hasOwnProperty.call(message, "quantParameterTensorNames")) {
                if (!$Array.isArray(message.quantParameterTensorNames))
                    return "quantParameterTensorNames: array expected";
                for (let i = 0; i < message.quantParameterTensorNames.length; ++i) {
                    let error = $root.onnx.StringStringEntryProto.verify(message.quantParameterTensorNames[i], _depth + 1);
                    if (error)
                        return "quantParameterTensorNames." + error;
                }
            }
            return null;
        };

        /**
         * Creates a TensorAnnotation message from a plain object. Also converts values to their respective internal types.
         * @function fromObject
         * @memberof onnx.TensorAnnotation
         * @static
         * @param {Object.<string,*>} object Plain object
         * @returns {onnx.TensorAnnotation} TensorAnnotation
         */
        TensorAnnotation.fromObject = function (object, _depth) {
            if (object instanceof $root.onnx.TensorAnnotation)
                return object;
            if (!$util.isObject(object))
                throw $TypeError(".onnx.TensorAnnotation: object expected");
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                throw $Error("max depth exceeded");
            let message = new $root.onnx.TensorAnnotation();
            if (object.tensorName != null)
                message.tensorName = $String(object.tensorName);
            if (object.quantParameterTensorNames) {
                if (!$Array.isArray(object.quantParameterTensorNames))
                    throw $TypeError(".onnx.TensorAnnotation.quantParameterTensorNames: array expected");
                message.quantParameterTensorNames = $Array(object.quantParameterTensorNames.length);
                for (let i = 0; i < object.quantParameterTensorNames.length; ++i) {
                    if (!$util.isObject(object.quantParameterTensorNames[i]))
                        throw $TypeError(".onnx.TensorAnnotation.quantParameterTensorNames: object expected");
                    message.quantParameterTensorNames[i] = $root.onnx.StringStringEntryProto.fromObject(object.quantParameterTensorNames[i], _depth + 1);
                }
            }
            return message;
        };

        /**
         * Creates a plain object from a TensorAnnotation message. Also converts values to other types if specified.
         * @function toObject
         * @memberof onnx.TensorAnnotation
         * @static
         * @param {onnx.TensorAnnotation} message TensorAnnotation
         * @param {$protobuf.IConversionOptions} [options] Conversion options
         * @returns {Object.<string,*>} Plain object
         */
        TensorAnnotation.toObject = function (message, options, _depth) {
            if (!options)
                options = {};
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                throw $Error("max depth exceeded");
            let object = {};
            if (options.arrays || options.defaults)
                object.quantParameterTensorNames = [];
            if (options.defaults)
                object.tensorName = "";
            if (message.tensorName != null && $Object.hasOwnProperty.call(message, "tensorName"))
                object.tensorName = message.tensorName;
            if (message.quantParameterTensorNames && message.quantParameterTensorNames.length) {
                object.quantParameterTensorNames = $Array(message.quantParameterTensorNames.length);
                for (let j = 0; j < message.quantParameterTensorNames.length; ++j)
                    object.quantParameterTensorNames[j] = $root.onnx.StringStringEntryProto.toObject(message.quantParameterTensorNames[j], options, _depth + 1);
            }
            return object;
        };

        /**
         * Converts this TensorAnnotation to JSON.
         * @function toJSON
         * @memberof onnx.TensorAnnotation
         * @instance
         * @returns {Object.<string,*>} JSON object
         */
        TensorAnnotation.prototype.toJSON = function() {
            return TensorAnnotation.toObject(this, $protobuf.util.toJSONOptions);
        };

        /**
         * Gets the type url for TensorAnnotation
         * @function getTypeUrl
         * @memberof onnx.TensorAnnotation
         * @static
         * @param {string} [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
         * @returns {string} The type url
         */
        TensorAnnotation.getTypeUrl = function(prefix) {
            if (prefix === $undefined)
                prefix = "type.googleapis.com";
            return prefix + "/onnx.TensorAnnotation";
        };

        return TensorAnnotation;
    })();

    onnx.GraphProto = (function() {

        /**
         * Properties of a GraphProto.
         * @typedef {Object} onnx.GraphProto.$Properties
         * @property {Array.<onnx.NodeProto.$Properties>|null} [node] GraphProto node
         * @property {string|null} [name] GraphProto name
         * @property {Array.<onnx.TensorProto.$Properties>|null} [initializer] GraphProto initializer
         * @property {Array.<onnx.SparseTensorProto.$Properties>|null} [sparseInitializer] GraphProto sparseInitializer
         * @property {string|null} [docString] GraphProto docString
         * @property {Array.<onnx.ValueInfoProto.$Properties>|null} [input] GraphProto input
         * @property {Array.<onnx.ValueInfoProto.$Properties>|null} [output] GraphProto output
         * @property {Array.<onnx.ValueInfoProto.$Properties>|null} [valueInfo] GraphProto valueInfo
         * @property {Array.<onnx.TensorAnnotation.$Properties>|null} [quantizationAnnotation] GraphProto quantizationAnnotation
         * @property {Array.<onnx.StringStringEntryProto.$Properties>|null} [metadataProps] GraphProto metadataProps
         * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding when enabled
         */

        /**
         * Properties of a GraphProto.
         * @memberof onnx
         * @interface IGraphProto
         * @augments onnx.GraphProto.$Properties
         * @deprecated Use onnx.GraphProto.$Properties instead.
         */

        /**
         * Shape of a GraphProto.
         * @typedef {{
         *   node?: Array.<onnx.NodeProto.$Shape>|null;
         *   name?: string|null;
         *   initializer?: Array.<onnx.TensorProto.$Shape>|null;
         *   sparseInitializer?: Array.<onnx.SparseTensorProto.$Shape>|null;
         *   docString?: string|null;
         *   input?: Array.<onnx.ValueInfoProto.$Shape>|null;
         *   output?: Array.<onnx.ValueInfoProto.$Shape>|null;
         *   valueInfo?: Array.<onnx.ValueInfoProto.$Shape>|null;
         *   quantizationAnnotation?: Array.<onnx.TensorAnnotation.$Shape>|null;
         *   metadataProps?: Array.<onnx.StringStringEntryProto.$Shape>|null;
         *   $unknowns?: Array.<Uint8Array>;
         * }} onnx.GraphProto.$Shape
         */

        /**
         * Constructs a new GraphProto.
         * @memberof onnx
         * @classdesc Represents a GraphProto.
         * @constructor
         * @param {onnx.GraphProto.$Properties=} [properties] Properties to set
         * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding when enabled
         */
        const GraphProto = function (properties) {
            this.node = [];
            this.initializer = [];
            this.sparseInitializer = [];
            this.input = [];
            this.output = [];
            this.valueInfo = [];
            this.quantizationAnnotation = [];
            this.metadataProps = [];
            if (properties)
                for (let keys = $Object.keys(properties), i = 0; i < keys.length; ++i)
                    if (properties[keys[i]] != null && keys[i] !== "__proto__")
                        this[keys[i]] = properties[keys[i]];
        };

        /**
         * GraphProto node.
         * @member {Array.<onnx.NodeProto.$Properties>} node
         * @memberof onnx.GraphProto
         * @instance
         */
        GraphProto.prototype.node = $util.emptyArray;

        /**
         * GraphProto name.
         * @member {string} name
         * @memberof onnx.GraphProto
         * @instance
         */
        GraphProto.prototype.name = "";

        /**
         * GraphProto initializer.
         * @member {Array.<onnx.TensorProto.$Properties>} initializer
         * @memberof onnx.GraphProto
         * @instance
         */
        GraphProto.prototype.initializer = $util.emptyArray;

        /**
         * GraphProto sparseInitializer.
         * @member {Array.<onnx.SparseTensorProto.$Properties>} sparseInitializer
         * @memberof onnx.GraphProto
         * @instance
         */
        GraphProto.prototype.sparseInitializer = $util.emptyArray;

        /**
         * GraphProto docString.
         * @member {string} docString
         * @memberof onnx.GraphProto
         * @instance
         */
        GraphProto.prototype.docString = "";

        /**
         * GraphProto input.
         * @member {Array.<onnx.ValueInfoProto.$Properties>} input
         * @memberof onnx.GraphProto
         * @instance
         */
        GraphProto.prototype.input = $util.emptyArray;

        /**
         * GraphProto output.
         * @member {Array.<onnx.ValueInfoProto.$Properties>} output
         * @memberof onnx.GraphProto
         * @instance
         */
        GraphProto.prototype.output = $util.emptyArray;

        /**
         * GraphProto valueInfo.
         * @member {Array.<onnx.ValueInfoProto.$Properties>} valueInfo
         * @memberof onnx.GraphProto
         * @instance
         */
        GraphProto.prototype.valueInfo = $util.emptyArray;

        /**
         * GraphProto quantizationAnnotation.
         * @member {Array.<onnx.TensorAnnotation.$Properties>} quantizationAnnotation
         * @memberof onnx.GraphProto
         * @instance
         */
        GraphProto.prototype.quantizationAnnotation = $util.emptyArray;

        /**
         * GraphProto metadataProps.
         * @member {Array.<onnx.StringStringEntryProto.$Properties>} metadataProps
         * @memberof onnx.GraphProto
         * @instance
         */
        GraphProto.prototype.metadataProps = $util.emptyArray;

        /**
         * Creates a new GraphProto instance using the specified properties.
         * @function create
         * @memberof onnx.GraphProto
         * @static
         * @param {onnx.GraphProto.$Properties=} [properties] Properties to set
         * @returns {onnx.GraphProto} GraphProto instance
         * @type {{
         *   (properties: onnx.GraphProto.$Shape): onnx.GraphProto & onnx.GraphProto.$Shape;
         *   (properties?: onnx.GraphProto.$Properties): onnx.GraphProto;
         * }}
         */
        GraphProto.create = function(properties) {
            return new GraphProto(properties);
        };

        /**
         * Encodes the specified GraphProto message. Does not implicitly {@link onnx.GraphProto.verify|verify} messages.
         * @function encode
         * @memberof onnx.GraphProto
         * @static
         * @param {onnx.GraphProto.$Properties} message GraphProto message or plain object to encode
         * @param {$protobuf.Writer} [writer] Writer to encode to
         * @returns {$protobuf.Writer} Writer
         */
        GraphProto.encode = function (message, writer, _depth) {
            if (!writer)
                writer = $Writer.create();
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                throw $Error("max depth exceeded");
            if (message.node != null && message.node.length)
                for (let i = 0; i < message.node.length; ++i)
                    $root.onnx.NodeProto.encode(message.node[i], writer.uint32(/* id 1, wireType 2 =*/10).fork(), _depth + 1).ldelim();
            if (message.name != null && $Object.hasOwnProperty.call(message, "name"))
                writer.uint32(/* id 2, wireType 2 =*/18).string(message.name);
            if (message.initializer != null && message.initializer.length)
                for (let i = 0; i < message.initializer.length; ++i)
                    $root.onnx.TensorProto.encode(message.initializer[i], writer.uint32(/* id 5, wireType 2 =*/42).fork(), _depth + 1).ldelim();
            if (message.docString != null && $Object.hasOwnProperty.call(message, "docString"))
                writer.uint32(/* id 10, wireType 2 =*/82).string(message.docString);
            if (message.input != null && message.input.length)
                for (let i = 0; i < message.input.length; ++i)
                    $root.onnx.ValueInfoProto.encode(message.input[i], writer.uint32(/* id 11, wireType 2 =*/90).fork(), _depth + 1).ldelim();
            if (message.output != null && message.output.length)
                for (let i = 0; i < message.output.length; ++i)
                    $root.onnx.ValueInfoProto.encode(message.output[i], writer.uint32(/* id 12, wireType 2 =*/98).fork(), _depth + 1).ldelim();
            if (message.valueInfo != null && message.valueInfo.length)
                for (let i = 0; i < message.valueInfo.length; ++i)
                    $root.onnx.ValueInfoProto.encode(message.valueInfo[i], writer.uint32(/* id 13, wireType 2 =*/106).fork(), _depth + 1).ldelim();
            if (message.quantizationAnnotation != null && message.quantizationAnnotation.length)
                for (let i = 0; i < message.quantizationAnnotation.length; ++i)
                    $root.onnx.TensorAnnotation.encode(message.quantizationAnnotation[i], writer.uint32(/* id 14, wireType 2 =*/114).fork(), _depth + 1).ldelim();
            if (message.sparseInitializer != null && message.sparseInitializer.length)
                for (let i = 0; i < message.sparseInitializer.length; ++i)
                    $root.onnx.SparseTensorProto.encode(message.sparseInitializer[i], writer.uint32(/* id 15, wireType 2 =*/122).fork(), _depth + 1).ldelim();
            if (message.metadataProps != null && message.metadataProps.length)
                for (let i = 0; i < message.metadataProps.length; ++i)
                    $root.onnx.StringStringEntryProto.encode(message.metadataProps[i], writer.uint32(/* id 16, wireType 2 =*/130).fork(), _depth + 1).ldelim();
            if (message.$unknowns != null && $Object.hasOwnProperty.call(message, "$unknowns"))
                for (let i = 0; i < message.$unknowns.length; ++i)
                    writer.raw(message.$unknowns[i]);
            return writer;
        };

        /**
         * Encodes the specified GraphProto message, length delimited. Does not implicitly {@link onnx.GraphProto.verify|verify} messages.
         * @function encodeDelimited
         * @memberof onnx.GraphProto
         * @static
         * @param {onnx.GraphProto.$Properties} message GraphProto message or plain object to encode
         * @param {$protobuf.Writer} [writer] Writer to encode to
         * @returns {$protobuf.Writer} Writer
         */
        GraphProto.encodeDelimited = function(message, writer) {
            return this.encode(message, (writer || $Writer.create()).fork()).ldelim();
        };

        /**
         * Decodes a GraphProto message from the specified reader or buffer.
         * @function decode
         * @memberof onnx.GraphProto
         * @static
         * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
         * @param {number} [length] Message length if known beforehand
         * @returns {onnx.GraphProto & onnx.GraphProto.$Shape} GraphProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        GraphProto.decode = function (reader, length, _end, _depth, _target) {
            if (!(reader instanceof $Reader))
                reader = $Reader.create(reader);
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $Reader.recursionLimit)
                throw $Error("max depth exceeded");
            let end = length === $undefined ? reader.len : reader.pos + length, message = _target || new $root.onnx.GraphProto();
            while (reader.pos < end) {
                let start = reader.pos;
                let tag = reader.tag();
                if (tag === _end) {
                    _end = $undefined;
                    break;
                }
                let wireType = tag & 7;
                switch (tag >>>= 3) {
                case 1: {
                        if (wireType !== 2)
                            break;
                        if (!(message.node && message.node.length))
                            message.node = [];
                        message.node.push($root.onnx.NodeProto.decode(reader, reader.uint32(), $undefined, _depth + 1));
                        continue;
                    }
                case 2: {
                        if (wireType !== 2)
                            break;
                        message.name = reader.string();
                        continue;
                    }
                case 5: {
                        if (wireType !== 2)
                            break;
                        if (!(message.initializer && message.initializer.length))
                            message.initializer = [];
                        message.initializer.push($root.onnx.TensorProto.decode(reader, reader.uint32(), $undefined, _depth + 1));
                        continue;
                    }
                case 15: {
                        if (wireType !== 2)
                            break;
                        if (!(message.sparseInitializer && message.sparseInitializer.length))
                            message.sparseInitializer = [];
                        message.sparseInitializer.push($root.onnx.SparseTensorProto.decode(reader, reader.uint32(), $undefined, _depth + 1));
                        continue;
                    }
                case 10: {
                        if (wireType !== 2)
                            break;
                        message.docString = reader.string();
                        continue;
                    }
                case 11: {
                        if (wireType !== 2)
                            break;
                        if (!(message.input && message.input.length))
                            message.input = [];
                        message.input.push($root.onnx.ValueInfoProto.decode(reader, reader.uint32(), $undefined, _depth + 1));
                        continue;
                    }
                case 12: {
                        if (wireType !== 2)
                            break;
                        if (!(message.output && message.output.length))
                            message.output = [];
                        message.output.push($root.onnx.ValueInfoProto.decode(reader, reader.uint32(), $undefined, _depth + 1));
                        continue;
                    }
                case 13: {
                        if (wireType !== 2)
                            break;
                        if (!(message.valueInfo && message.valueInfo.length))
                            message.valueInfo = [];
                        message.valueInfo.push($root.onnx.ValueInfoProto.decode(reader, reader.uint32(), $undefined, _depth + 1));
                        continue;
                    }
                case 14: {
                        if (wireType !== 2)
                            break;
                        if (!(message.quantizationAnnotation && message.quantizationAnnotation.length))
                            message.quantizationAnnotation = [];
                        message.quantizationAnnotation.push($root.onnx.TensorAnnotation.decode(reader, reader.uint32(), $undefined, _depth + 1));
                        continue;
                    }
                case 16: {
                        if (wireType !== 2)
                            break;
                        if (!(message.metadataProps && message.metadataProps.length))
                            message.metadataProps = [];
                        message.metadataProps.push($root.onnx.StringStringEntryProto.decode(reader, reader.uint32(), $undefined, _depth + 1));
                        continue;
                    }
                }
                reader.skipType(wireType, _depth, tag);
                if (!reader.discardUnknown) {
                    $util.makeProp(message, "$unknowns", false);
                    (message.$unknowns || (message.$unknowns = [])).push(reader.raw(start, reader.pos));
                }
            }
            if (_end !== $undefined)
                throw $Error("missing end group");
            return message;
        };

        /**
         * Decodes a GraphProto message from the specified reader or buffer, length delimited.
         * @function decodeDelimited
         * @memberof onnx.GraphProto
         * @static
         * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
         * @returns {onnx.GraphProto & onnx.GraphProto.$Shape} GraphProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        GraphProto.decodeDelimited = function(reader) {
            if (!(reader instanceof $Reader))
                reader = new $Reader(reader);
            return this.decode(reader, reader.uint32());
        };

        /**
         * Verifies a GraphProto message.
         * @function verify
         * @memberof onnx.GraphProto
         * @static
         * @param {Object.<string,*>} message Plain object to verify
         * @returns {string|null} `null` if valid, otherwise the reason why it is not
         */
        GraphProto.verify = function (message, _depth) {
            if (typeof message !== "object" || message === null)
                return "object expected";
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                return "max depth exceeded";
            if (message.node != null && $Object.hasOwnProperty.call(message, "node")) {
                if (!$Array.isArray(message.node))
                    return "node: array expected";
                for (let i = 0; i < message.node.length; ++i) {
                    let error = $root.onnx.NodeProto.verify(message.node[i], _depth + 1);
                    if (error)
                        return "node." + error;
                }
            }
            if (message.name != null && $Object.hasOwnProperty.call(message, "name"))
                if (!$util.isString(message.name))
                    return "name: string expected";
            if (message.initializer != null && $Object.hasOwnProperty.call(message, "initializer")) {
                if (!$Array.isArray(message.initializer))
                    return "initializer: array expected";
                for (let i = 0; i < message.initializer.length; ++i) {
                    let error = $root.onnx.TensorProto.verify(message.initializer[i], _depth + 1);
                    if (error)
                        return "initializer." + error;
                }
            }
            if (message.sparseInitializer != null && $Object.hasOwnProperty.call(message, "sparseInitializer")) {
                if (!$Array.isArray(message.sparseInitializer))
                    return "sparseInitializer: array expected";
                for (let i = 0; i < message.sparseInitializer.length; ++i) {
                    let error = $root.onnx.SparseTensorProto.verify(message.sparseInitializer[i], _depth + 1);
                    if (error)
                        return "sparseInitializer." + error;
                }
            }
            if (message.docString != null && $Object.hasOwnProperty.call(message, "docString"))
                if (!$util.isString(message.docString))
                    return "docString: string expected";
            if (message.input != null && $Object.hasOwnProperty.call(message, "input")) {
                if (!$Array.isArray(message.input))
                    return "input: array expected";
                for (let i = 0; i < message.input.length; ++i) {
                    let error = $root.onnx.ValueInfoProto.verify(message.input[i], _depth + 1);
                    if (error)
                        return "input." + error;
                }
            }
            if (message.output != null && $Object.hasOwnProperty.call(message, "output")) {
                if (!$Array.isArray(message.output))
                    return "output: array expected";
                for (let i = 0; i < message.output.length; ++i) {
                    let error = $root.onnx.ValueInfoProto.verify(message.output[i], _depth + 1);
                    if (error)
                        return "output." + error;
                }
            }
            if (message.valueInfo != null && $Object.hasOwnProperty.call(message, "valueInfo")) {
                if (!$Array.isArray(message.valueInfo))
                    return "valueInfo: array expected";
                for (let i = 0; i < message.valueInfo.length; ++i) {
                    let error = $root.onnx.ValueInfoProto.verify(message.valueInfo[i], _depth + 1);
                    if (error)
                        return "valueInfo." + error;
                }
            }
            if (message.quantizationAnnotation != null && $Object.hasOwnProperty.call(message, "quantizationAnnotation")) {
                if (!$Array.isArray(message.quantizationAnnotation))
                    return "quantizationAnnotation: array expected";
                for (let i = 0; i < message.quantizationAnnotation.length; ++i) {
                    let error = $root.onnx.TensorAnnotation.verify(message.quantizationAnnotation[i], _depth + 1);
                    if (error)
                        return "quantizationAnnotation." + error;
                }
            }
            if (message.metadataProps != null && $Object.hasOwnProperty.call(message, "metadataProps")) {
                if (!$Array.isArray(message.metadataProps))
                    return "metadataProps: array expected";
                for (let i = 0; i < message.metadataProps.length; ++i) {
                    let error = $root.onnx.StringStringEntryProto.verify(message.metadataProps[i], _depth + 1);
                    if (error)
                        return "metadataProps." + error;
                }
            }
            return null;
        };

        /**
         * Creates a GraphProto message from a plain object. Also converts values to their respective internal types.
         * @function fromObject
         * @memberof onnx.GraphProto
         * @static
         * @param {Object.<string,*>} object Plain object
         * @returns {onnx.GraphProto} GraphProto
         */
        GraphProto.fromObject = function (object, _depth) {
            if (object instanceof $root.onnx.GraphProto)
                return object;
            if (!$util.isObject(object))
                throw $TypeError(".onnx.GraphProto: object expected");
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                throw $Error("max depth exceeded");
            let message = new $root.onnx.GraphProto();
            if (object.node) {
                if (!$Array.isArray(object.node))
                    throw $TypeError(".onnx.GraphProto.node: array expected");
                message.node = $Array(object.node.length);
                for (let i = 0; i < object.node.length; ++i) {
                    if (!$util.isObject(object.node[i]))
                        throw $TypeError(".onnx.GraphProto.node: object expected");
                    message.node[i] = $root.onnx.NodeProto.fromObject(object.node[i], _depth + 1);
                }
            }
            if (object.name != null)
                message.name = $String(object.name);
            if (object.initializer) {
                if (!$Array.isArray(object.initializer))
                    throw $TypeError(".onnx.GraphProto.initializer: array expected");
                message.initializer = $Array(object.initializer.length);
                for (let i = 0; i < object.initializer.length; ++i) {
                    if (!$util.isObject(object.initializer[i]))
                        throw $TypeError(".onnx.GraphProto.initializer: object expected");
                    message.initializer[i] = $root.onnx.TensorProto.fromObject(object.initializer[i], _depth + 1);
                }
            }
            if (object.sparseInitializer) {
                if (!$Array.isArray(object.sparseInitializer))
                    throw $TypeError(".onnx.GraphProto.sparseInitializer: array expected");
                message.sparseInitializer = $Array(object.sparseInitializer.length);
                for (let i = 0; i < object.sparseInitializer.length; ++i) {
                    if (!$util.isObject(object.sparseInitializer[i]))
                        throw $TypeError(".onnx.GraphProto.sparseInitializer: object expected");
                    message.sparseInitializer[i] = $root.onnx.SparseTensorProto.fromObject(object.sparseInitializer[i], _depth + 1);
                }
            }
            if (object.docString != null)
                message.docString = $String(object.docString);
            if (object.input) {
                if (!$Array.isArray(object.input))
                    throw $TypeError(".onnx.GraphProto.input: array expected");
                message.input = $Array(object.input.length);
                for (let i = 0; i < object.input.length; ++i) {
                    if (!$util.isObject(object.input[i]))
                        throw $TypeError(".onnx.GraphProto.input: object expected");
                    message.input[i] = $root.onnx.ValueInfoProto.fromObject(object.input[i], _depth + 1);
                }
            }
            if (object.output) {
                if (!$Array.isArray(object.output))
                    throw $TypeError(".onnx.GraphProto.output: array expected");
                message.output = $Array(object.output.length);
                for (let i = 0; i < object.output.length; ++i) {
                    if (!$util.isObject(object.output[i]))
                        throw $TypeError(".onnx.GraphProto.output: object expected");
                    message.output[i] = $root.onnx.ValueInfoProto.fromObject(object.output[i], _depth + 1);
                }
            }
            if (object.valueInfo) {
                if (!$Array.isArray(object.valueInfo))
                    throw $TypeError(".onnx.GraphProto.valueInfo: array expected");
                message.valueInfo = $Array(object.valueInfo.length);
                for (let i = 0; i < object.valueInfo.length; ++i) {
                    if (!$util.isObject(object.valueInfo[i]))
                        throw $TypeError(".onnx.GraphProto.valueInfo: object expected");
                    message.valueInfo[i] = $root.onnx.ValueInfoProto.fromObject(object.valueInfo[i], _depth + 1);
                }
            }
            if (object.quantizationAnnotation) {
                if (!$Array.isArray(object.quantizationAnnotation))
                    throw $TypeError(".onnx.GraphProto.quantizationAnnotation: array expected");
                message.quantizationAnnotation = $Array(object.quantizationAnnotation.length);
                for (let i = 0; i < object.quantizationAnnotation.length; ++i) {
                    if (!$util.isObject(object.quantizationAnnotation[i]))
                        throw $TypeError(".onnx.GraphProto.quantizationAnnotation: object expected");
                    message.quantizationAnnotation[i] = $root.onnx.TensorAnnotation.fromObject(object.quantizationAnnotation[i], _depth + 1);
                }
            }
            if (object.metadataProps) {
                if (!$Array.isArray(object.metadataProps))
                    throw $TypeError(".onnx.GraphProto.metadataProps: array expected");
                message.metadataProps = $Array(object.metadataProps.length);
                for (let i = 0; i < object.metadataProps.length; ++i) {
                    if (!$util.isObject(object.metadataProps[i]))
                        throw $TypeError(".onnx.GraphProto.metadataProps: object expected");
                    message.metadataProps[i] = $root.onnx.StringStringEntryProto.fromObject(object.metadataProps[i], _depth + 1);
                }
            }
            return message;
        };

        /**
         * Creates a plain object from a GraphProto message. Also converts values to other types if specified.
         * @function toObject
         * @memberof onnx.GraphProto
         * @static
         * @param {onnx.GraphProto} message GraphProto
         * @param {$protobuf.IConversionOptions} [options] Conversion options
         * @returns {Object.<string,*>} Plain object
         */
        GraphProto.toObject = function (message, options, _depth) {
            if (!options)
                options = {};
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                throw $Error("max depth exceeded");
            let object = {};
            if (options.arrays || options.defaults) {
                object.node = [];
                object.initializer = [];
                object.input = [];
                object.output = [];
                object.valueInfo = [];
                object.quantizationAnnotation = [];
                object.sparseInitializer = [];
                object.metadataProps = [];
            }
            if (options.defaults) {
                object.name = "";
                object.docString = "";
            }
            if (message.node && message.node.length) {
                object.node = $Array(message.node.length);
                for (let j = 0; j < message.node.length; ++j)
                    object.node[j] = $root.onnx.NodeProto.toObject(message.node[j], options, _depth + 1);
            }
            if (message.name != null && $Object.hasOwnProperty.call(message, "name"))
                object.name = message.name;
            if (message.initializer && message.initializer.length) {
                object.initializer = $Array(message.initializer.length);
                for (let j = 0; j < message.initializer.length; ++j)
                    object.initializer[j] = $root.onnx.TensorProto.toObject(message.initializer[j], options, _depth + 1);
            }
            if (message.docString != null && $Object.hasOwnProperty.call(message, "docString"))
                object.docString = message.docString;
            if (message.input && message.input.length) {
                object.input = $Array(message.input.length);
                for (let j = 0; j < message.input.length; ++j)
                    object.input[j] = $root.onnx.ValueInfoProto.toObject(message.input[j], options, _depth + 1);
            }
            if (message.output && message.output.length) {
                object.output = $Array(message.output.length);
                for (let j = 0; j < message.output.length; ++j)
                    object.output[j] = $root.onnx.ValueInfoProto.toObject(message.output[j], options, _depth + 1);
            }
            if (message.valueInfo && message.valueInfo.length) {
                object.valueInfo = $Array(message.valueInfo.length);
                for (let j = 0; j < message.valueInfo.length; ++j)
                    object.valueInfo[j] = $root.onnx.ValueInfoProto.toObject(message.valueInfo[j], options, _depth + 1);
            }
            if (message.quantizationAnnotation && message.quantizationAnnotation.length) {
                object.quantizationAnnotation = $Array(message.quantizationAnnotation.length);
                for (let j = 0; j < message.quantizationAnnotation.length; ++j)
                    object.quantizationAnnotation[j] = $root.onnx.TensorAnnotation.toObject(message.quantizationAnnotation[j], options, _depth + 1);
            }
            if (message.sparseInitializer && message.sparseInitializer.length) {
                object.sparseInitializer = $Array(message.sparseInitializer.length);
                for (let j = 0; j < message.sparseInitializer.length; ++j)
                    object.sparseInitializer[j] = $root.onnx.SparseTensorProto.toObject(message.sparseInitializer[j], options, _depth + 1);
            }
            if (message.metadataProps && message.metadataProps.length) {
                object.metadataProps = $Array(message.metadataProps.length);
                for (let j = 0; j < message.metadataProps.length; ++j)
                    object.metadataProps[j] = $root.onnx.StringStringEntryProto.toObject(message.metadataProps[j], options, _depth + 1);
            }
            return object;
        };

        /**
         * Converts this GraphProto to JSON.
         * @function toJSON
         * @memberof onnx.GraphProto
         * @instance
         * @returns {Object.<string,*>} JSON object
         */
        GraphProto.prototype.toJSON = function() {
            return GraphProto.toObject(this, $protobuf.util.toJSONOptions);
        };

        /**
         * Gets the type url for GraphProto
         * @function getTypeUrl
         * @memberof onnx.GraphProto
         * @static
         * @param {string} [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
         * @returns {string} The type url
         */
        GraphProto.getTypeUrl = function(prefix) {
            if (prefix === $undefined)
                prefix = "type.googleapis.com";
            return prefix + "/onnx.GraphProto";
        };

        return GraphProto;
    })();

    onnx.TensorProto = (function() {

        /**
         * Properties of a TensorProto.
         * @typedef {Object} onnx.TensorProto.$Properties
         * @property {Array.<number|Long>|null} [dims] TensorProto dims
         * @property {number|null} [dataType] TensorProto dataType
         * @property {onnx.TensorProto.Segment.$Properties|null} [segment] TensorProto segment
         * @property {Array.<number>|null} [floatData] TensorProto floatData
         * @property {Array.<number>|null} [int32Data] TensorProto int32Data
         * @property {Array.<Uint8Array>|null} [stringData] TensorProto stringData
         * @property {Array.<number|Long>|null} [int64Data] TensorProto int64Data
         * @property {string|null} [name] TensorProto name
         * @property {string|null} [docString] TensorProto docString
         * @property {Uint8Array|null} [rawData] TensorProto rawData
         * @property {Array.<onnx.StringStringEntryProto.$Properties>|null} [externalData] TensorProto externalData
         * @property {onnx.TensorProto.DataLocation|null} [dataLocation] TensorProto dataLocation
         * @property {Array.<number>|null} [doubleData] TensorProto doubleData
         * @property {Array.<number|Long>|null} [uint64Data] TensorProto uint64Data
         * @property {Array.<onnx.StringStringEntryProto.$Properties>|null} [metadataProps] TensorProto metadataProps
         * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding when enabled
         */

        /**
         * Properties of a TensorProto.
         * @memberof onnx
         * @interface ITensorProto
         * @augments onnx.TensorProto.$Properties
         * @deprecated Use onnx.TensorProto.$Properties instead.
         */

        /**
         * Shape of a TensorProto.
         * @typedef {onnx.TensorProto.$Properties} onnx.TensorProto.$Shape
         */

        /**
         * Constructs a new TensorProto.
         * @memberof onnx
         * @classdesc Represents a TensorProto.
         * @constructor
         * @param {onnx.TensorProto.$Properties=} [properties] Properties to set
         * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding when enabled
         */
        const TensorProto = function (properties) {
            this.dims = [];
            this.floatData = [];
            this.int32Data = [];
            this.stringData = [];
            this.int64Data = [];
            this.externalData = [];
            this.doubleData = [];
            this.uint64Data = [];
            this.metadataProps = [];
            if (properties)
                for (let keys = $Object.keys(properties), i = 0; i < keys.length; ++i)
                    if (properties[keys[i]] != null && keys[i] !== "__proto__")
                        this[keys[i]] = properties[keys[i]];
        };

        /**
         * TensorProto dims.
         * @member {Array.<number|Long>} dims
         * @memberof onnx.TensorProto
         * @instance
         */
        TensorProto.prototype.dims = $util.emptyArray;

        /**
         * TensorProto dataType.
         * @member {number} dataType
         * @memberof onnx.TensorProto
         * @instance
         */
        TensorProto.prototype.dataType = 0;

        /**
         * TensorProto segment.
         * @member {onnx.TensorProto.Segment.$Properties|null|undefined} segment
         * @memberof onnx.TensorProto
         * @instance
         */
        TensorProto.prototype.segment = null;

        /**
         * TensorProto floatData.
         * @member {Array.<number>} floatData
         * @memberof onnx.TensorProto
         * @instance
         */
        TensorProto.prototype.floatData = $util.emptyArray;

        /**
         * TensorProto int32Data.
         * @member {Array.<number>} int32Data
         * @memberof onnx.TensorProto
         * @instance
         */
        TensorProto.prototype.int32Data = $util.emptyArray;

        /**
         * TensorProto stringData.
         * @member {Array.<Uint8Array>} stringData
         * @memberof onnx.TensorProto
         * @instance
         */
        TensorProto.prototype.stringData = $util.emptyArray;

        /**
         * TensorProto int64Data.
         * @member {Array.<number|Long>} int64Data
         * @memberof onnx.TensorProto
         * @instance
         */
        TensorProto.prototype.int64Data = $util.emptyArray;

        /**
         * TensorProto name.
         * @member {string} name
         * @memberof onnx.TensorProto
         * @instance
         */
        TensorProto.prototype.name = "";

        /**
         * TensorProto docString.
         * @member {string} docString
         * @memberof onnx.TensorProto
         * @instance
         */
        TensorProto.prototype.docString = "";

        /**
         * TensorProto rawData.
         * @member {Uint8Array} rawData
         * @memberof onnx.TensorProto
         * @instance
         */
        TensorProto.prototype.rawData = $util.newBuffer([]);

        /**
         * TensorProto externalData.
         * @member {Array.<onnx.StringStringEntryProto.$Properties>} externalData
         * @memberof onnx.TensorProto
         * @instance
         */
        TensorProto.prototype.externalData = $util.emptyArray;

        /**
         * TensorProto dataLocation.
         * @member {onnx.TensorProto.DataLocation} dataLocation
         * @memberof onnx.TensorProto
         * @instance
         */
        TensorProto.prototype.dataLocation = 0;

        /**
         * TensorProto doubleData.
         * @member {Array.<number>} doubleData
         * @memberof onnx.TensorProto
         * @instance
         */
        TensorProto.prototype.doubleData = $util.emptyArray;

        /**
         * TensorProto uint64Data.
         * @member {Array.<number|Long>} uint64Data
         * @memberof onnx.TensorProto
         * @instance
         */
        TensorProto.prototype.uint64Data = $util.emptyArray;

        /**
         * TensorProto metadataProps.
         * @member {Array.<onnx.StringStringEntryProto.$Properties>} metadataProps
         * @memberof onnx.TensorProto
         * @instance
         */
        TensorProto.prototype.metadataProps = $util.emptyArray;

        /**
         * Creates a new TensorProto instance using the specified properties.
         * @function create
         * @memberof onnx.TensorProto
         * @static
         * @param {onnx.TensorProto.$Properties=} [properties] Properties to set
         * @returns {onnx.TensorProto} TensorProto instance
         * @type {{
         *   (properties: onnx.TensorProto.$Shape): onnx.TensorProto & onnx.TensorProto.$Shape;
         *   (properties?: onnx.TensorProto.$Properties): onnx.TensorProto;
         * }}
         */
        TensorProto.create = function(properties) {
            return new TensorProto(properties);
        };

        /**
         * Encodes the specified TensorProto message. Does not implicitly {@link onnx.TensorProto.verify|verify} messages.
         * @function encode
         * @memberof onnx.TensorProto
         * @static
         * @param {onnx.TensorProto.$Properties} message TensorProto message or plain object to encode
         * @param {$protobuf.Writer} [writer] Writer to encode to
         * @returns {$protobuf.Writer} Writer
         */
        TensorProto.encode = function (message, writer, _depth) {
            if (!writer)
                writer = $Writer.create();
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                throw $Error("max depth exceeded");
            if (message.dims != null && message.dims.length)
                for (let i = 0; i < message.dims.length; ++i)
                    writer.uint32(/* id 1, wireType 0 =*/8).int64(message.dims[i]);
            if (message.dataType != null && $Object.hasOwnProperty.call(message, "dataType"))
                writer.uint32(/* id 2, wireType 0 =*/16).int32(message.dataType);
            if (message.segment != null && $Object.hasOwnProperty.call(message, "segment"))
                $root.onnx.TensorProto.Segment.encode(message.segment, writer.uint32(/* id 3, wireType 2 =*/26).fork(), _depth + 1).ldelim();
            if (message.floatData != null && message.floatData.length)
                writer.uint32(/* id 4, wireType 2 =*/34).floats(message.floatData);
            if (message.int32Data != null && message.int32Data.length)
                writer.uint32(/* id 5, wireType 2 =*/42).int32s(message.int32Data);
            if (message.stringData != null && message.stringData.length)
                for (let i = 0; i < message.stringData.length; ++i)
                    writer.uint32(/* id 6, wireType 2 =*/50).bytes(message.stringData[i]);
            if (message.int64Data != null && message.int64Data.length)
                writer.uint32(/* id 7, wireType 2 =*/58).int64s(message.int64Data);
            if (message.name != null && $Object.hasOwnProperty.call(message, "name"))
                writer.uint32(/* id 8, wireType 2 =*/66).string(message.name);
            if (message.rawData != null && $Object.hasOwnProperty.call(message, "rawData"))
                writer.uint32(/* id 9, wireType 2 =*/74).bytes(message.rawData);
            if (message.doubleData != null && message.doubleData.length)
                writer.uint32(/* id 10, wireType 2 =*/82).doubles(message.doubleData);
            if (message.uint64Data != null && message.uint64Data.length)
                writer.uint32(/* id 11, wireType 2 =*/90).uint64s(message.uint64Data);
            if (message.docString != null && $Object.hasOwnProperty.call(message, "docString"))
                writer.uint32(/* id 12, wireType 2 =*/98).string(message.docString);
            if (message.externalData != null && message.externalData.length)
                for (let i = 0; i < message.externalData.length; ++i)
                    $root.onnx.StringStringEntryProto.encode(message.externalData[i], writer.uint32(/* id 13, wireType 2 =*/106).fork(), _depth + 1).ldelim();
            if (message.dataLocation != null && $Object.hasOwnProperty.call(message, "dataLocation"))
                writer.uint32(/* id 14, wireType 0 =*/112).int32(message.dataLocation);
            if (message.metadataProps != null && message.metadataProps.length)
                for (let i = 0; i < message.metadataProps.length; ++i)
                    $root.onnx.StringStringEntryProto.encode(message.metadataProps[i], writer.uint32(/* id 16, wireType 2 =*/130).fork(), _depth + 1).ldelim();
            if (message.$unknowns != null && $Object.hasOwnProperty.call(message, "$unknowns"))
                for (let i = 0; i < message.$unknowns.length; ++i)
                    writer.raw(message.$unknowns[i]);
            return writer;
        };

        /**
         * Encodes the specified TensorProto message, length delimited. Does not implicitly {@link onnx.TensorProto.verify|verify} messages.
         * @function encodeDelimited
         * @memberof onnx.TensorProto
         * @static
         * @param {onnx.TensorProto.$Properties} message TensorProto message or plain object to encode
         * @param {$protobuf.Writer} [writer] Writer to encode to
         * @returns {$protobuf.Writer} Writer
         */
        TensorProto.encodeDelimited = function(message, writer) {
            return this.encode(message, (writer || $Writer.create()).fork()).ldelim();
        };

        /**
         * Decodes a TensorProto message from the specified reader or buffer.
         * @function decode
         * @memberof onnx.TensorProto
         * @static
         * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
         * @param {number} [length] Message length if known beforehand
         * @returns {onnx.TensorProto & onnx.TensorProto.$Shape} TensorProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        TensorProto.decode = function (reader, length, _end, _depth, _target) {
            if (!(reader instanceof $Reader))
                reader = $Reader.create(reader);
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $Reader.recursionLimit)
                throw $Error("max depth exceeded");
            let end = length === $undefined ? reader.len : reader.pos + length, message = _target || new $root.onnx.TensorProto(), value;
            while (reader.pos < end) {
                let start = reader.pos;
                let tag = reader.tag();
                if (tag === _end) {
                    _end = $undefined;
                    break;
                }
                let wireType = tag & 7;
                switch (tag >>>= 3) {
                case 1: {
                        if (wireType === 2) {
                            if (!(message.dims && message.dims.length))
                                message.dims = [];
                            reader.int64s(message.dims);
                            continue;
                        }
                        if (wireType !== 0)
                            break;
                        if (!(message.dims && message.dims.length))
                            message.dims = [];
                        message.dims.push(reader.int64());
                        continue;
                    }
                case 2: {
                        if (wireType !== 0)
                            break;
                        message.dataType = reader.int32();
                        continue;
                    }
                case 3: {
                        if (wireType !== 2)
                            break;
                        message.segment = $root.onnx.TensorProto.Segment.decode(reader, reader.uint32(), $undefined, _depth + 1, message.segment);
                        continue;
                    }
                case 4: {
                        if (wireType === 2) {
                            if (!(message.floatData && message.floatData.length))
                                message.floatData = [];
                            reader.floats(message.floatData);
                            continue;
                        }
                        if (wireType !== 5)
                            break;
                        if (!(message.floatData && message.floatData.length))
                            message.floatData = [];
                        message.floatData.push(reader.float());
                        continue;
                    }
                case 5: {
                        if (wireType === 2) {
                            if (!(message.int32Data && message.int32Data.length))
                                message.int32Data = [];
                            reader.int32s(message.int32Data);
                            continue;
                        }
                        if (wireType !== 0)
                            break;
                        if (!(message.int32Data && message.int32Data.length))
                            message.int32Data = [];
                        message.int32Data.push(reader.int32());
                        continue;
                    }
                case 6: {
                        if (wireType !== 2)
                            break;
                        if (!(message.stringData && message.stringData.length))
                            message.stringData = [];
                        message.stringData.push(reader.bytes());
                        continue;
                    }
                case 7: {
                        if (wireType === 2) {
                            if (!(message.int64Data && message.int64Data.length))
                                message.int64Data = [];
                            reader.int64s(message.int64Data);
                            continue;
                        }
                        if (wireType !== 0)
                            break;
                        if (!(message.int64Data && message.int64Data.length))
                            message.int64Data = [];
                        message.int64Data.push(reader.int64());
                        continue;
                    }
                case 8: {
                        if (wireType !== 2)
                            break;
                        message.name = reader.string();
                        continue;
                    }
                case 12: {
                        if (wireType !== 2)
                            break;
                        message.docString = reader.string();
                        continue;
                    }
                case 9: {
                        if (wireType !== 2)
                            break;
                        message.rawData = reader.bytes();
                        continue;
                    }
                case 13: {
                        if (wireType !== 2)
                            break;
                        if (!(message.externalData && message.externalData.length))
                            message.externalData = [];
                        message.externalData.push($root.onnx.StringStringEntryProto.decode(reader, reader.uint32(), $undefined, _depth + 1));
                        continue;
                    }
                case 14: {
                        if (wireType !== 0)
                            break;
                        value = reader.int32();
                        if ($root.onnx.TensorProto.DataLocation[value] !== $undefined)
                            message.dataLocation = value;
                        else if (!reader.discardUnknown) {
                            $util.makeProp(message, "$unknowns", false);
                            (message.$unknowns || (message.$unknowns = [])).push(reader.raw(start, reader.pos));
                        }
                        continue;
                    }
                case 10: {
                        if (wireType === 2) {
                            if (!(message.doubleData && message.doubleData.length))
                                message.doubleData = [];
                            reader.doubles(message.doubleData);
                            continue;
                        }
                        if (wireType !== 1)
                            break;
                        if (!(message.doubleData && message.doubleData.length))
                            message.doubleData = [];
                        message.doubleData.push(reader.double());
                        continue;
                    }
                case 11: {
                        if (wireType === 2) {
                            if (!(message.uint64Data && message.uint64Data.length))
                                message.uint64Data = [];
                            reader.uint64s(message.uint64Data);
                            continue;
                        }
                        if (wireType !== 0)
                            break;
                        if (!(message.uint64Data && message.uint64Data.length))
                            message.uint64Data = [];
                        message.uint64Data.push(reader.uint64());
                        continue;
                    }
                case 16: {
                        if (wireType !== 2)
                            break;
                        if (!(message.metadataProps && message.metadataProps.length))
                            message.metadataProps = [];
                        message.metadataProps.push($root.onnx.StringStringEntryProto.decode(reader, reader.uint32(), $undefined, _depth + 1));
                        continue;
                    }
                }
                reader.skipType(wireType, _depth, tag);
                if (!reader.discardUnknown) {
                    $util.makeProp(message, "$unknowns", false);
                    (message.$unknowns || (message.$unknowns = [])).push(reader.raw(start, reader.pos));
                }
            }
            if (_end !== $undefined)
                throw $Error("missing end group");
            return message;
        };

        /**
         * Decodes a TensorProto message from the specified reader or buffer, length delimited.
         * @function decodeDelimited
         * @memberof onnx.TensorProto
         * @static
         * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
         * @returns {onnx.TensorProto & onnx.TensorProto.$Shape} TensorProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        TensorProto.decodeDelimited = function(reader) {
            if (!(reader instanceof $Reader))
                reader = new $Reader(reader);
            return this.decode(reader, reader.uint32());
        };

        /**
         * Verifies a TensorProto message.
         * @function verify
         * @memberof onnx.TensorProto
         * @static
         * @param {Object.<string,*>} message Plain object to verify
         * @returns {string|null} `null` if valid, otherwise the reason why it is not
         */
        TensorProto.verify = function (message, _depth) {
            if (typeof message !== "object" || message === null)
                return "object expected";
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                return "max depth exceeded";
            if (message.dims != null && $Object.hasOwnProperty.call(message, "dims")) {
                if (!$Array.isArray(message.dims))
                    return "dims: array expected";
                for (let i = 0; i < message.dims.length; ++i)
                    if (!$util.isInteger(message.dims[i]) && !(message.dims[i] && $util.isInteger(message.dims[i].low) && $util.isInteger(message.dims[i].high)))
                        return "dims: integer|Long[] expected";
            }
            if (message.dataType != null && $Object.hasOwnProperty.call(message, "dataType"))
                if (!$util.isInteger(message.dataType))
                    return "dataType: integer expected";
            if (message.segment != null && $Object.hasOwnProperty.call(message, "segment")) {
                let error = $root.onnx.TensorProto.Segment.verify(message.segment, _depth + 1);
                if (error)
                    return "segment." + error;
            }
            if (message.floatData != null && $Object.hasOwnProperty.call(message, "floatData")) {
                if (!$Array.isArray(message.floatData))
                    return "floatData: array expected";
                for (let i = 0; i < message.floatData.length; ++i)
                    if (typeof message.floatData[i] !== "number")
                        return "floatData: number[] expected";
            }
            if (message.int32Data != null && $Object.hasOwnProperty.call(message, "int32Data")) {
                if (!$Array.isArray(message.int32Data))
                    return "int32Data: array expected";
                for (let i = 0; i < message.int32Data.length; ++i)
                    if (!$util.isInteger(message.int32Data[i]))
                        return "int32Data: integer[] expected";
            }
            if (message.stringData != null && $Object.hasOwnProperty.call(message, "stringData")) {
                if (!$Array.isArray(message.stringData))
                    return "stringData: array expected";
                for (let i = 0; i < message.stringData.length; ++i)
                    if (!(message.stringData[i] && typeof message.stringData[i].length === "number" || $util.isString(message.stringData[i])))
                        return "stringData: buffer[] expected";
            }
            if (message.int64Data != null && $Object.hasOwnProperty.call(message, "int64Data")) {
                if (!$Array.isArray(message.int64Data))
                    return "int64Data: array expected";
                for (let i = 0; i < message.int64Data.length; ++i)
                    if (!$util.isInteger(message.int64Data[i]) && !(message.int64Data[i] && $util.isInteger(message.int64Data[i].low) && $util.isInteger(message.int64Data[i].high)))
                        return "int64Data: integer|Long[] expected";
            }
            if (message.name != null && $Object.hasOwnProperty.call(message, "name"))
                if (!$util.isString(message.name))
                    return "name: string expected";
            if (message.docString != null && $Object.hasOwnProperty.call(message, "docString"))
                if (!$util.isString(message.docString))
                    return "docString: string expected";
            if (message.rawData != null && $Object.hasOwnProperty.call(message, "rawData"))
                if (!(message.rawData && typeof message.rawData.length === "number" || $util.isString(message.rawData)))
                    return "rawData: buffer expected";
            if (message.externalData != null && $Object.hasOwnProperty.call(message, "externalData")) {
                if (!$Array.isArray(message.externalData))
                    return "externalData: array expected";
                for (let i = 0; i < message.externalData.length; ++i) {
                    let error = $root.onnx.StringStringEntryProto.verify(message.externalData[i], _depth + 1);
                    if (error)
                        return "externalData." + error;
                }
            }
            if (message.dataLocation != null && $Object.hasOwnProperty.call(message, "dataLocation"))
                switch (message.dataLocation) {
                default:
                    return "dataLocation: enum value expected";
                case 0:
                case 1:
                    break;
                }
            if (message.doubleData != null && $Object.hasOwnProperty.call(message, "doubleData")) {
                if (!$Array.isArray(message.doubleData))
                    return "doubleData: array expected";
                for (let i = 0; i < message.doubleData.length; ++i)
                    if (typeof message.doubleData[i] !== "number")
                        return "doubleData: number[] expected";
            }
            if (message.uint64Data != null && $Object.hasOwnProperty.call(message, "uint64Data")) {
                if (!$Array.isArray(message.uint64Data))
                    return "uint64Data: array expected";
                for (let i = 0; i < message.uint64Data.length; ++i)
                    if (!$util.isInteger(message.uint64Data[i]) && !(message.uint64Data[i] && $util.isInteger(message.uint64Data[i].low) && $util.isInteger(message.uint64Data[i].high)))
                        return "uint64Data: integer|Long[] expected";
            }
            if (message.metadataProps != null && $Object.hasOwnProperty.call(message, "metadataProps")) {
                if (!$Array.isArray(message.metadataProps))
                    return "metadataProps: array expected";
                for (let i = 0; i < message.metadataProps.length; ++i) {
                    let error = $root.onnx.StringStringEntryProto.verify(message.metadataProps[i], _depth + 1);
                    if (error)
                        return "metadataProps." + error;
                }
            }
            return null;
        };

        /**
         * Creates a TensorProto message from a plain object. Also converts values to their respective internal types.
         * @function fromObject
         * @memberof onnx.TensorProto
         * @static
         * @param {Object.<string,*>} object Plain object
         * @returns {onnx.TensorProto} TensorProto
         */
        TensorProto.fromObject = function (object, _depth) {
            if (object instanceof $root.onnx.TensorProto)
                return object;
            if (!$util.isObject(object))
                throw $TypeError(".onnx.TensorProto: object expected");
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                throw $Error("max depth exceeded");
            let message = new $root.onnx.TensorProto();
            if (object.dims) {
                if (!$Array.isArray(object.dims))
                    throw $TypeError(".onnx.TensorProto.dims: array expected");
                message.dims = $Array(object.dims.length);
                for (let i = 0; i < object.dims.length; ++i)
                    if ($util.Long)
                        message.dims[i] = $util.Long.fromValue(object.dims[i], false);
                    else if (typeof object.dims[i] === "string")
                        message.dims[i] = $parseInt(object.dims[i], 10);
                    else if (typeof object.dims[i] === "number")
                        message.dims[i] = object.dims[i];
                    else if (typeof object.dims[i] === "object")
                        message.dims[i] = new $util.LongBits(object.dims[i].low >>> 0, object.dims[i].high >>> 0).toNumber();
            }
            if (object.dataType != null)
                message.dataType = object.dataType | 0;
            if (object.segment != null) {
                if (!$util.isObject(object.segment))
                    throw $TypeError(".onnx.TensorProto.segment: object expected");
                message.segment = $root.onnx.TensorProto.Segment.fromObject(object.segment, _depth + 1);
            }
            if (object.floatData) {
                if (!$Array.isArray(object.floatData))
                    throw $TypeError(".onnx.TensorProto.floatData: array expected");
                message.floatData = $Array(object.floatData.length);
                for (let i = 0; i < object.floatData.length; ++i)
                    message.floatData[i] = $Number(object.floatData[i]);
            }
            if (object.int32Data) {
                if (!$Array.isArray(object.int32Data))
                    throw $TypeError(".onnx.TensorProto.int32Data: array expected");
                message.int32Data = $Array(object.int32Data.length);
                for (let i = 0; i < object.int32Data.length; ++i)
                    message.int32Data[i] = object.int32Data[i] | 0;
            }
            if (object.stringData) {
                if (!$Array.isArray(object.stringData))
                    throw $TypeError(".onnx.TensorProto.stringData: array expected");
                message.stringData = $Array(object.stringData.length);
                for (let i = 0; i < object.stringData.length; ++i)
                    if (typeof object.stringData[i] === "string")
                        $util.base64.decode(object.stringData[i], message.stringData[i] = $util.newBuffer($util.base64.length(object.stringData[i])), 0);
                    else if (object.stringData[i].length >= 0)
                        message.stringData[i] = object.stringData[i];
            }
            if (object.int64Data) {
                if (!$Array.isArray(object.int64Data))
                    throw $TypeError(".onnx.TensorProto.int64Data: array expected");
                message.int64Data = $Array(object.int64Data.length);
                for (let i = 0; i < object.int64Data.length; ++i)
                    if ($util.Long)
                        message.int64Data[i] = $util.Long.fromValue(object.int64Data[i], false);
                    else if (typeof object.int64Data[i] === "string")
                        message.int64Data[i] = $parseInt(object.int64Data[i], 10);
                    else if (typeof object.int64Data[i] === "number")
                        message.int64Data[i] = object.int64Data[i];
                    else if (typeof object.int64Data[i] === "object")
                        message.int64Data[i] = new $util.LongBits(object.int64Data[i].low >>> 0, object.int64Data[i].high >>> 0).toNumber();
            }
            if (object.name != null)
                message.name = $String(object.name);
            if (object.docString != null)
                message.docString = $String(object.docString);
            if (object.rawData != null)
                if (typeof object.rawData === "string")
                    $util.base64.decode(object.rawData, message.rawData = $util.newBuffer($util.base64.length(object.rawData)), 0);
                else if (object.rawData.length >= 0)
                    message.rawData = object.rawData;
            if (object.externalData) {
                if (!$Array.isArray(object.externalData))
                    throw $TypeError(".onnx.TensorProto.externalData: array expected");
                message.externalData = $Array(object.externalData.length);
                for (let i = 0; i < object.externalData.length; ++i) {
                    if (!$util.isObject(object.externalData[i]))
                        throw $TypeError(".onnx.TensorProto.externalData: object expected");
                    message.externalData[i] = $root.onnx.StringStringEntryProto.fromObject(object.externalData[i], _depth + 1);
                }
            }
            switch (object.dataLocation) {
            case "DEFAULT":
            case 0:
                message.dataLocation = 0;
                break;
            case "EXTERNAL":
            case 1:
                message.dataLocation = 1;
                break;
            default:
            }
            if (object.doubleData) {
                if (!$Array.isArray(object.doubleData))
                    throw $TypeError(".onnx.TensorProto.doubleData: array expected");
                message.doubleData = $Array(object.doubleData.length);
                for (let i = 0; i < object.doubleData.length; ++i)
                    message.doubleData[i] = $Number(object.doubleData[i]);
            }
            if (object.uint64Data) {
                if (!$Array.isArray(object.uint64Data))
                    throw $TypeError(".onnx.TensorProto.uint64Data: array expected");
                message.uint64Data = $Array(object.uint64Data.length);
                for (let i = 0; i < object.uint64Data.length; ++i)
                    if ($util.Long)
                        message.uint64Data[i] = $util.Long.fromValue(object.uint64Data[i], true);
                    else if (typeof object.uint64Data[i] === "string")
                        message.uint64Data[i] = $parseInt(object.uint64Data[i], 10);
                    else if (typeof object.uint64Data[i] === "number")
                        message.uint64Data[i] = object.uint64Data[i];
                    else if (typeof object.uint64Data[i] === "object")
                        message.uint64Data[i] = new $util.LongBits(object.uint64Data[i].low >>> 0, object.uint64Data[i].high >>> 0).toNumber(true);
            }
            if (object.metadataProps) {
                if (!$Array.isArray(object.metadataProps))
                    throw $TypeError(".onnx.TensorProto.metadataProps: array expected");
                message.metadataProps = $Array(object.metadataProps.length);
                for (let i = 0; i < object.metadataProps.length; ++i) {
                    if (!$util.isObject(object.metadataProps[i]))
                        throw $TypeError(".onnx.TensorProto.metadataProps: object expected");
                    message.metadataProps[i] = $root.onnx.StringStringEntryProto.fromObject(object.metadataProps[i], _depth + 1);
                }
            }
            return message;
        };

        /**
         * Creates a plain object from a TensorProto message. Also converts values to other types if specified.
         * @function toObject
         * @memberof onnx.TensorProto
         * @static
         * @param {onnx.TensorProto} message TensorProto
         * @param {$protobuf.IConversionOptions} [options] Conversion options
         * @returns {Object.<string,*>} Plain object
         */
        TensorProto.toObject = function (message, options, _depth) {
            if (!options)
                options = {};
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                throw $Error("max depth exceeded");
            let object = {};
            if (options.arrays || options.defaults) {
                object.dims = [];
                object.floatData = [];
                object.int32Data = [];
                object.stringData = [];
                object.int64Data = [];
                object.doubleData = [];
                object.uint64Data = [];
                object.externalData = [];
                object.metadataProps = [];
            }
            if (options.defaults) {
                object.dataType = 0;
                object.segment = null;
                object.name = "";
                if (options.bytes === $String)
                    object.rawData = "";
                else {
                    object.rawData = [];
                    if (options.bytes !== $Array)
                        object.rawData = $util.newBuffer(object.rawData);
                }
                object.docString = "";
                object.dataLocation = options.enums === $String ? "DEFAULT" : 0;
            }
            if (message.dims && message.dims.length) {
                object.dims = $Array(message.dims.length);
                for (let j = 0; j < message.dims.length; ++j)
                    if (typeof $BigInt !== "undefined" && options.longs === $BigInt)
                        object.dims[j] = typeof message.dims[j] === "number" ? $BigInt(message.dims[j]) : $util.Long.fromBits(message.dims[j].low >>> 0, message.dims[j].high >>> 0, false).toBigInt();
                    else if (typeof message.dims[j] === "number")
                        object.dims[j] = options.longs === $String ? $String(message.dims[j]) : message.dims[j];
                    else
                        object.dims[j] = options.longs === $String ? $util.Long.prototype.toString.call(message.dims[j]) : options.longs === $Number ? new $util.LongBits(message.dims[j].low >>> 0, message.dims[j].high >>> 0).toNumber() : message.dims[j];
            }
            if (message.dataType != null && $Object.hasOwnProperty.call(message, "dataType"))
                object.dataType = message.dataType;
            if (message.segment != null && $Object.hasOwnProperty.call(message, "segment"))
                object.segment = $root.onnx.TensorProto.Segment.toObject(message.segment, options, _depth + 1);
            if (message.floatData && message.floatData.length) {
                object.floatData = $Array(message.floatData.length);
                for (let j = 0; j < message.floatData.length; ++j)
                    object.floatData[j] = options.json && !$isFinite(message.floatData[j]) ? $String(message.floatData[j]) : message.floatData[j];
            }
            if (message.int32Data && message.int32Data.length) {
                object.int32Data = $Array(message.int32Data.length);
                for (let j = 0; j < message.int32Data.length; ++j)
                    object.int32Data[j] = message.int32Data[j];
            }
            if (message.stringData && message.stringData.length) {
                object.stringData = $Array(message.stringData.length);
                for (let j = 0; j < message.stringData.length; ++j)
                    object.stringData[j] = options.bytes === $String ? $util.base64.encode(message.stringData[j], 0, message.stringData[j].length) : options.bytes === $Array ? $Array.prototype.slice.call(message.stringData[j]) : message.stringData[j];
            }
            if (message.int64Data && message.int64Data.length) {
                object.int64Data = $Array(message.int64Data.length);
                for (let j = 0; j < message.int64Data.length; ++j)
                    if (typeof $BigInt !== "undefined" && options.longs === $BigInt)
                        object.int64Data[j] = typeof message.int64Data[j] === "number" ? $BigInt(message.int64Data[j]) : $util.Long.fromBits(message.int64Data[j].low >>> 0, message.int64Data[j].high >>> 0, false).toBigInt();
                    else if (typeof message.int64Data[j] === "number")
                        object.int64Data[j] = options.longs === $String ? $String(message.int64Data[j]) : message.int64Data[j];
                    else
                        object.int64Data[j] = options.longs === $String ? $util.Long.prototype.toString.call(message.int64Data[j]) : options.longs === $Number ? new $util.LongBits(message.int64Data[j].low >>> 0, message.int64Data[j].high >>> 0).toNumber() : message.int64Data[j];
            }
            if (message.name != null && $Object.hasOwnProperty.call(message, "name"))
                object.name = message.name;
            if (message.rawData != null && $Object.hasOwnProperty.call(message, "rawData"))
                object.rawData = options.bytes === $String ? $util.base64.encode(message.rawData, 0, message.rawData.length) : options.bytes === $Array ? $Array.prototype.slice.call(message.rawData) : message.rawData;
            if (message.doubleData && message.doubleData.length) {
                object.doubleData = $Array(message.doubleData.length);
                for (let j = 0; j < message.doubleData.length; ++j)
                    object.doubleData[j] = options.json && !$isFinite(message.doubleData[j]) ? $String(message.doubleData[j]) : message.doubleData[j];
            }
            if (message.uint64Data && message.uint64Data.length) {
                object.uint64Data = $Array(message.uint64Data.length);
                for (let j = 0; j < message.uint64Data.length; ++j)
                    if (typeof $BigInt !== "undefined" && options.longs === $BigInt)
                        object.uint64Data[j] = typeof message.uint64Data[j] === "number" ? $BigInt(message.uint64Data[j]) : $util.Long.fromBits(message.uint64Data[j].low >>> 0, message.uint64Data[j].high >>> 0, true).toBigInt();
                    else if (typeof message.uint64Data[j] === "number")
                        object.uint64Data[j] = options.longs === $String ? $String(message.uint64Data[j]) : message.uint64Data[j];
                    else
                        object.uint64Data[j] = options.longs === $String ? $util.Long.prototype.toString.call(message.uint64Data[j]) : options.longs === $Number ? new $util.LongBits(message.uint64Data[j].low >>> 0, message.uint64Data[j].high >>> 0).toNumber(true) : message.uint64Data[j];
            }
            if (message.docString != null && $Object.hasOwnProperty.call(message, "docString"))
                object.docString = message.docString;
            if (message.externalData && message.externalData.length) {
                object.externalData = $Array(message.externalData.length);
                for (let j = 0; j < message.externalData.length; ++j)
                    object.externalData[j] = $root.onnx.StringStringEntryProto.toObject(message.externalData[j], options, _depth + 1);
            }
            if (message.dataLocation != null && $Object.hasOwnProperty.call(message, "dataLocation"))
                object.dataLocation = options.enums === $String ? $root.onnx.TensorProto.DataLocation[message.dataLocation] === $undefined ? message.dataLocation : $root.onnx.TensorProto.DataLocation[message.dataLocation] : message.dataLocation;
            if (message.metadataProps && message.metadataProps.length) {
                object.metadataProps = $Array(message.metadataProps.length);
                for (let j = 0; j < message.metadataProps.length; ++j)
                    object.metadataProps[j] = $root.onnx.StringStringEntryProto.toObject(message.metadataProps[j], options, _depth + 1);
            }
            return object;
        };

        /**
         * Converts this TensorProto to JSON.
         * @function toJSON
         * @memberof onnx.TensorProto
         * @instance
         * @returns {Object.<string,*>} JSON object
         */
        TensorProto.prototype.toJSON = function() {
            return TensorProto.toObject(this, $protobuf.util.toJSONOptions);
        };

        /**
         * Gets the type url for TensorProto
         * @function getTypeUrl
         * @memberof onnx.TensorProto
         * @static
         * @param {string} [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
         * @returns {string} The type url
         */
        TensorProto.getTypeUrl = function(prefix) {
            if (prefix === $undefined)
                prefix = "type.googleapis.com";
            return prefix + "/onnx.TensorProto";
        };

        /**
         * DataType enum.
         * @name onnx.TensorProto.DataType
         * @enum {number}
         * @property {number} UNDEFINED=0 UNDEFINED value
         * @property {number} FLOAT=1 FLOAT value
         * @property {number} UINT8=2 UINT8 value
         * @property {number} INT8=3 INT8 value
         * @property {number} UINT16=4 UINT16 value
         * @property {number} INT16=5 INT16 value
         * @property {number} INT32=6 INT32 value
         * @property {number} INT64=7 INT64 value
         * @property {number} STRING=8 STRING value
         * @property {number} BOOL=9 BOOL value
         * @property {number} FLOAT16=10 FLOAT16 value
         * @property {number} DOUBLE=11 DOUBLE value
         * @property {number} UINT32=12 UINT32 value
         * @property {number} UINT64=13 UINT64 value
         * @property {number} COMPLEX64=14 COMPLEX64 value
         * @property {number} COMPLEX128=15 COMPLEX128 value
         * @property {number} BFLOAT16=16 BFLOAT16 value
         * @property {number} FLOAT8E4M3FN=17 FLOAT8E4M3FN value
         * @property {number} FLOAT8E4M3FNUZ=18 FLOAT8E4M3FNUZ value
         * @property {number} FLOAT8E5M2=19 FLOAT8E5M2 value
         * @property {number} FLOAT8E5M2FNUZ=20 FLOAT8E5M2FNUZ value
         * @property {number} UINT4=21 UINT4 value
         * @property {number} INT4=22 INT4 value
         */
        TensorProto.DataType = (function() {
            const valuesById = $Object.create(null), values = $Object.create(valuesById);
            values[valuesById[0] = "UNDEFINED"] = 0;
            values[valuesById[1] = "FLOAT"] = 1;
            values[valuesById[2] = "UINT8"] = 2;
            values[valuesById[3] = "INT8"] = 3;
            values[valuesById[4] = "UINT16"] = 4;
            values[valuesById[5] = "INT16"] = 5;
            values[valuesById[6] = "INT32"] = 6;
            values[valuesById[7] = "INT64"] = 7;
            values[valuesById[8] = "STRING"] = 8;
            values[valuesById[9] = "BOOL"] = 9;
            values[valuesById[10] = "FLOAT16"] = 10;
            values[valuesById[11] = "DOUBLE"] = 11;
            values[valuesById[12] = "UINT32"] = 12;
            values[valuesById[13] = "UINT64"] = 13;
            values[valuesById[14] = "COMPLEX64"] = 14;
            values[valuesById[15] = "COMPLEX128"] = 15;
            values[valuesById[16] = "BFLOAT16"] = 16;
            values[valuesById[17] = "FLOAT8E4M3FN"] = 17;
            values[valuesById[18] = "FLOAT8E4M3FNUZ"] = 18;
            values[valuesById[19] = "FLOAT8E5M2"] = 19;
            values[valuesById[20] = "FLOAT8E5M2FNUZ"] = 20;
            values[valuesById[21] = "UINT4"] = 21;
            values[valuesById[22] = "INT4"] = 22;
            return values;
        })();

        TensorProto.Segment = (function() {

            /**
             * Properties of a Segment.
             * @typedef {Object} onnx.TensorProto.Segment.$Properties
             * @property {number|Long|null} [begin] Segment begin
             * @property {number|Long|null} [end] Segment end
             * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding when enabled
             */

            /**
             * Properties of a Segment.
             * @memberof onnx.TensorProto
             * @interface ISegment
             * @augments onnx.TensorProto.Segment.$Properties
             * @deprecated Use onnx.TensorProto.Segment.$Properties instead.
             */

            /**
             * Shape of a Segment.
             * @typedef {onnx.TensorProto.Segment.$Properties} onnx.TensorProto.Segment.$Shape
             */

            /**
             * Constructs a new Segment.
             * @memberof onnx.TensorProto
             * @classdesc Represents a Segment.
             * @constructor
             * @param {onnx.TensorProto.Segment.$Properties=} [properties] Properties to set
             * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding when enabled
             */
            const Segment = function (properties) {
                if (properties)
                    for (let keys = $Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            };

            /**
             * Segment begin.
             * @member {number|Long} begin
             * @memberof onnx.TensorProto.Segment
             * @instance
             */
            Segment.prototype.begin = $util.Long ? $util.Long.fromBits(0,0,false) : 0;

            /**
             * Segment end.
             * @member {number|Long} end
             * @memberof onnx.TensorProto.Segment
             * @instance
             */
            Segment.prototype.end = $util.Long ? $util.Long.fromBits(0,0,false) : 0;

            /**
             * Creates a new Segment instance using the specified properties.
             * @function create
             * @memberof onnx.TensorProto.Segment
             * @static
             * @param {onnx.TensorProto.Segment.$Properties=} [properties] Properties to set
             * @returns {onnx.TensorProto.Segment} Segment instance
             * @type {{
             *   (properties: onnx.TensorProto.Segment.$Shape): onnx.TensorProto.Segment & onnx.TensorProto.Segment.$Shape;
             *   (properties?: onnx.TensorProto.Segment.$Properties): onnx.TensorProto.Segment;
             * }}
             */
            Segment.create = function(properties) {
                return new Segment(properties);
            };

            /**
             * Encodes the specified Segment message. Does not implicitly {@link onnx.TensorProto.Segment.verify|verify} messages.
             * @function encode
             * @memberof onnx.TensorProto.Segment
             * @static
             * @param {onnx.TensorProto.Segment.$Properties} message Segment message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            Segment.encode = function (message, writer, _depth) {
                if (!writer)
                    writer = $Writer.create();
                if (_depth === $undefined)
                    _depth = 0;
                if (_depth > $util.recursionLimit)
                    throw $Error("max depth exceeded");
                if (message.begin != null && $Object.hasOwnProperty.call(message, "begin"))
                    writer.uint32(/* id 1, wireType 0 =*/8).int64(message.begin);
                if (message.end != null && $Object.hasOwnProperty.call(message, "end"))
                    writer.uint32(/* id 2, wireType 0 =*/16).int64(message.end);
                if (message.$unknowns != null && $Object.hasOwnProperty.call(message, "$unknowns"))
                    for (let i = 0; i < message.$unknowns.length; ++i)
                        writer.raw(message.$unknowns[i]);
                return writer;
            };

            /**
             * Encodes the specified Segment message, length delimited. Does not implicitly {@link onnx.TensorProto.Segment.verify|verify} messages.
             * @function encodeDelimited
             * @memberof onnx.TensorProto.Segment
             * @static
             * @param {onnx.TensorProto.Segment.$Properties} message Segment message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            Segment.encodeDelimited = function(message, writer) {
                return this.encode(message, (writer || $Writer.create()).fork()).ldelim();
            };

            /**
             * Decodes a Segment message from the specified reader or buffer.
             * @function decode
             * @memberof onnx.TensorProto.Segment
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {onnx.TensorProto.Segment & onnx.TensorProto.Segment.$Shape} Segment
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            Segment.decode = function (reader, length, _end, _depth, _target) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (_depth === $undefined)
                    _depth = 0;
                if (_depth > $Reader.recursionLimit)
                    throw $Error("max depth exceeded");
                let end = length === $undefined ? reader.len : reader.pos + length, message = _target || new $root.onnx.TensorProto.Segment();
                while (reader.pos < end) {
                    let start = reader.pos;
                    let tag = reader.tag();
                    if (tag === _end) {
                        _end = $undefined;
                        break;
                    }
                    let wireType = tag & 7;
                    switch (tag >>>= 3) {
                    case 1: {
                            if (wireType !== 0)
                                break;
                            message.begin = reader.int64();
                            continue;
                        }
                    case 2: {
                            if (wireType !== 0)
                                break;
                            message.end = reader.int64();
                            continue;
                        }
                    }
                    reader.skipType(wireType, _depth, tag);
                    if (!reader.discardUnknown) {
                        $util.makeProp(message, "$unknowns", false);
                        (message.$unknowns || (message.$unknowns = [])).push(reader.raw(start, reader.pos));
                    }
                }
                if (_end !== $undefined)
                    throw $Error("missing end group");
                return message;
            };

            /**
             * Decodes a Segment message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof onnx.TensorProto.Segment
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {onnx.TensorProto.Segment & onnx.TensorProto.Segment.$Shape} Segment
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            Segment.decodeDelimited = function(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies a Segment message.
             * @function verify
             * @memberof onnx.TensorProto.Segment
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            Segment.verify = function (message, _depth) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (_depth === $undefined)
                    _depth = 0;
                if (_depth > $util.recursionLimit)
                    return "max depth exceeded";
                if (message.begin != null && $Object.hasOwnProperty.call(message, "begin"))
                    if (!$util.isInteger(message.begin) && !(message.begin && $util.isInteger(message.begin.low) && $util.isInteger(message.begin.high)))
                        return "begin: integer|Long expected";
                if (message.end != null && $Object.hasOwnProperty.call(message, "end"))
                    if (!$util.isInteger(message.end) && !(message.end && $util.isInteger(message.end.low) && $util.isInteger(message.end.high)))
                        return "end: integer|Long expected";
                return null;
            };

            /**
             * Creates a Segment message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof onnx.TensorProto.Segment
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {onnx.TensorProto.Segment} Segment
             */
            Segment.fromObject = function (object, _depth) {
                if (object instanceof $root.onnx.TensorProto.Segment)
                    return object;
                if (!$util.isObject(object))
                    throw $TypeError(".onnx.TensorProto.Segment: object expected");
                if (_depth === $undefined)
                    _depth = 0;
                if (_depth > $util.recursionLimit)
                    throw $Error("max depth exceeded");
                let message = new $root.onnx.TensorProto.Segment();
                if (object.begin != null)
                    if ($util.Long)
                        message.begin = $util.Long.fromValue(object.begin, false);
                    else if (typeof object.begin === "string")
                        message.begin = $parseInt(object.begin, 10);
                    else if (typeof object.begin === "number")
                        message.begin = object.begin;
                    else if (typeof object.begin === "object")
                        message.begin = new $util.LongBits(object.begin.low >>> 0, object.begin.high >>> 0).toNumber();
                if (object.end != null)
                    if ($util.Long)
                        message.end = $util.Long.fromValue(object.end, false);
                    else if (typeof object.end === "string")
                        message.end = $parseInt(object.end, 10);
                    else if (typeof object.end === "number")
                        message.end = object.end;
                    else if (typeof object.end === "object")
                        message.end = new $util.LongBits(object.end.low >>> 0, object.end.high >>> 0).toNumber();
                return message;
            };

            /**
             * Creates a plain object from a Segment message. Also converts values to other types if specified.
             * @function toObject
             * @memberof onnx.TensorProto.Segment
             * @static
             * @param {onnx.TensorProto.Segment} message Segment
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            Segment.toObject = function (message, options, _depth) {
                if (!options)
                    options = {};
                if (_depth === $undefined)
                    _depth = 0;
                if (_depth > $util.recursionLimit)
                    throw $Error("max depth exceeded");
                let object = {};
                if (options.defaults) {
                    if ($util.Long) {
                        let long = new $util.Long(0, 0, false);
                        object.begin = options.longs === $String ? long.toString() : options.longs === $Number ? long.toNumber() : typeof $BigInt !== "undefined" && options.longs === $BigInt ? long.toBigInt() : long;
                    } else
                        object.begin = options.longs === $String ? "0" : typeof $BigInt !== "undefined" && options.longs === $BigInt ? $BigInt("0") : 0;
                    if ($util.Long) {
                        let long = new $util.Long(0, 0, false);
                        object.end = options.longs === $String ? long.toString() : options.longs === $Number ? long.toNumber() : typeof $BigInt !== "undefined" && options.longs === $BigInt ? long.toBigInt() : long;
                    } else
                        object.end = options.longs === $String ? "0" : typeof $BigInt !== "undefined" && options.longs === $BigInt ? $BigInt("0") : 0;
                }
                if (message.begin != null && $Object.hasOwnProperty.call(message, "begin"))
                    if (typeof $BigInt !== "undefined" && options.longs === $BigInt)
                        object.begin = typeof message.begin === "number" ? $BigInt(message.begin) : $util.Long.fromBits(message.begin.low >>> 0, message.begin.high >>> 0, false).toBigInt();
                    else if (typeof message.begin === "number")
                        object.begin = options.longs === $String ? $String(message.begin) : message.begin;
                    else
                        object.begin = options.longs === $String ? $util.Long.prototype.toString.call(message.begin) : options.longs === $Number ? new $util.LongBits(message.begin.low >>> 0, message.begin.high >>> 0).toNumber() : message.begin;
                if (message.end != null && $Object.hasOwnProperty.call(message, "end"))
                    if (typeof $BigInt !== "undefined" && options.longs === $BigInt)
                        object.end = typeof message.end === "number" ? $BigInt(message.end) : $util.Long.fromBits(message.end.low >>> 0, message.end.high >>> 0, false).toBigInt();
                    else if (typeof message.end === "number")
                        object.end = options.longs === $String ? $String(message.end) : message.end;
                    else
                        object.end = options.longs === $String ? $util.Long.prototype.toString.call(message.end) : options.longs === $Number ? new $util.LongBits(message.end.low >>> 0, message.end.high >>> 0).toNumber() : message.end;
                return object;
            };

            /**
             * Converts this Segment to JSON.
             * @function toJSON
             * @memberof onnx.TensorProto.Segment
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            Segment.prototype.toJSON = function() {
                return Segment.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the type url for Segment
             * @function getTypeUrl
             * @memberof onnx.TensorProto.Segment
             * @static
             * @param {string} [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
             * @returns {string} The type url
             */
            Segment.getTypeUrl = function(prefix) {
                if (prefix === $undefined)
                    prefix = "type.googleapis.com";
                return prefix + "/onnx.TensorProto.Segment";
            };

            return Segment;
        })();

        /**
         * DataLocation enum.
         * @name onnx.TensorProto.DataLocation
         * @enum {number}
         * @property {number} DEFAULT=0 DEFAULT value
         * @property {number} EXTERNAL=1 EXTERNAL value
         */
        TensorProto.DataLocation = (function() {
            const valuesById = $Object.create(null), values = $Object.create(valuesById);
            values[valuesById[0] = "DEFAULT"] = 0;
            values[valuesById[1] = "EXTERNAL"] = 1;
            return values;
        })();

        return TensorProto;
    })();

    onnx.SparseTensorProto = (function() {

        /**
         * Properties of a SparseTensorProto.
         * @typedef {Object} onnx.SparseTensorProto.$Properties
         * @property {onnx.TensorProto.$Properties|null} [values] SparseTensorProto values
         * @property {onnx.TensorProto.$Properties|null} [indices] SparseTensorProto indices
         * @property {Array.<number|Long>|null} [dims] SparseTensorProto dims
         * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding when enabled
         */

        /**
         * Properties of a SparseTensorProto.
         * @memberof onnx
         * @interface ISparseTensorProto
         * @augments onnx.SparseTensorProto.$Properties
         * @deprecated Use onnx.SparseTensorProto.$Properties instead.
         */

        /**
         * Shape of a SparseTensorProto.
         * @typedef {onnx.SparseTensorProto.$Properties} onnx.SparseTensorProto.$Shape
         */

        /**
         * Constructs a new SparseTensorProto.
         * @memberof onnx
         * @classdesc Represents a SparseTensorProto.
         * @constructor
         * @param {onnx.SparseTensorProto.$Properties=} [properties] Properties to set
         * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding when enabled
         */
        const SparseTensorProto = function (properties) {
            this.dims = [];
            if (properties)
                for (let keys = $Object.keys(properties), i = 0; i < keys.length; ++i)
                    if (properties[keys[i]] != null && keys[i] !== "__proto__")
                        this[keys[i]] = properties[keys[i]];
        };

        /**
         * SparseTensorProto values.
         * @member {onnx.TensorProto.$Properties|null|undefined} values
         * @memberof onnx.SparseTensorProto
         * @instance
         */
        SparseTensorProto.prototype.values = null;

        /**
         * SparseTensorProto indices.
         * @member {onnx.TensorProto.$Properties|null|undefined} indices
         * @memberof onnx.SparseTensorProto
         * @instance
         */
        SparseTensorProto.prototype.indices = null;

        /**
         * SparseTensorProto dims.
         * @member {Array.<number|Long>} dims
         * @memberof onnx.SparseTensorProto
         * @instance
         */
        SparseTensorProto.prototype.dims = $util.emptyArray;

        /**
         * Creates a new SparseTensorProto instance using the specified properties.
         * @function create
         * @memberof onnx.SparseTensorProto
         * @static
         * @param {onnx.SparseTensorProto.$Properties=} [properties] Properties to set
         * @returns {onnx.SparseTensorProto} SparseTensorProto instance
         * @type {{
         *   (properties: onnx.SparseTensorProto.$Shape): onnx.SparseTensorProto & onnx.SparseTensorProto.$Shape;
         *   (properties?: onnx.SparseTensorProto.$Properties): onnx.SparseTensorProto;
         * }}
         */
        SparseTensorProto.create = function(properties) {
            return new SparseTensorProto(properties);
        };

        /**
         * Encodes the specified SparseTensorProto message. Does not implicitly {@link onnx.SparseTensorProto.verify|verify} messages.
         * @function encode
         * @memberof onnx.SparseTensorProto
         * @static
         * @param {onnx.SparseTensorProto.$Properties} message SparseTensorProto message or plain object to encode
         * @param {$protobuf.Writer} [writer] Writer to encode to
         * @returns {$protobuf.Writer} Writer
         */
        SparseTensorProto.encode = function (message, writer, _depth) {
            if (!writer)
                writer = $Writer.create();
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                throw $Error("max depth exceeded");
            if (message.values != null && $Object.hasOwnProperty.call(message, "values"))
                $root.onnx.TensorProto.encode(message.values, writer.uint32(/* id 1, wireType 2 =*/10).fork(), _depth + 1).ldelim();
            if (message.indices != null && $Object.hasOwnProperty.call(message, "indices"))
                $root.onnx.TensorProto.encode(message.indices, writer.uint32(/* id 2, wireType 2 =*/18).fork(), _depth + 1).ldelim();
            if (message.dims != null && message.dims.length)
                for (let i = 0; i < message.dims.length; ++i)
                    writer.uint32(/* id 3, wireType 0 =*/24).int64(message.dims[i]);
            if (message.$unknowns != null && $Object.hasOwnProperty.call(message, "$unknowns"))
                for (let i = 0; i < message.$unknowns.length; ++i)
                    writer.raw(message.$unknowns[i]);
            return writer;
        };

        /**
         * Encodes the specified SparseTensorProto message, length delimited. Does not implicitly {@link onnx.SparseTensorProto.verify|verify} messages.
         * @function encodeDelimited
         * @memberof onnx.SparseTensorProto
         * @static
         * @param {onnx.SparseTensorProto.$Properties} message SparseTensorProto message or plain object to encode
         * @param {$protobuf.Writer} [writer] Writer to encode to
         * @returns {$protobuf.Writer} Writer
         */
        SparseTensorProto.encodeDelimited = function(message, writer) {
            return this.encode(message, (writer || $Writer.create()).fork()).ldelim();
        };

        /**
         * Decodes a SparseTensorProto message from the specified reader or buffer.
         * @function decode
         * @memberof onnx.SparseTensorProto
         * @static
         * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
         * @param {number} [length] Message length if known beforehand
         * @returns {onnx.SparseTensorProto & onnx.SparseTensorProto.$Shape} SparseTensorProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        SparseTensorProto.decode = function (reader, length, _end, _depth, _target) {
            if (!(reader instanceof $Reader))
                reader = $Reader.create(reader);
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $Reader.recursionLimit)
                throw $Error("max depth exceeded");
            let end = length === $undefined ? reader.len : reader.pos + length, message = _target || new $root.onnx.SparseTensorProto();
            while (reader.pos < end) {
                let start = reader.pos;
                let tag = reader.tag();
                if (tag === _end) {
                    _end = $undefined;
                    break;
                }
                let wireType = tag & 7;
                switch (tag >>>= 3) {
                case 1: {
                        if (wireType !== 2)
                            break;
                        message.values = $root.onnx.TensorProto.decode(reader, reader.uint32(), $undefined, _depth + 1, message.values);
                        continue;
                    }
                case 2: {
                        if (wireType !== 2)
                            break;
                        message.indices = $root.onnx.TensorProto.decode(reader, reader.uint32(), $undefined, _depth + 1, message.indices);
                        continue;
                    }
                case 3: {
                        if (wireType === 2) {
                            if (!(message.dims && message.dims.length))
                                message.dims = [];
                            reader.int64s(message.dims);
                            continue;
                        }
                        if (wireType !== 0)
                            break;
                        if (!(message.dims && message.dims.length))
                            message.dims = [];
                        message.dims.push(reader.int64());
                        continue;
                    }
                }
                reader.skipType(wireType, _depth, tag);
                if (!reader.discardUnknown) {
                    $util.makeProp(message, "$unknowns", false);
                    (message.$unknowns || (message.$unknowns = [])).push(reader.raw(start, reader.pos));
                }
            }
            if (_end !== $undefined)
                throw $Error("missing end group");
            return message;
        };

        /**
         * Decodes a SparseTensorProto message from the specified reader or buffer, length delimited.
         * @function decodeDelimited
         * @memberof onnx.SparseTensorProto
         * @static
         * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
         * @returns {onnx.SparseTensorProto & onnx.SparseTensorProto.$Shape} SparseTensorProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        SparseTensorProto.decodeDelimited = function(reader) {
            if (!(reader instanceof $Reader))
                reader = new $Reader(reader);
            return this.decode(reader, reader.uint32());
        };

        /**
         * Verifies a SparseTensorProto message.
         * @function verify
         * @memberof onnx.SparseTensorProto
         * @static
         * @param {Object.<string,*>} message Plain object to verify
         * @returns {string|null} `null` if valid, otherwise the reason why it is not
         */
        SparseTensorProto.verify = function (message, _depth) {
            if (typeof message !== "object" || message === null)
                return "object expected";
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                return "max depth exceeded";
            if (message.values != null && $Object.hasOwnProperty.call(message, "values")) {
                let error = $root.onnx.TensorProto.verify(message.values, _depth + 1);
                if (error)
                    return "values." + error;
            }
            if (message.indices != null && $Object.hasOwnProperty.call(message, "indices")) {
                let error = $root.onnx.TensorProto.verify(message.indices, _depth + 1);
                if (error)
                    return "indices." + error;
            }
            if (message.dims != null && $Object.hasOwnProperty.call(message, "dims")) {
                if (!$Array.isArray(message.dims))
                    return "dims: array expected";
                for (let i = 0; i < message.dims.length; ++i)
                    if (!$util.isInteger(message.dims[i]) && !(message.dims[i] && $util.isInteger(message.dims[i].low) && $util.isInteger(message.dims[i].high)))
                        return "dims: integer|Long[] expected";
            }
            return null;
        };

        /**
         * Creates a SparseTensorProto message from a plain object. Also converts values to their respective internal types.
         * @function fromObject
         * @memberof onnx.SparseTensorProto
         * @static
         * @param {Object.<string,*>} object Plain object
         * @returns {onnx.SparseTensorProto} SparseTensorProto
         */
        SparseTensorProto.fromObject = function (object, _depth) {
            if (object instanceof $root.onnx.SparseTensorProto)
                return object;
            if (!$util.isObject(object))
                throw $TypeError(".onnx.SparseTensorProto: object expected");
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                throw $Error("max depth exceeded");
            let message = new $root.onnx.SparseTensorProto();
            if (object.values != null) {
                if (!$util.isObject(object.values))
                    throw $TypeError(".onnx.SparseTensorProto.values: object expected");
                message.values = $root.onnx.TensorProto.fromObject(object.values, _depth + 1);
            }
            if (object.indices != null) {
                if (!$util.isObject(object.indices))
                    throw $TypeError(".onnx.SparseTensorProto.indices: object expected");
                message.indices = $root.onnx.TensorProto.fromObject(object.indices, _depth + 1);
            }
            if (object.dims) {
                if (!$Array.isArray(object.dims))
                    throw $TypeError(".onnx.SparseTensorProto.dims: array expected");
                message.dims = $Array(object.dims.length);
                for (let i = 0; i < object.dims.length; ++i)
                    if ($util.Long)
                        message.dims[i] = $util.Long.fromValue(object.dims[i], false);
                    else if (typeof object.dims[i] === "string")
                        message.dims[i] = $parseInt(object.dims[i], 10);
                    else if (typeof object.dims[i] === "number")
                        message.dims[i] = object.dims[i];
                    else if (typeof object.dims[i] === "object")
                        message.dims[i] = new $util.LongBits(object.dims[i].low >>> 0, object.dims[i].high >>> 0).toNumber();
            }
            return message;
        };

        /**
         * Creates a plain object from a SparseTensorProto message. Also converts values to other types if specified.
         * @function toObject
         * @memberof onnx.SparseTensorProto
         * @static
         * @param {onnx.SparseTensorProto} message SparseTensorProto
         * @param {$protobuf.IConversionOptions} [options] Conversion options
         * @returns {Object.<string,*>} Plain object
         */
        SparseTensorProto.toObject = function (message, options, _depth) {
            if (!options)
                options = {};
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                throw $Error("max depth exceeded");
            let object = {};
            if (options.arrays || options.defaults)
                object.dims = [];
            if (options.defaults) {
                object.values = null;
                object.indices = null;
            }
            if (message.values != null && $Object.hasOwnProperty.call(message, "values"))
                object.values = $root.onnx.TensorProto.toObject(message.values, options, _depth + 1);
            if (message.indices != null && $Object.hasOwnProperty.call(message, "indices"))
                object.indices = $root.onnx.TensorProto.toObject(message.indices, options, _depth + 1);
            if (message.dims && message.dims.length) {
                object.dims = $Array(message.dims.length);
                for (let j = 0; j < message.dims.length; ++j)
                    if (typeof $BigInt !== "undefined" && options.longs === $BigInt)
                        object.dims[j] = typeof message.dims[j] === "number" ? $BigInt(message.dims[j]) : $util.Long.fromBits(message.dims[j].low >>> 0, message.dims[j].high >>> 0, false).toBigInt();
                    else if (typeof message.dims[j] === "number")
                        object.dims[j] = options.longs === $String ? $String(message.dims[j]) : message.dims[j];
                    else
                        object.dims[j] = options.longs === $String ? $util.Long.prototype.toString.call(message.dims[j]) : options.longs === $Number ? new $util.LongBits(message.dims[j].low >>> 0, message.dims[j].high >>> 0).toNumber() : message.dims[j];
            }
            return object;
        };

        /**
         * Converts this SparseTensorProto to JSON.
         * @function toJSON
         * @memberof onnx.SparseTensorProto
         * @instance
         * @returns {Object.<string,*>} JSON object
         */
        SparseTensorProto.prototype.toJSON = function() {
            return SparseTensorProto.toObject(this, $protobuf.util.toJSONOptions);
        };

        /**
         * Gets the type url for SparseTensorProto
         * @function getTypeUrl
         * @memberof onnx.SparseTensorProto
         * @static
         * @param {string} [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
         * @returns {string} The type url
         */
        SparseTensorProto.getTypeUrl = function(prefix) {
            if (prefix === $undefined)
                prefix = "type.googleapis.com";
            return prefix + "/onnx.SparseTensorProto";
        };

        return SparseTensorProto;
    })();

    onnx.TensorShapeProto = (function() {

        /**
         * Properties of a TensorShapeProto.
         * @typedef {Object} onnx.TensorShapeProto.$Properties
         * @property {Array.<onnx.TensorShapeProto.Dimension.$Properties>|null} [dim] TensorShapeProto dim
         * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding when enabled
         */

        /**
         * Properties of a TensorShapeProto.
         * @memberof onnx
         * @interface ITensorShapeProto
         * @augments onnx.TensorShapeProto.$Properties
         * @deprecated Use onnx.TensorShapeProto.$Properties instead.
         */

        /**
         * Shape of a TensorShapeProto.
         * @typedef {{
         *   dim?: Array.<onnx.TensorShapeProto.Dimension.$Shape>|null;
         *   $unknowns?: Array.<Uint8Array>;
         * }} onnx.TensorShapeProto.$Shape
         */

        /**
         * Constructs a new TensorShapeProto.
         * @memberof onnx
         * @classdesc Represents a TensorShapeProto.
         * @constructor
         * @param {onnx.TensorShapeProto.$Properties=} [properties] Properties to set
         * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding when enabled
         */
        const TensorShapeProto = function (properties) {
            this.dim = [];
            if (properties)
                for (let keys = $Object.keys(properties), i = 0; i < keys.length; ++i)
                    if (properties[keys[i]] != null && keys[i] !== "__proto__")
                        this[keys[i]] = properties[keys[i]];
        };

        /**
         * TensorShapeProto dim.
         * @member {Array.<onnx.TensorShapeProto.Dimension.$Properties>} dim
         * @memberof onnx.TensorShapeProto
         * @instance
         */
        TensorShapeProto.prototype.dim = $util.emptyArray;

        /**
         * Creates a new TensorShapeProto instance using the specified properties.
         * @function create
         * @memberof onnx.TensorShapeProto
         * @static
         * @param {onnx.TensorShapeProto.$Properties=} [properties] Properties to set
         * @returns {onnx.TensorShapeProto} TensorShapeProto instance
         * @type {{
         *   (properties: onnx.TensorShapeProto.$Shape): onnx.TensorShapeProto & onnx.TensorShapeProto.$Shape;
         *   (properties?: onnx.TensorShapeProto.$Properties): onnx.TensorShapeProto;
         * }}
         */
        TensorShapeProto.create = function(properties) {
            return new TensorShapeProto(properties);
        };

        /**
         * Encodes the specified TensorShapeProto message. Does not implicitly {@link onnx.TensorShapeProto.verify|verify} messages.
         * @function encode
         * @memberof onnx.TensorShapeProto
         * @static
         * @param {onnx.TensorShapeProto.$Properties} message TensorShapeProto message or plain object to encode
         * @param {$protobuf.Writer} [writer] Writer to encode to
         * @returns {$protobuf.Writer} Writer
         */
        TensorShapeProto.encode = function (message, writer, _depth) {
            if (!writer)
                writer = $Writer.create();
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                throw $Error("max depth exceeded");
            if (message.dim != null && message.dim.length)
                for (let i = 0; i < message.dim.length; ++i)
                    $root.onnx.TensorShapeProto.Dimension.encode(message.dim[i], writer.uint32(/* id 1, wireType 2 =*/10).fork(), _depth + 1).ldelim();
            if (message.$unknowns != null && $Object.hasOwnProperty.call(message, "$unknowns"))
                for (let i = 0; i < message.$unknowns.length; ++i)
                    writer.raw(message.$unknowns[i]);
            return writer;
        };

        /**
         * Encodes the specified TensorShapeProto message, length delimited. Does not implicitly {@link onnx.TensorShapeProto.verify|verify} messages.
         * @function encodeDelimited
         * @memberof onnx.TensorShapeProto
         * @static
         * @param {onnx.TensorShapeProto.$Properties} message TensorShapeProto message or plain object to encode
         * @param {$protobuf.Writer} [writer] Writer to encode to
         * @returns {$protobuf.Writer} Writer
         */
        TensorShapeProto.encodeDelimited = function(message, writer) {
            return this.encode(message, (writer || $Writer.create()).fork()).ldelim();
        };

        /**
         * Decodes a TensorShapeProto message from the specified reader or buffer.
         * @function decode
         * @memberof onnx.TensorShapeProto
         * @static
         * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
         * @param {number} [length] Message length if known beforehand
         * @returns {onnx.TensorShapeProto & onnx.TensorShapeProto.$Shape} TensorShapeProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        TensorShapeProto.decode = function (reader, length, _end, _depth, _target) {
            if (!(reader instanceof $Reader))
                reader = $Reader.create(reader);
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $Reader.recursionLimit)
                throw $Error("max depth exceeded");
            let end = length === $undefined ? reader.len : reader.pos + length, message = _target || new $root.onnx.TensorShapeProto();
            while (reader.pos < end) {
                let start = reader.pos;
                let tag = reader.tag();
                if (tag === _end) {
                    _end = $undefined;
                    break;
                }
                let wireType = tag & 7;
                switch (tag >>>= 3) {
                case 1: {
                        if (wireType !== 2)
                            break;
                        if (!(message.dim && message.dim.length))
                            message.dim = [];
                        message.dim.push($root.onnx.TensorShapeProto.Dimension.decode(reader, reader.uint32(), $undefined, _depth + 1));
                        continue;
                    }
                }
                reader.skipType(wireType, _depth, tag);
                if (!reader.discardUnknown) {
                    $util.makeProp(message, "$unknowns", false);
                    (message.$unknowns || (message.$unknowns = [])).push(reader.raw(start, reader.pos));
                }
            }
            if (_end !== $undefined)
                throw $Error("missing end group");
            return message;
        };

        /**
         * Decodes a TensorShapeProto message from the specified reader or buffer, length delimited.
         * @function decodeDelimited
         * @memberof onnx.TensorShapeProto
         * @static
         * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
         * @returns {onnx.TensorShapeProto & onnx.TensorShapeProto.$Shape} TensorShapeProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        TensorShapeProto.decodeDelimited = function(reader) {
            if (!(reader instanceof $Reader))
                reader = new $Reader(reader);
            return this.decode(reader, reader.uint32());
        };

        /**
         * Verifies a TensorShapeProto message.
         * @function verify
         * @memberof onnx.TensorShapeProto
         * @static
         * @param {Object.<string,*>} message Plain object to verify
         * @returns {string|null} `null` if valid, otherwise the reason why it is not
         */
        TensorShapeProto.verify = function (message, _depth) {
            if (typeof message !== "object" || message === null)
                return "object expected";
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                return "max depth exceeded";
            if (message.dim != null && $Object.hasOwnProperty.call(message, "dim")) {
                if (!$Array.isArray(message.dim))
                    return "dim: array expected";
                for (let i = 0; i < message.dim.length; ++i) {
                    let error = $root.onnx.TensorShapeProto.Dimension.verify(message.dim[i], _depth + 1);
                    if (error)
                        return "dim." + error;
                }
            }
            return null;
        };

        /**
         * Creates a TensorShapeProto message from a plain object. Also converts values to their respective internal types.
         * @function fromObject
         * @memberof onnx.TensorShapeProto
         * @static
         * @param {Object.<string,*>} object Plain object
         * @returns {onnx.TensorShapeProto} TensorShapeProto
         */
        TensorShapeProto.fromObject = function (object, _depth) {
            if (object instanceof $root.onnx.TensorShapeProto)
                return object;
            if (!$util.isObject(object))
                throw $TypeError(".onnx.TensorShapeProto: object expected");
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                throw $Error("max depth exceeded");
            let message = new $root.onnx.TensorShapeProto();
            if (object.dim) {
                if (!$Array.isArray(object.dim))
                    throw $TypeError(".onnx.TensorShapeProto.dim: array expected");
                message.dim = $Array(object.dim.length);
                for (let i = 0; i < object.dim.length; ++i) {
                    if (!$util.isObject(object.dim[i]))
                        throw $TypeError(".onnx.TensorShapeProto.dim: object expected");
                    message.dim[i] = $root.onnx.TensorShapeProto.Dimension.fromObject(object.dim[i], _depth + 1);
                }
            }
            return message;
        };

        /**
         * Creates a plain object from a TensorShapeProto message. Also converts values to other types if specified.
         * @function toObject
         * @memberof onnx.TensorShapeProto
         * @static
         * @param {onnx.TensorShapeProto} message TensorShapeProto
         * @param {$protobuf.IConversionOptions} [options] Conversion options
         * @returns {Object.<string,*>} Plain object
         */
        TensorShapeProto.toObject = function (message, options, _depth) {
            if (!options)
                options = {};
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                throw $Error("max depth exceeded");
            let object = {};
            if (options.arrays || options.defaults)
                object.dim = [];
            if (message.dim && message.dim.length) {
                object.dim = $Array(message.dim.length);
                for (let j = 0; j < message.dim.length; ++j)
                    object.dim[j] = $root.onnx.TensorShapeProto.Dimension.toObject(message.dim[j], options, _depth + 1);
            }
            return object;
        };

        /**
         * Converts this TensorShapeProto to JSON.
         * @function toJSON
         * @memberof onnx.TensorShapeProto
         * @instance
         * @returns {Object.<string,*>} JSON object
         */
        TensorShapeProto.prototype.toJSON = function() {
            return TensorShapeProto.toObject(this, $protobuf.util.toJSONOptions);
        };

        /**
         * Gets the type url for TensorShapeProto
         * @function getTypeUrl
         * @memberof onnx.TensorShapeProto
         * @static
         * @param {string} [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
         * @returns {string} The type url
         */
        TensorShapeProto.getTypeUrl = function(prefix) {
            if (prefix === $undefined)
                prefix = "type.googleapis.com";
            return prefix + "/onnx.TensorShapeProto";
        };

        TensorShapeProto.Dimension = (function() {

            /**
             * Properties of a Dimension.
             * @typedef {Object} onnx.TensorShapeProto.Dimension.$Properties
             * @property {number|Long|null} [dimValue] Dimension dimValue
             * @property {string|null} [dimParam] Dimension dimParam
             * @property {string|null} [denotation] Dimension denotation
             * @property {"dimValue"|"dimParam"} [value] Dimension value
             * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding when enabled
             */

            /**
             * Properties of a Dimension.
             * @memberof onnx.TensorShapeProto
             * @interface IDimension
             * @augments onnx.TensorShapeProto.Dimension.$Properties
             * @deprecated Use onnx.TensorShapeProto.Dimension.$Properties instead.
             */

            /**
             * Narrowed shape of a Dimension.
             * @typedef {{
             *   dimValue?: number|Long|null;
             *   dimParam?: string|null;
             *   denotation?: string|null;
             *   $unknowns?: Array.<Uint8Array>;
             * } & (
             *   ({ value?: undefined; dimValue?: null; dimParam?: null }|{ value?: "dimValue"; dimValue: number|Long; dimParam?: null }|{ value?: "dimParam"; dimValue?: null; dimParam: string })
             * )} onnx.TensorShapeProto.Dimension.$Shape
             */

            /**
             * Constructs a new Dimension.
             * @memberof onnx.TensorShapeProto
             * @classdesc Represents a Dimension.
             * @constructor
             * @param {onnx.TensorShapeProto.Dimension.$Properties=} [properties] Properties to set
             * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding when enabled
             */
            const Dimension = function (properties) {
                if (properties)
                    for (let keys = $Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            };

            /**
             * Dimension dimValue.
             * @member {number|Long|null|undefined} dimValue
             * @memberof onnx.TensorShapeProto.Dimension
             * @instance
             */
            Dimension.prototype.dimValue = null;

            /**
             * Dimension dimParam.
             * @member {string|null|undefined} dimParam
             * @memberof onnx.TensorShapeProto.Dimension
             * @instance
             */
            Dimension.prototype.dimParam = null;

            /**
             * Dimension denotation.
             * @member {string} denotation
             * @memberof onnx.TensorShapeProto.Dimension
             * @instance
             */
            Dimension.prototype.denotation = "";

            // OneOf field names bound to virtual getters and setters
            let $oneOfFields;

            /**
             * Dimension value.
             * @member {"dimValue"|"dimParam"|undefined} value
             * @memberof onnx.TensorShapeProto.Dimension
             * @instance
             */
            $Object.defineProperty(Dimension.prototype, "value", {
                get: $util.oneOfGetter($oneOfFields = ["dimValue", "dimParam"]),
                set: $util.oneOfSetter($oneOfFields)
            });

            /**
             * Creates a new Dimension instance using the specified properties.
             * @function create
             * @memberof onnx.TensorShapeProto.Dimension
             * @static
             * @param {onnx.TensorShapeProto.Dimension.$Properties=} [properties] Properties to set
             * @returns {onnx.TensorShapeProto.Dimension} Dimension instance
             * @type {{
             *   (properties: onnx.TensorShapeProto.Dimension.$Shape): onnx.TensorShapeProto.Dimension & onnx.TensorShapeProto.Dimension.$Shape;
             *   (properties?: onnx.TensorShapeProto.Dimension.$Properties): onnx.TensorShapeProto.Dimension;
             * }}
             */
            Dimension.create = function(properties) {
                return new Dimension(properties);
            };

            /**
             * Encodes the specified Dimension message. Does not implicitly {@link onnx.TensorShapeProto.Dimension.verify|verify} messages.
             * @function encode
             * @memberof onnx.TensorShapeProto.Dimension
             * @static
             * @param {onnx.TensorShapeProto.Dimension.$Properties} message Dimension message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            Dimension.encode = function (message, writer, _depth) {
                if (!writer)
                    writer = $Writer.create();
                if (_depth === $undefined)
                    _depth = 0;
                if (_depth > $util.recursionLimit)
                    throw $Error("max depth exceeded");
                if (message.dimValue != null && $Object.hasOwnProperty.call(message, "dimValue"))
                    writer.uint32(/* id 1, wireType 0 =*/8).int64(message.dimValue);
                if (message.dimParam != null && $Object.hasOwnProperty.call(message, "dimParam"))
                    writer.uint32(/* id 2, wireType 2 =*/18).string(message.dimParam);
                if (message.denotation != null && $Object.hasOwnProperty.call(message, "denotation"))
                    writer.uint32(/* id 3, wireType 2 =*/26).string(message.denotation);
                if (message.$unknowns != null && $Object.hasOwnProperty.call(message, "$unknowns"))
                    for (let i = 0; i < message.$unknowns.length; ++i)
                        writer.raw(message.$unknowns[i]);
                return writer;
            };

            /**
             * Encodes the specified Dimension message, length delimited. Does not implicitly {@link onnx.TensorShapeProto.Dimension.verify|verify} messages.
             * @function encodeDelimited
             * @memberof onnx.TensorShapeProto.Dimension
             * @static
             * @param {onnx.TensorShapeProto.Dimension.$Properties} message Dimension message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            Dimension.encodeDelimited = function(message, writer) {
                return this.encode(message, (writer || $Writer.create()).fork()).ldelim();
            };

            /**
             * Decodes a Dimension message from the specified reader or buffer.
             * @function decode
             * @memberof onnx.TensorShapeProto.Dimension
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {onnx.TensorShapeProto.Dimension & onnx.TensorShapeProto.Dimension.$Shape} Dimension
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            Dimension.decode = function (reader, length, _end, _depth, _target) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (_depth === $undefined)
                    _depth = 0;
                if (_depth > $Reader.recursionLimit)
                    throw $Error("max depth exceeded");
                let end = length === $undefined ? reader.len : reader.pos + length, message = _target || new $root.onnx.TensorShapeProto.Dimension();
                while (reader.pos < end) {
                    let start = reader.pos;
                    let tag = reader.tag();
                    if (tag === _end) {
                        _end = $undefined;
                        break;
                    }
                    let wireType = tag & 7;
                    switch (tag >>>= 3) {
                    case 1: {
                            if (wireType !== 0)
                                break;
                            message.dimValue = reader.int64();
                            message.value = "dimValue";
                            continue;
                        }
                    case 2: {
                            if (wireType !== 2)
                                break;
                            message.dimParam = reader.string();
                            message.value = "dimParam";
                            continue;
                        }
                    case 3: {
                            if (wireType !== 2)
                                break;
                            message.denotation = reader.string();
                            continue;
                        }
                    }
                    reader.skipType(wireType, _depth, tag);
                    if (!reader.discardUnknown) {
                        $util.makeProp(message, "$unknowns", false);
                        (message.$unknowns || (message.$unknowns = [])).push(reader.raw(start, reader.pos));
                    }
                }
                if (_end !== $undefined)
                    throw $Error("missing end group");
                return message;
            };

            /**
             * Decodes a Dimension message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof onnx.TensorShapeProto.Dimension
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {onnx.TensorShapeProto.Dimension & onnx.TensorShapeProto.Dimension.$Shape} Dimension
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            Dimension.decodeDelimited = function(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies a Dimension message.
             * @function verify
             * @memberof onnx.TensorShapeProto.Dimension
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            Dimension.verify = function (message, _depth) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (_depth === $undefined)
                    _depth = 0;
                if (_depth > $util.recursionLimit)
                    return "max depth exceeded";
                let properties = {};
                if (message.dimValue != null && $Object.hasOwnProperty.call(message, "dimValue")) {
                    properties.value = 1;
                    if (!$util.isInteger(message.dimValue) && !(message.dimValue && $util.isInteger(message.dimValue.low) && $util.isInteger(message.dimValue.high)))
                        return "dimValue: integer|Long expected";
                }
                if (message.dimParam != null && $Object.hasOwnProperty.call(message, "dimParam")) {
                    if (properties.value === 1)
                        return "value: multiple values";
                    properties.value = 1;
                    if (!$util.isString(message.dimParam))
                        return "dimParam: string expected";
                }
                if (message.denotation != null && $Object.hasOwnProperty.call(message, "denotation"))
                    if (!$util.isString(message.denotation))
                        return "denotation: string expected";
                return null;
            };

            /**
             * Creates a Dimension message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof onnx.TensorShapeProto.Dimension
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {onnx.TensorShapeProto.Dimension} Dimension
             */
            Dimension.fromObject = function (object, _depth) {
                if (object instanceof $root.onnx.TensorShapeProto.Dimension)
                    return object;
                if (!$util.isObject(object))
                    throw $TypeError(".onnx.TensorShapeProto.Dimension: object expected");
                if (_depth === $undefined)
                    _depth = 0;
                if (_depth > $util.recursionLimit)
                    throw $Error("max depth exceeded");
                let message = new $root.onnx.TensorShapeProto.Dimension();
                if (object.dimValue != null)
                    if ($util.Long)
                        message.dimValue = $util.Long.fromValue(object.dimValue, false);
                    else if (typeof object.dimValue === "string")
                        message.dimValue = $parseInt(object.dimValue, 10);
                    else if (typeof object.dimValue === "number")
                        message.dimValue = object.dimValue;
                    else if (typeof object.dimValue === "object")
                        message.dimValue = new $util.LongBits(object.dimValue.low >>> 0, object.dimValue.high >>> 0).toNumber();
                if (object.dimParam != null)
                    message.dimParam = $String(object.dimParam);
                if (object.denotation != null)
                    message.denotation = $String(object.denotation);
                return message;
            };

            /**
             * Creates a plain object from a Dimension message. Also converts values to other types if specified.
             * @function toObject
             * @memberof onnx.TensorShapeProto.Dimension
             * @static
             * @param {onnx.TensorShapeProto.Dimension} message Dimension
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            Dimension.toObject = function (message, options, _depth) {
                if (!options)
                    options = {};
                if (_depth === $undefined)
                    _depth = 0;
                if (_depth > $util.recursionLimit)
                    throw $Error("max depth exceeded");
                let object = {};
                if (options.defaults)
                    object.denotation = "";
                if (message.dimValue != null && $Object.hasOwnProperty.call(message, "dimValue")) {
                    if (typeof $BigInt !== "undefined" && options.longs === $BigInt)
                        object.dimValue = typeof message.dimValue === "number" ? $BigInt(message.dimValue) : $util.Long.fromBits(message.dimValue.low >>> 0, message.dimValue.high >>> 0, false).toBigInt();
                    else if (typeof message.dimValue === "number")
                        object.dimValue = options.longs === $String ? $String(message.dimValue) : message.dimValue;
                    else
                        object.dimValue = options.longs === $String ? $util.Long.prototype.toString.call(message.dimValue) : options.longs === $Number ? new $util.LongBits(message.dimValue.low >>> 0, message.dimValue.high >>> 0).toNumber() : message.dimValue;
                    if (options.oneofs)
                        object.value = "dimValue";
                }
                if (message.dimParam != null && $Object.hasOwnProperty.call(message, "dimParam")) {
                    object.dimParam = message.dimParam;
                    if (options.oneofs)
                        object.value = "dimParam";
                }
                if (message.denotation != null && $Object.hasOwnProperty.call(message, "denotation"))
                    object.denotation = message.denotation;
                return object;
            };

            /**
             * Converts this Dimension to JSON.
             * @function toJSON
             * @memberof onnx.TensorShapeProto.Dimension
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            Dimension.prototype.toJSON = function() {
                return Dimension.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the type url for Dimension
             * @function getTypeUrl
             * @memberof onnx.TensorShapeProto.Dimension
             * @static
             * @param {string} [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
             * @returns {string} The type url
             */
            Dimension.getTypeUrl = function(prefix) {
                if (prefix === $undefined)
                    prefix = "type.googleapis.com";
                return prefix + "/onnx.TensorShapeProto.Dimension";
            };

            return Dimension;
        })();

        return TensorShapeProto;
    })();

    onnx.TypeProto = (function() {

        /**
         * Properties of a TypeProto.
         * @typedef {Object} onnx.TypeProto.$Properties
         * @property {onnx.TypeProto.Tensor.$Properties|null} [tensorType] TypeProto tensorType
         * @property {onnx.TypeProto.Sequence.$Properties|null} [sequenceType] TypeProto sequenceType
         * @property {onnx.TypeProto.Map.$Properties|null} [mapType] TypeProto mapType
         * @property {onnx.TypeProto.Optional.$Properties|null} [optionalType] TypeProto optionalType
         * @property {onnx.TypeProto.SparseTensor.$Properties|null} [sparseTensorType] TypeProto sparseTensorType
         * @property {string|null} [denotation] TypeProto denotation
         * @property {"tensorType"|"sequenceType"|"mapType"|"optionalType"|"sparseTensorType"} [value] TypeProto value
         * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding when enabled
         */

        /**
         * Properties of a TypeProto.
         * @memberof onnx
         * @interface ITypeProto
         * @augments onnx.TypeProto.$Properties
         * @deprecated Use onnx.TypeProto.$Properties instead.
         */

        /**
         * Narrowed shape of a TypeProto.
         * @typedef {{
         *   tensorType?: onnx.TypeProto.Tensor.$Shape|null;
         *   sequenceType?: onnx.TypeProto.Sequence.$Shape|null;
         *   mapType?: onnx.TypeProto.Map.$Shape|null;
         *   optionalType?: onnx.TypeProto.Optional.$Shape|null;
         *   sparseTensorType?: onnx.TypeProto.SparseTensor.$Shape|null;
         *   denotation?: string|null;
         *   $unknowns?: Array.<Uint8Array>;
         * } & (
         *   ({ value?: undefined; tensorType?: null; sequenceType?: null; mapType?: null; optionalType?: null; sparseTensorType?: null }|{ value?: "tensorType"; tensorType: onnx.TypeProto.Tensor.$Shape; sequenceType?: null; mapType?: null; optionalType?: null; sparseTensorType?: null }|{ value?: "sequenceType"; tensorType?: null; sequenceType: onnx.TypeProto.Sequence.$Shape; mapType?: null; optionalType?: null; sparseTensorType?: null }|{ value?: "mapType"; tensorType?: null; sequenceType?: null; mapType: onnx.TypeProto.Map.$Shape; optionalType?: null; sparseTensorType?: null }|{ value?: "optionalType"; tensorType?: null; sequenceType?: null; mapType?: null; optionalType: onnx.TypeProto.Optional.$Shape; sparseTensorType?: null }|{ value?: "sparseTensorType"; tensorType?: null; sequenceType?: null; mapType?: null; optionalType?: null; sparseTensorType: onnx.TypeProto.SparseTensor.$Shape })
         * )} onnx.TypeProto.$Shape
         */

        /**
         * Constructs a new TypeProto.
         * @memberof onnx
         * @classdesc Represents a TypeProto.
         * @constructor
         * @param {onnx.TypeProto.$Properties=} [properties] Properties to set
         * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding when enabled
         */
        const TypeProto = function (properties) {
            if (properties)
                for (let keys = $Object.keys(properties), i = 0; i < keys.length; ++i)
                    if (properties[keys[i]] != null && keys[i] !== "__proto__")
                        this[keys[i]] = properties[keys[i]];
        };

        /**
         * TypeProto tensorType.
         * @member {onnx.TypeProto.Tensor.$Properties|null|undefined} tensorType
         * @memberof onnx.TypeProto
         * @instance
         */
        TypeProto.prototype.tensorType = null;

        /**
         * TypeProto sequenceType.
         * @member {onnx.TypeProto.Sequence.$Properties|null|undefined} sequenceType
         * @memberof onnx.TypeProto
         * @instance
         */
        TypeProto.prototype.sequenceType = null;

        /**
         * TypeProto mapType.
         * @member {onnx.TypeProto.Map.$Properties|null|undefined} mapType
         * @memberof onnx.TypeProto
         * @instance
         */
        TypeProto.prototype.mapType = null;

        /**
         * TypeProto optionalType.
         * @member {onnx.TypeProto.Optional.$Properties|null|undefined} optionalType
         * @memberof onnx.TypeProto
         * @instance
         */
        TypeProto.prototype.optionalType = null;

        /**
         * TypeProto sparseTensorType.
         * @member {onnx.TypeProto.SparseTensor.$Properties|null|undefined} sparseTensorType
         * @memberof onnx.TypeProto
         * @instance
         */
        TypeProto.prototype.sparseTensorType = null;

        /**
         * TypeProto denotation.
         * @member {string} denotation
         * @memberof onnx.TypeProto
         * @instance
         */
        TypeProto.prototype.denotation = "";

        // OneOf field names bound to virtual getters and setters
        let $oneOfFields;

        /**
         * TypeProto value.
         * @member {"tensorType"|"sequenceType"|"mapType"|"optionalType"|"sparseTensorType"|undefined} value
         * @memberof onnx.TypeProto
         * @instance
         */
        $Object.defineProperty(TypeProto.prototype, "value", {
            get: $util.oneOfGetter($oneOfFields = ["tensorType", "sequenceType", "mapType", "optionalType", "sparseTensorType"]),
            set: $util.oneOfSetter($oneOfFields)
        });

        /**
         * Creates a new TypeProto instance using the specified properties.
         * @function create
         * @memberof onnx.TypeProto
         * @static
         * @param {onnx.TypeProto.$Properties=} [properties] Properties to set
         * @returns {onnx.TypeProto} TypeProto instance
         * @type {{
         *   (properties: onnx.TypeProto.$Shape): onnx.TypeProto & onnx.TypeProto.$Shape;
         *   (properties?: onnx.TypeProto.$Properties): onnx.TypeProto;
         * }}
         */
        TypeProto.create = function(properties) {
            return new TypeProto(properties);
        };

        /**
         * Encodes the specified TypeProto message. Does not implicitly {@link onnx.TypeProto.verify|verify} messages.
         * @function encode
         * @memberof onnx.TypeProto
         * @static
         * @param {onnx.TypeProto.$Properties} message TypeProto message or plain object to encode
         * @param {$protobuf.Writer} [writer] Writer to encode to
         * @returns {$protobuf.Writer} Writer
         */
        TypeProto.encode = function (message, writer, _depth) {
            if (!writer)
                writer = $Writer.create();
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                throw $Error("max depth exceeded");
            if (message.tensorType != null && $Object.hasOwnProperty.call(message, "tensorType"))
                $root.onnx.TypeProto.Tensor.encode(message.tensorType, writer.uint32(/* id 1, wireType 2 =*/10).fork(), _depth + 1).ldelim();
            if (message.sequenceType != null && $Object.hasOwnProperty.call(message, "sequenceType"))
                $root.onnx.TypeProto.Sequence.encode(message.sequenceType, writer.uint32(/* id 4, wireType 2 =*/34).fork(), _depth + 1).ldelim();
            if (message.mapType != null && $Object.hasOwnProperty.call(message, "mapType"))
                $root.onnx.TypeProto.Map.encode(message.mapType, writer.uint32(/* id 5, wireType 2 =*/42).fork(), _depth + 1).ldelim();
            if (message.denotation != null && $Object.hasOwnProperty.call(message, "denotation"))
                writer.uint32(/* id 6, wireType 2 =*/50).string(message.denotation);
            if (message.sparseTensorType != null && $Object.hasOwnProperty.call(message, "sparseTensorType"))
                $root.onnx.TypeProto.SparseTensor.encode(message.sparseTensorType, writer.uint32(/* id 8, wireType 2 =*/66).fork(), _depth + 1).ldelim();
            if (message.optionalType != null && $Object.hasOwnProperty.call(message, "optionalType"))
                $root.onnx.TypeProto.Optional.encode(message.optionalType, writer.uint32(/* id 9, wireType 2 =*/74).fork(), _depth + 1).ldelim();
            if (message.$unknowns != null && $Object.hasOwnProperty.call(message, "$unknowns"))
                for (let i = 0; i < message.$unknowns.length; ++i)
                    writer.raw(message.$unknowns[i]);
            return writer;
        };

        /**
         * Encodes the specified TypeProto message, length delimited. Does not implicitly {@link onnx.TypeProto.verify|verify} messages.
         * @function encodeDelimited
         * @memberof onnx.TypeProto
         * @static
         * @param {onnx.TypeProto.$Properties} message TypeProto message or plain object to encode
         * @param {$protobuf.Writer} [writer] Writer to encode to
         * @returns {$protobuf.Writer} Writer
         */
        TypeProto.encodeDelimited = function(message, writer) {
            return this.encode(message, (writer || $Writer.create()).fork()).ldelim();
        };

        /**
         * Decodes a TypeProto message from the specified reader or buffer.
         * @function decode
         * @memberof onnx.TypeProto
         * @static
         * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
         * @param {number} [length] Message length if known beforehand
         * @returns {onnx.TypeProto & onnx.TypeProto.$Shape} TypeProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        TypeProto.decode = function (reader, length, _end, _depth, _target) {
            if (!(reader instanceof $Reader))
                reader = $Reader.create(reader);
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $Reader.recursionLimit)
                throw $Error("max depth exceeded");
            let end = length === $undefined ? reader.len : reader.pos + length, message = _target || new $root.onnx.TypeProto();
            while (reader.pos < end) {
                let start = reader.pos;
                let tag = reader.tag();
                if (tag === _end) {
                    _end = $undefined;
                    break;
                }
                let wireType = tag & 7;
                switch (tag >>>= 3) {
                case 1: {
                        if (wireType !== 2)
                            break;
                        message.tensorType = $root.onnx.TypeProto.Tensor.decode(reader, reader.uint32(), $undefined, _depth + 1, message.tensorType);
                        message.value = "tensorType";
                        continue;
                    }
                case 4: {
                        if (wireType !== 2)
                            break;
                        message.sequenceType = $root.onnx.TypeProto.Sequence.decode(reader, reader.uint32(), $undefined, _depth + 1, message.sequenceType);
                        message.value = "sequenceType";
                        continue;
                    }
                case 5: {
                        if (wireType !== 2)
                            break;
                        message.mapType = $root.onnx.TypeProto.Map.decode(reader, reader.uint32(), $undefined, _depth + 1, message.mapType);
                        message.value = "mapType";
                        continue;
                    }
                case 9: {
                        if (wireType !== 2)
                            break;
                        message.optionalType = $root.onnx.TypeProto.Optional.decode(reader, reader.uint32(), $undefined, _depth + 1, message.optionalType);
                        message.value = "optionalType";
                        continue;
                    }
                case 8: {
                        if (wireType !== 2)
                            break;
                        message.sparseTensorType = $root.onnx.TypeProto.SparseTensor.decode(reader, reader.uint32(), $undefined, _depth + 1, message.sparseTensorType);
                        message.value = "sparseTensorType";
                        continue;
                    }
                case 6: {
                        if (wireType !== 2)
                            break;
                        message.denotation = reader.string();
                        continue;
                    }
                }
                reader.skipType(wireType, _depth, tag);
                if (!reader.discardUnknown) {
                    $util.makeProp(message, "$unknowns", false);
                    (message.$unknowns || (message.$unknowns = [])).push(reader.raw(start, reader.pos));
                }
            }
            if (_end !== $undefined)
                throw $Error("missing end group");
            return message;
        };

        /**
         * Decodes a TypeProto message from the specified reader or buffer, length delimited.
         * @function decodeDelimited
         * @memberof onnx.TypeProto
         * @static
         * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
         * @returns {onnx.TypeProto & onnx.TypeProto.$Shape} TypeProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        TypeProto.decodeDelimited = function(reader) {
            if (!(reader instanceof $Reader))
                reader = new $Reader(reader);
            return this.decode(reader, reader.uint32());
        };

        /**
         * Verifies a TypeProto message.
         * @function verify
         * @memberof onnx.TypeProto
         * @static
         * @param {Object.<string,*>} message Plain object to verify
         * @returns {string|null} `null` if valid, otherwise the reason why it is not
         */
        TypeProto.verify = function (message, _depth) {
            if (typeof message !== "object" || message === null)
                return "object expected";
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                return "max depth exceeded";
            let properties = {};
            if (message.tensorType != null && $Object.hasOwnProperty.call(message, "tensorType")) {
                properties.value = 1;
                {
                    let error = $root.onnx.TypeProto.Tensor.verify(message.tensorType, _depth + 1);
                    if (error)
                        return "tensorType." + error;
                }
            }
            if (message.sequenceType != null && $Object.hasOwnProperty.call(message, "sequenceType")) {
                if (properties.value === 1)
                    return "value: multiple values";
                properties.value = 1;
                {
                    let error = $root.onnx.TypeProto.Sequence.verify(message.sequenceType, _depth + 1);
                    if (error)
                        return "sequenceType." + error;
                }
            }
            if (message.mapType != null && $Object.hasOwnProperty.call(message, "mapType")) {
                if (properties.value === 1)
                    return "value: multiple values";
                properties.value = 1;
                {
                    let error = $root.onnx.TypeProto.Map.verify(message.mapType, _depth + 1);
                    if (error)
                        return "mapType." + error;
                }
            }
            if (message.optionalType != null && $Object.hasOwnProperty.call(message, "optionalType")) {
                if (properties.value === 1)
                    return "value: multiple values";
                properties.value = 1;
                {
                    let error = $root.onnx.TypeProto.Optional.verify(message.optionalType, _depth + 1);
                    if (error)
                        return "optionalType." + error;
                }
            }
            if (message.sparseTensorType != null && $Object.hasOwnProperty.call(message, "sparseTensorType")) {
                if (properties.value === 1)
                    return "value: multiple values";
                properties.value = 1;
                {
                    let error = $root.onnx.TypeProto.SparseTensor.verify(message.sparseTensorType, _depth + 1);
                    if (error)
                        return "sparseTensorType." + error;
                }
            }
            if (message.denotation != null && $Object.hasOwnProperty.call(message, "denotation"))
                if (!$util.isString(message.denotation))
                    return "denotation: string expected";
            return null;
        };

        /**
         * Creates a TypeProto message from a plain object. Also converts values to their respective internal types.
         * @function fromObject
         * @memberof onnx.TypeProto
         * @static
         * @param {Object.<string,*>} object Plain object
         * @returns {onnx.TypeProto} TypeProto
         */
        TypeProto.fromObject = function (object, _depth) {
            if (object instanceof $root.onnx.TypeProto)
                return object;
            if (!$util.isObject(object))
                throw $TypeError(".onnx.TypeProto: object expected");
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                throw $Error("max depth exceeded");
            let message = new $root.onnx.TypeProto();
            if (object.tensorType != null) {
                if (!$util.isObject(object.tensorType))
                    throw $TypeError(".onnx.TypeProto.tensorType: object expected");
                message.tensorType = $root.onnx.TypeProto.Tensor.fromObject(object.tensorType, _depth + 1);
            }
            if (object.sequenceType != null) {
                if (!$util.isObject(object.sequenceType))
                    throw $TypeError(".onnx.TypeProto.sequenceType: object expected");
                message.sequenceType = $root.onnx.TypeProto.Sequence.fromObject(object.sequenceType, _depth + 1);
            }
            if (object.mapType != null) {
                if (!$util.isObject(object.mapType))
                    throw $TypeError(".onnx.TypeProto.mapType: object expected");
                message.mapType = $root.onnx.TypeProto.Map.fromObject(object.mapType, _depth + 1);
            }
            if (object.optionalType != null) {
                if (!$util.isObject(object.optionalType))
                    throw $TypeError(".onnx.TypeProto.optionalType: object expected");
                message.optionalType = $root.onnx.TypeProto.Optional.fromObject(object.optionalType, _depth + 1);
            }
            if (object.sparseTensorType != null) {
                if (!$util.isObject(object.sparseTensorType))
                    throw $TypeError(".onnx.TypeProto.sparseTensorType: object expected");
                message.sparseTensorType = $root.onnx.TypeProto.SparseTensor.fromObject(object.sparseTensorType, _depth + 1);
            }
            if (object.denotation != null)
                message.denotation = $String(object.denotation);
            return message;
        };

        /**
         * Creates a plain object from a TypeProto message. Also converts values to other types if specified.
         * @function toObject
         * @memberof onnx.TypeProto
         * @static
         * @param {onnx.TypeProto} message TypeProto
         * @param {$protobuf.IConversionOptions} [options] Conversion options
         * @returns {Object.<string,*>} Plain object
         */
        TypeProto.toObject = function (message, options, _depth) {
            if (!options)
                options = {};
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                throw $Error("max depth exceeded");
            let object = {};
            if (options.defaults)
                object.denotation = "";
            if (message.tensorType != null && $Object.hasOwnProperty.call(message, "tensorType")) {
                object.tensorType = $root.onnx.TypeProto.Tensor.toObject(message.tensorType, options, _depth + 1);
                if (options.oneofs)
                    object.value = "tensorType";
            }
            if (message.sequenceType != null && $Object.hasOwnProperty.call(message, "sequenceType")) {
                object.sequenceType = $root.onnx.TypeProto.Sequence.toObject(message.sequenceType, options, _depth + 1);
                if (options.oneofs)
                    object.value = "sequenceType";
            }
            if (message.mapType != null && $Object.hasOwnProperty.call(message, "mapType")) {
                object.mapType = $root.onnx.TypeProto.Map.toObject(message.mapType, options, _depth + 1);
                if (options.oneofs)
                    object.value = "mapType";
            }
            if (message.denotation != null && $Object.hasOwnProperty.call(message, "denotation"))
                object.denotation = message.denotation;
            if (message.sparseTensorType != null && $Object.hasOwnProperty.call(message, "sparseTensorType")) {
                object.sparseTensorType = $root.onnx.TypeProto.SparseTensor.toObject(message.sparseTensorType, options, _depth + 1);
                if (options.oneofs)
                    object.value = "sparseTensorType";
            }
            if (message.optionalType != null && $Object.hasOwnProperty.call(message, "optionalType")) {
                object.optionalType = $root.onnx.TypeProto.Optional.toObject(message.optionalType, options, _depth + 1);
                if (options.oneofs)
                    object.value = "optionalType";
            }
            return object;
        };

        /**
         * Converts this TypeProto to JSON.
         * @function toJSON
         * @memberof onnx.TypeProto
         * @instance
         * @returns {Object.<string,*>} JSON object
         */
        TypeProto.prototype.toJSON = function() {
            return TypeProto.toObject(this, $protobuf.util.toJSONOptions);
        };

        /**
         * Gets the type url for TypeProto
         * @function getTypeUrl
         * @memberof onnx.TypeProto
         * @static
         * @param {string} [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
         * @returns {string} The type url
         */
        TypeProto.getTypeUrl = function(prefix) {
            if (prefix === $undefined)
                prefix = "type.googleapis.com";
            return prefix + "/onnx.TypeProto";
        };

        TypeProto.Tensor = (function() {

            /**
             * Properties of a Tensor.
             * @typedef {Object} onnx.TypeProto.Tensor.$Properties
             * @property {number|null} [elemType] Tensor elemType
             * @property {onnx.TensorShapeProto.$Properties|null} [shape] Tensor shape
             * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding when enabled
             */

            /**
             * Properties of a Tensor.
             * @memberof onnx.TypeProto
             * @interface ITensor
             * @augments onnx.TypeProto.Tensor.$Properties
             * @deprecated Use onnx.TypeProto.Tensor.$Properties instead.
             */

            /**
             * Shape of a Tensor.
             * @typedef {{
             *   elemType?: number|null;
             *   shape?: onnx.TensorShapeProto.$Shape|null;
             *   $unknowns?: Array.<Uint8Array>;
             * }} onnx.TypeProto.Tensor.$Shape
             */

            /**
             * Constructs a new Tensor.
             * @memberof onnx.TypeProto
             * @classdesc Represents a Tensor.
             * @constructor
             * @param {onnx.TypeProto.Tensor.$Properties=} [properties] Properties to set
             * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding when enabled
             */
            const Tensor = function (properties) {
                if (properties)
                    for (let keys = $Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            };

            /**
             * Tensor elemType.
             * @member {number} elemType
             * @memberof onnx.TypeProto.Tensor
             * @instance
             */
            Tensor.prototype.elemType = 0;

            /**
             * Tensor shape.
             * @member {onnx.TensorShapeProto.$Properties|null|undefined} shape
             * @memberof onnx.TypeProto.Tensor
             * @instance
             */
            Tensor.prototype.shape = null;

            /**
             * Creates a new Tensor instance using the specified properties.
             * @function create
             * @memberof onnx.TypeProto.Tensor
             * @static
             * @param {onnx.TypeProto.Tensor.$Properties=} [properties] Properties to set
             * @returns {onnx.TypeProto.Tensor} Tensor instance
             * @type {{
             *   (properties: onnx.TypeProto.Tensor.$Shape): onnx.TypeProto.Tensor & onnx.TypeProto.Tensor.$Shape;
             *   (properties?: onnx.TypeProto.Tensor.$Properties): onnx.TypeProto.Tensor;
             * }}
             */
            Tensor.create = function(properties) {
                return new Tensor(properties);
            };

            /**
             * Encodes the specified Tensor message. Does not implicitly {@link onnx.TypeProto.Tensor.verify|verify} messages.
             * @function encode
             * @memberof onnx.TypeProto.Tensor
             * @static
             * @param {onnx.TypeProto.Tensor.$Properties} message Tensor message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            Tensor.encode = function (message, writer, _depth) {
                if (!writer)
                    writer = $Writer.create();
                if (_depth === $undefined)
                    _depth = 0;
                if (_depth > $util.recursionLimit)
                    throw $Error("max depth exceeded");
                if (message.elemType != null && $Object.hasOwnProperty.call(message, "elemType"))
                    writer.uint32(/* id 1, wireType 0 =*/8).int32(message.elemType);
                if (message.shape != null && $Object.hasOwnProperty.call(message, "shape"))
                    $root.onnx.TensorShapeProto.encode(message.shape, writer.uint32(/* id 2, wireType 2 =*/18).fork(), _depth + 1).ldelim();
                if (message.$unknowns != null && $Object.hasOwnProperty.call(message, "$unknowns"))
                    for (let i = 0; i < message.$unknowns.length; ++i)
                        writer.raw(message.$unknowns[i]);
                return writer;
            };

            /**
             * Encodes the specified Tensor message, length delimited. Does not implicitly {@link onnx.TypeProto.Tensor.verify|verify} messages.
             * @function encodeDelimited
             * @memberof onnx.TypeProto.Tensor
             * @static
             * @param {onnx.TypeProto.Tensor.$Properties} message Tensor message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            Tensor.encodeDelimited = function(message, writer) {
                return this.encode(message, (writer || $Writer.create()).fork()).ldelim();
            };

            /**
             * Decodes a Tensor message from the specified reader or buffer.
             * @function decode
             * @memberof onnx.TypeProto.Tensor
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {onnx.TypeProto.Tensor & onnx.TypeProto.Tensor.$Shape} Tensor
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            Tensor.decode = function (reader, length, _end, _depth, _target) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (_depth === $undefined)
                    _depth = 0;
                if (_depth > $Reader.recursionLimit)
                    throw $Error("max depth exceeded");
                let end = length === $undefined ? reader.len : reader.pos + length, message = _target || new $root.onnx.TypeProto.Tensor();
                while (reader.pos < end) {
                    let start = reader.pos;
                    let tag = reader.tag();
                    if (tag === _end) {
                        _end = $undefined;
                        break;
                    }
                    let wireType = tag & 7;
                    switch (tag >>>= 3) {
                    case 1: {
                            if (wireType !== 0)
                                break;
                            message.elemType = reader.int32();
                            continue;
                        }
                    case 2: {
                            if (wireType !== 2)
                                break;
                            message.shape = $root.onnx.TensorShapeProto.decode(reader, reader.uint32(), $undefined, _depth + 1, message.shape);
                            continue;
                        }
                    }
                    reader.skipType(wireType, _depth, tag);
                    if (!reader.discardUnknown) {
                        $util.makeProp(message, "$unknowns", false);
                        (message.$unknowns || (message.$unknowns = [])).push(reader.raw(start, reader.pos));
                    }
                }
                if (_end !== $undefined)
                    throw $Error("missing end group");
                return message;
            };

            /**
             * Decodes a Tensor message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof onnx.TypeProto.Tensor
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {onnx.TypeProto.Tensor & onnx.TypeProto.Tensor.$Shape} Tensor
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            Tensor.decodeDelimited = function(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies a Tensor message.
             * @function verify
             * @memberof onnx.TypeProto.Tensor
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            Tensor.verify = function (message, _depth) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (_depth === $undefined)
                    _depth = 0;
                if (_depth > $util.recursionLimit)
                    return "max depth exceeded";
                if (message.elemType != null && $Object.hasOwnProperty.call(message, "elemType"))
                    if (!$util.isInteger(message.elemType))
                        return "elemType: integer expected";
                if (message.shape != null && $Object.hasOwnProperty.call(message, "shape")) {
                    let error = $root.onnx.TensorShapeProto.verify(message.shape, _depth + 1);
                    if (error)
                        return "shape." + error;
                }
                return null;
            };

            /**
             * Creates a Tensor message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof onnx.TypeProto.Tensor
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {onnx.TypeProto.Tensor} Tensor
             */
            Tensor.fromObject = function (object, _depth) {
                if (object instanceof $root.onnx.TypeProto.Tensor)
                    return object;
                if (!$util.isObject(object))
                    throw $TypeError(".onnx.TypeProto.Tensor: object expected");
                if (_depth === $undefined)
                    _depth = 0;
                if (_depth > $util.recursionLimit)
                    throw $Error("max depth exceeded");
                let message = new $root.onnx.TypeProto.Tensor();
                if (object.elemType != null)
                    message.elemType = object.elemType | 0;
                if (object.shape != null) {
                    if (!$util.isObject(object.shape))
                        throw $TypeError(".onnx.TypeProto.Tensor.shape: object expected");
                    message.shape = $root.onnx.TensorShapeProto.fromObject(object.shape, _depth + 1);
                }
                return message;
            };

            /**
             * Creates a plain object from a Tensor message. Also converts values to other types if specified.
             * @function toObject
             * @memberof onnx.TypeProto.Tensor
             * @static
             * @param {onnx.TypeProto.Tensor} message Tensor
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            Tensor.toObject = function (message, options, _depth) {
                if (!options)
                    options = {};
                if (_depth === $undefined)
                    _depth = 0;
                if (_depth > $util.recursionLimit)
                    throw $Error("max depth exceeded");
                let object = {};
                if (options.defaults) {
                    object.elemType = 0;
                    object.shape = null;
                }
                if (message.elemType != null && $Object.hasOwnProperty.call(message, "elemType"))
                    object.elemType = message.elemType;
                if (message.shape != null && $Object.hasOwnProperty.call(message, "shape"))
                    object.shape = $root.onnx.TensorShapeProto.toObject(message.shape, options, _depth + 1);
                return object;
            };

            /**
             * Converts this Tensor to JSON.
             * @function toJSON
             * @memberof onnx.TypeProto.Tensor
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            Tensor.prototype.toJSON = function() {
                return Tensor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the type url for Tensor
             * @function getTypeUrl
             * @memberof onnx.TypeProto.Tensor
             * @static
             * @param {string} [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
             * @returns {string} The type url
             */
            Tensor.getTypeUrl = function(prefix) {
                if (prefix === $undefined)
                    prefix = "type.googleapis.com";
                return prefix + "/onnx.TypeProto.Tensor";
            };

            return Tensor;
        })();

        TypeProto.Sequence = (function() {

            /**
             * Properties of a Sequence.
             * @typedef {Object} onnx.TypeProto.Sequence.$Properties
             * @property {onnx.TypeProto.$Properties|null} [elemType] Sequence elemType
             * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding when enabled
             */

            /**
             * Properties of a Sequence.
             * @memberof onnx.TypeProto
             * @interface ISequence
             * @augments onnx.TypeProto.Sequence.$Properties
             * @deprecated Use onnx.TypeProto.Sequence.$Properties instead.
             */

            /**
             * Shape of a Sequence.
             * @typedef {{
             *   elemType?: onnx.TypeProto.$Shape|null;
             *   $unknowns?: Array.<Uint8Array>;
             * }} onnx.TypeProto.Sequence.$Shape
             */

            /**
             * Constructs a new Sequence.
             * @memberof onnx.TypeProto
             * @classdesc Represents a Sequence.
             * @constructor
             * @param {onnx.TypeProto.Sequence.$Properties=} [properties] Properties to set
             * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding when enabled
             */
            const Sequence = function (properties) {
                if (properties)
                    for (let keys = $Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            };

            /**
             * Sequence elemType.
             * @member {onnx.TypeProto.$Properties|null|undefined} elemType
             * @memberof onnx.TypeProto.Sequence
             * @instance
             */
            Sequence.prototype.elemType = null;

            /**
             * Creates a new Sequence instance using the specified properties.
             * @function create
             * @memberof onnx.TypeProto.Sequence
             * @static
             * @param {onnx.TypeProto.Sequence.$Properties=} [properties] Properties to set
             * @returns {onnx.TypeProto.Sequence} Sequence instance
             * @type {{
             *   (properties: onnx.TypeProto.Sequence.$Shape): onnx.TypeProto.Sequence & onnx.TypeProto.Sequence.$Shape;
             *   (properties?: onnx.TypeProto.Sequence.$Properties): onnx.TypeProto.Sequence;
             * }}
             */
            Sequence.create = function(properties) {
                return new Sequence(properties);
            };

            /**
             * Encodes the specified Sequence message. Does not implicitly {@link onnx.TypeProto.Sequence.verify|verify} messages.
             * @function encode
             * @memberof onnx.TypeProto.Sequence
             * @static
             * @param {onnx.TypeProto.Sequence.$Properties} message Sequence message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            Sequence.encode = function (message, writer, _depth) {
                if (!writer)
                    writer = $Writer.create();
                if (_depth === $undefined)
                    _depth = 0;
                if (_depth > $util.recursionLimit)
                    throw $Error("max depth exceeded");
                if (message.elemType != null && $Object.hasOwnProperty.call(message, "elemType"))
                    $root.onnx.TypeProto.encode(message.elemType, writer.uint32(/* id 1, wireType 2 =*/10).fork(), _depth + 1).ldelim();
                if (message.$unknowns != null && $Object.hasOwnProperty.call(message, "$unknowns"))
                    for (let i = 0; i < message.$unknowns.length; ++i)
                        writer.raw(message.$unknowns[i]);
                return writer;
            };

            /**
             * Encodes the specified Sequence message, length delimited. Does not implicitly {@link onnx.TypeProto.Sequence.verify|verify} messages.
             * @function encodeDelimited
             * @memberof onnx.TypeProto.Sequence
             * @static
             * @param {onnx.TypeProto.Sequence.$Properties} message Sequence message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            Sequence.encodeDelimited = function(message, writer) {
                return this.encode(message, (writer || $Writer.create()).fork()).ldelim();
            };

            /**
             * Decodes a Sequence message from the specified reader or buffer.
             * @function decode
             * @memberof onnx.TypeProto.Sequence
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {onnx.TypeProto.Sequence & onnx.TypeProto.Sequence.$Shape} Sequence
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            Sequence.decode = function (reader, length, _end, _depth, _target) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (_depth === $undefined)
                    _depth = 0;
                if (_depth > $Reader.recursionLimit)
                    throw $Error("max depth exceeded");
                let end = length === $undefined ? reader.len : reader.pos + length, message = _target || new $root.onnx.TypeProto.Sequence();
                while (reader.pos < end) {
                    let start = reader.pos;
                    let tag = reader.tag();
                    if (tag === _end) {
                        _end = $undefined;
                        break;
                    }
                    let wireType = tag & 7;
                    switch (tag >>>= 3) {
                    case 1: {
                            if (wireType !== 2)
                                break;
                            message.elemType = $root.onnx.TypeProto.decode(reader, reader.uint32(), $undefined, _depth + 1, message.elemType);
                            continue;
                        }
                    }
                    reader.skipType(wireType, _depth, tag);
                    if (!reader.discardUnknown) {
                        $util.makeProp(message, "$unknowns", false);
                        (message.$unknowns || (message.$unknowns = [])).push(reader.raw(start, reader.pos));
                    }
                }
                if (_end !== $undefined)
                    throw $Error("missing end group");
                return message;
            };

            /**
             * Decodes a Sequence message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof onnx.TypeProto.Sequence
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {onnx.TypeProto.Sequence & onnx.TypeProto.Sequence.$Shape} Sequence
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            Sequence.decodeDelimited = function(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies a Sequence message.
             * @function verify
             * @memberof onnx.TypeProto.Sequence
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            Sequence.verify = function (message, _depth) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (_depth === $undefined)
                    _depth = 0;
                if (_depth > $util.recursionLimit)
                    return "max depth exceeded";
                if (message.elemType != null && $Object.hasOwnProperty.call(message, "elemType")) {
                    let error = $root.onnx.TypeProto.verify(message.elemType, _depth + 1);
                    if (error)
                        return "elemType." + error;
                }
                return null;
            };

            /**
             * Creates a Sequence message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof onnx.TypeProto.Sequence
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {onnx.TypeProto.Sequence} Sequence
             */
            Sequence.fromObject = function (object, _depth) {
                if (object instanceof $root.onnx.TypeProto.Sequence)
                    return object;
                if (!$util.isObject(object))
                    throw $TypeError(".onnx.TypeProto.Sequence: object expected");
                if (_depth === $undefined)
                    _depth = 0;
                if (_depth > $util.recursionLimit)
                    throw $Error("max depth exceeded");
                let message = new $root.onnx.TypeProto.Sequence();
                if (object.elemType != null) {
                    if (!$util.isObject(object.elemType))
                        throw $TypeError(".onnx.TypeProto.Sequence.elemType: object expected");
                    message.elemType = $root.onnx.TypeProto.fromObject(object.elemType, _depth + 1);
                }
                return message;
            };

            /**
             * Creates a plain object from a Sequence message. Also converts values to other types if specified.
             * @function toObject
             * @memberof onnx.TypeProto.Sequence
             * @static
             * @param {onnx.TypeProto.Sequence} message Sequence
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            Sequence.toObject = function (message, options, _depth) {
                if (!options)
                    options = {};
                if (_depth === $undefined)
                    _depth = 0;
                if (_depth > $util.recursionLimit)
                    throw $Error("max depth exceeded");
                let object = {};
                if (options.defaults)
                    object.elemType = null;
                if (message.elemType != null && $Object.hasOwnProperty.call(message, "elemType"))
                    object.elemType = $root.onnx.TypeProto.toObject(message.elemType, options, _depth + 1);
                return object;
            };

            /**
             * Converts this Sequence to JSON.
             * @function toJSON
             * @memberof onnx.TypeProto.Sequence
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            Sequence.prototype.toJSON = function() {
                return Sequence.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the type url for Sequence
             * @function getTypeUrl
             * @memberof onnx.TypeProto.Sequence
             * @static
             * @param {string} [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
             * @returns {string} The type url
             */
            Sequence.getTypeUrl = function(prefix) {
                if (prefix === $undefined)
                    prefix = "type.googleapis.com";
                return prefix + "/onnx.TypeProto.Sequence";
            };

            return Sequence;
        })();

        TypeProto.Map = (function() {

            /**
             * Properties of a Map.
             * @typedef {Object} onnx.TypeProto.Map.$Properties
             * @property {number|null} [keyType] Map keyType
             * @property {onnx.TypeProto.$Properties|null} [valueType] Map valueType
             * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding when enabled
             */

            /**
             * Properties of a Map.
             * @memberof onnx.TypeProto
             * @interface IMap
             * @augments onnx.TypeProto.Map.$Properties
             * @deprecated Use onnx.TypeProto.Map.$Properties instead.
             */

            /**
             * Shape of a Map.
             * @typedef {{
             *   keyType?: number|null;
             *   valueType?: onnx.TypeProto.$Shape|null;
             *   $unknowns?: Array.<Uint8Array>;
             * }} onnx.TypeProto.Map.$Shape
             */

            /**
             * Constructs a new Map.
             * @memberof onnx.TypeProto
             * @classdesc Represents a Map.
             * @constructor
             * @param {onnx.TypeProto.Map.$Properties=} [properties] Properties to set
             * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding when enabled
             */
            const Map = function (properties) {
                if (properties)
                    for (let keys = $Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            };

            /**
             * Map keyType.
             * @member {number} keyType
             * @memberof onnx.TypeProto.Map
             * @instance
             */
            Map.prototype.keyType = 0;

            /**
             * Map valueType.
             * @member {onnx.TypeProto.$Properties|null|undefined} valueType
             * @memberof onnx.TypeProto.Map
             * @instance
             */
            Map.prototype.valueType = null;

            /**
             * Creates a new Map instance using the specified properties.
             * @function create
             * @memberof onnx.TypeProto.Map
             * @static
             * @param {onnx.TypeProto.Map.$Properties=} [properties] Properties to set
             * @returns {onnx.TypeProto.Map} Map instance
             * @type {{
             *   (properties: onnx.TypeProto.Map.$Shape): onnx.TypeProto.Map & onnx.TypeProto.Map.$Shape;
             *   (properties?: onnx.TypeProto.Map.$Properties): onnx.TypeProto.Map;
             * }}
             */
            Map.create = function(properties) {
                return new Map(properties);
            };

            /**
             * Encodes the specified Map message. Does not implicitly {@link onnx.TypeProto.Map.verify|verify} messages.
             * @function encode
             * @memberof onnx.TypeProto.Map
             * @static
             * @param {onnx.TypeProto.Map.$Properties} message Map message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            Map.encode = function (message, writer, _depth) {
                if (!writer)
                    writer = $Writer.create();
                if (_depth === $undefined)
                    _depth = 0;
                if (_depth > $util.recursionLimit)
                    throw $Error("max depth exceeded");
                if (message.keyType != null && $Object.hasOwnProperty.call(message, "keyType"))
                    writer.uint32(/* id 1, wireType 0 =*/8).int32(message.keyType);
                if (message.valueType != null && $Object.hasOwnProperty.call(message, "valueType"))
                    $root.onnx.TypeProto.encode(message.valueType, writer.uint32(/* id 2, wireType 2 =*/18).fork(), _depth + 1).ldelim();
                if (message.$unknowns != null && $Object.hasOwnProperty.call(message, "$unknowns"))
                    for (let i = 0; i < message.$unknowns.length; ++i)
                        writer.raw(message.$unknowns[i]);
                return writer;
            };

            /**
             * Encodes the specified Map message, length delimited. Does not implicitly {@link onnx.TypeProto.Map.verify|verify} messages.
             * @function encodeDelimited
             * @memberof onnx.TypeProto.Map
             * @static
             * @param {onnx.TypeProto.Map.$Properties} message Map message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            Map.encodeDelimited = function(message, writer) {
                return this.encode(message, (writer || $Writer.create()).fork()).ldelim();
            };

            /**
             * Decodes a Map message from the specified reader or buffer.
             * @function decode
             * @memberof onnx.TypeProto.Map
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {onnx.TypeProto.Map & onnx.TypeProto.Map.$Shape} Map
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            Map.decode = function (reader, length, _end, _depth, _target) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (_depth === $undefined)
                    _depth = 0;
                if (_depth > $Reader.recursionLimit)
                    throw $Error("max depth exceeded");
                let end = length === $undefined ? reader.len : reader.pos + length, message = _target || new $root.onnx.TypeProto.Map();
                while (reader.pos < end) {
                    let start = reader.pos;
                    let tag = reader.tag();
                    if (tag === _end) {
                        _end = $undefined;
                        break;
                    }
                    let wireType = tag & 7;
                    switch (tag >>>= 3) {
                    case 1: {
                            if (wireType !== 0)
                                break;
                            message.keyType = reader.int32();
                            continue;
                        }
                    case 2: {
                            if (wireType !== 2)
                                break;
                            message.valueType = $root.onnx.TypeProto.decode(reader, reader.uint32(), $undefined, _depth + 1, message.valueType);
                            continue;
                        }
                    }
                    reader.skipType(wireType, _depth, tag);
                    if (!reader.discardUnknown) {
                        $util.makeProp(message, "$unknowns", false);
                        (message.$unknowns || (message.$unknowns = [])).push(reader.raw(start, reader.pos));
                    }
                }
                if (_end !== $undefined)
                    throw $Error("missing end group");
                return message;
            };

            /**
             * Decodes a Map message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof onnx.TypeProto.Map
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {onnx.TypeProto.Map & onnx.TypeProto.Map.$Shape} Map
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            Map.decodeDelimited = function(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies a Map message.
             * @function verify
             * @memberof onnx.TypeProto.Map
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            Map.verify = function (message, _depth) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (_depth === $undefined)
                    _depth = 0;
                if (_depth > $util.recursionLimit)
                    return "max depth exceeded";
                if (message.keyType != null && $Object.hasOwnProperty.call(message, "keyType"))
                    if (!$util.isInteger(message.keyType))
                        return "keyType: integer expected";
                if (message.valueType != null && $Object.hasOwnProperty.call(message, "valueType")) {
                    let error = $root.onnx.TypeProto.verify(message.valueType, _depth + 1);
                    if (error)
                        return "valueType." + error;
                }
                return null;
            };

            /**
             * Creates a Map message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof onnx.TypeProto.Map
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {onnx.TypeProto.Map} Map
             */
            Map.fromObject = function (object, _depth) {
                if (object instanceof $root.onnx.TypeProto.Map)
                    return object;
                if (!$util.isObject(object))
                    throw $TypeError(".onnx.TypeProto.Map: object expected");
                if (_depth === $undefined)
                    _depth = 0;
                if (_depth > $util.recursionLimit)
                    throw $Error("max depth exceeded");
                let message = new $root.onnx.TypeProto.Map();
                if (object.keyType != null)
                    message.keyType = object.keyType | 0;
                if (object.valueType != null) {
                    if (!$util.isObject(object.valueType))
                        throw $TypeError(".onnx.TypeProto.Map.valueType: object expected");
                    message.valueType = $root.onnx.TypeProto.fromObject(object.valueType, _depth + 1);
                }
                return message;
            };

            /**
             * Creates a plain object from a Map message. Also converts values to other types if specified.
             * @function toObject
             * @memberof onnx.TypeProto.Map
             * @static
             * @param {onnx.TypeProto.Map} message Map
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            Map.toObject = function (message, options, _depth) {
                if (!options)
                    options = {};
                if (_depth === $undefined)
                    _depth = 0;
                if (_depth > $util.recursionLimit)
                    throw $Error("max depth exceeded");
                let object = {};
                if (options.defaults) {
                    object.keyType = 0;
                    object.valueType = null;
                }
                if (message.keyType != null && $Object.hasOwnProperty.call(message, "keyType"))
                    object.keyType = message.keyType;
                if (message.valueType != null && $Object.hasOwnProperty.call(message, "valueType"))
                    object.valueType = $root.onnx.TypeProto.toObject(message.valueType, options, _depth + 1);
                return object;
            };

            /**
             * Converts this Map to JSON.
             * @function toJSON
             * @memberof onnx.TypeProto.Map
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            Map.prototype.toJSON = function() {
                return Map.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the type url for Map
             * @function getTypeUrl
             * @memberof onnx.TypeProto.Map
             * @static
             * @param {string} [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
             * @returns {string} The type url
             */
            Map.getTypeUrl = function(prefix) {
                if (prefix === $undefined)
                    prefix = "type.googleapis.com";
                return prefix + "/onnx.TypeProto.Map";
            };

            return Map;
        })();

        TypeProto.Optional = (function() {

            /**
             * Properties of an Optional.
             * @typedef {Object} onnx.TypeProto.Optional.$Properties
             * @property {onnx.TypeProto.$Properties|null} [elemType] Optional elemType
             * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding when enabled
             */

            /**
             * Properties of an Optional.
             * @memberof onnx.TypeProto
             * @interface IOptional
             * @augments onnx.TypeProto.Optional.$Properties
             * @deprecated Use onnx.TypeProto.Optional.$Properties instead.
             */

            /**
             * Shape of an Optional.
             * @typedef {{
             *   elemType?: onnx.TypeProto.$Shape|null;
             *   $unknowns?: Array.<Uint8Array>;
             * }} onnx.TypeProto.Optional.$Shape
             */

            /**
             * Constructs a new Optional.
             * @memberof onnx.TypeProto
             * @classdesc Represents an Optional.
             * @constructor
             * @param {onnx.TypeProto.Optional.$Properties=} [properties] Properties to set
             * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding when enabled
             */
            const Optional = function (properties) {
                if (properties)
                    for (let keys = $Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            };

            /**
             * Optional elemType.
             * @member {onnx.TypeProto.$Properties|null|undefined} elemType
             * @memberof onnx.TypeProto.Optional
             * @instance
             */
            Optional.prototype.elemType = null;

            /**
             * Creates a new Optional instance using the specified properties.
             * @function create
             * @memberof onnx.TypeProto.Optional
             * @static
             * @param {onnx.TypeProto.Optional.$Properties=} [properties] Properties to set
             * @returns {onnx.TypeProto.Optional} Optional instance
             * @type {{
             *   (properties: onnx.TypeProto.Optional.$Shape): onnx.TypeProto.Optional & onnx.TypeProto.Optional.$Shape;
             *   (properties?: onnx.TypeProto.Optional.$Properties): onnx.TypeProto.Optional;
             * }}
             */
            Optional.create = function(properties) {
                return new Optional(properties);
            };

            /**
             * Encodes the specified Optional message. Does not implicitly {@link onnx.TypeProto.Optional.verify|verify} messages.
             * @function encode
             * @memberof onnx.TypeProto.Optional
             * @static
             * @param {onnx.TypeProto.Optional.$Properties} message Optional message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            Optional.encode = function (message, writer, _depth) {
                if (!writer)
                    writer = $Writer.create();
                if (_depth === $undefined)
                    _depth = 0;
                if (_depth > $util.recursionLimit)
                    throw $Error("max depth exceeded");
                if (message.elemType != null && $Object.hasOwnProperty.call(message, "elemType"))
                    $root.onnx.TypeProto.encode(message.elemType, writer.uint32(/* id 1, wireType 2 =*/10).fork(), _depth + 1).ldelim();
                if (message.$unknowns != null && $Object.hasOwnProperty.call(message, "$unknowns"))
                    for (let i = 0; i < message.$unknowns.length; ++i)
                        writer.raw(message.$unknowns[i]);
                return writer;
            };

            /**
             * Encodes the specified Optional message, length delimited. Does not implicitly {@link onnx.TypeProto.Optional.verify|verify} messages.
             * @function encodeDelimited
             * @memberof onnx.TypeProto.Optional
             * @static
             * @param {onnx.TypeProto.Optional.$Properties} message Optional message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            Optional.encodeDelimited = function(message, writer) {
                return this.encode(message, (writer || $Writer.create()).fork()).ldelim();
            };

            /**
             * Decodes an Optional message from the specified reader or buffer.
             * @function decode
             * @memberof onnx.TypeProto.Optional
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {onnx.TypeProto.Optional & onnx.TypeProto.Optional.$Shape} Optional
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            Optional.decode = function (reader, length, _end, _depth, _target) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (_depth === $undefined)
                    _depth = 0;
                if (_depth > $Reader.recursionLimit)
                    throw $Error("max depth exceeded");
                let end = length === $undefined ? reader.len : reader.pos + length, message = _target || new $root.onnx.TypeProto.Optional();
                while (reader.pos < end) {
                    let start = reader.pos;
                    let tag = reader.tag();
                    if (tag === _end) {
                        _end = $undefined;
                        break;
                    }
                    let wireType = tag & 7;
                    switch (tag >>>= 3) {
                    case 1: {
                            if (wireType !== 2)
                                break;
                            message.elemType = $root.onnx.TypeProto.decode(reader, reader.uint32(), $undefined, _depth + 1, message.elemType);
                            continue;
                        }
                    }
                    reader.skipType(wireType, _depth, tag);
                    if (!reader.discardUnknown) {
                        $util.makeProp(message, "$unknowns", false);
                        (message.$unknowns || (message.$unknowns = [])).push(reader.raw(start, reader.pos));
                    }
                }
                if (_end !== $undefined)
                    throw $Error("missing end group");
                return message;
            };

            /**
             * Decodes an Optional message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof onnx.TypeProto.Optional
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {onnx.TypeProto.Optional & onnx.TypeProto.Optional.$Shape} Optional
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            Optional.decodeDelimited = function(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies an Optional message.
             * @function verify
             * @memberof onnx.TypeProto.Optional
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            Optional.verify = function (message, _depth) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (_depth === $undefined)
                    _depth = 0;
                if (_depth > $util.recursionLimit)
                    return "max depth exceeded";
                if (message.elemType != null && $Object.hasOwnProperty.call(message, "elemType")) {
                    let error = $root.onnx.TypeProto.verify(message.elemType, _depth + 1);
                    if (error)
                        return "elemType." + error;
                }
                return null;
            };

            /**
             * Creates an Optional message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof onnx.TypeProto.Optional
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {onnx.TypeProto.Optional} Optional
             */
            Optional.fromObject = function (object, _depth) {
                if (object instanceof $root.onnx.TypeProto.Optional)
                    return object;
                if (!$util.isObject(object))
                    throw $TypeError(".onnx.TypeProto.Optional: object expected");
                if (_depth === $undefined)
                    _depth = 0;
                if (_depth > $util.recursionLimit)
                    throw $Error("max depth exceeded");
                let message = new $root.onnx.TypeProto.Optional();
                if (object.elemType != null) {
                    if (!$util.isObject(object.elemType))
                        throw $TypeError(".onnx.TypeProto.Optional.elemType: object expected");
                    message.elemType = $root.onnx.TypeProto.fromObject(object.elemType, _depth + 1);
                }
                return message;
            };

            /**
             * Creates a plain object from an Optional message. Also converts values to other types if specified.
             * @function toObject
             * @memberof onnx.TypeProto.Optional
             * @static
             * @param {onnx.TypeProto.Optional} message Optional
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            Optional.toObject = function (message, options, _depth) {
                if (!options)
                    options = {};
                if (_depth === $undefined)
                    _depth = 0;
                if (_depth > $util.recursionLimit)
                    throw $Error("max depth exceeded");
                let object = {};
                if (options.defaults)
                    object.elemType = null;
                if (message.elemType != null && $Object.hasOwnProperty.call(message, "elemType"))
                    object.elemType = $root.onnx.TypeProto.toObject(message.elemType, options, _depth + 1);
                return object;
            };

            /**
             * Converts this Optional to JSON.
             * @function toJSON
             * @memberof onnx.TypeProto.Optional
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            Optional.prototype.toJSON = function() {
                return Optional.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the type url for Optional
             * @function getTypeUrl
             * @memberof onnx.TypeProto.Optional
             * @static
             * @param {string} [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
             * @returns {string} The type url
             */
            Optional.getTypeUrl = function(prefix) {
                if (prefix === $undefined)
                    prefix = "type.googleapis.com";
                return prefix + "/onnx.TypeProto.Optional";
            };

            return Optional;
        })();

        TypeProto.SparseTensor = (function() {

            /**
             * Properties of a SparseTensor.
             * @typedef {Object} onnx.TypeProto.SparseTensor.$Properties
             * @property {number|null} [elemType] SparseTensor elemType
             * @property {onnx.TensorShapeProto.$Properties|null} [shape] SparseTensor shape
             * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding when enabled
             */

            /**
             * Properties of a SparseTensor.
             * @memberof onnx.TypeProto
             * @interface ISparseTensor
             * @augments onnx.TypeProto.SparseTensor.$Properties
             * @deprecated Use onnx.TypeProto.SparseTensor.$Properties instead.
             */

            /**
             * Shape of a SparseTensor.
             * @typedef {{
             *   elemType?: number|null;
             *   shape?: onnx.TensorShapeProto.$Shape|null;
             *   $unknowns?: Array.<Uint8Array>;
             * }} onnx.TypeProto.SparseTensor.$Shape
             */

            /**
             * Constructs a new SparseTensor.
             * @memberof onnx.TypeProto
             * @classdesc Represents a SparseTensor.
             * @constructor
             * @param {onnx.TypeProto.SparseTensor.$Properties=} [properties] Properties to set
             * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding when enabled
             */
            const SparseTensor = function (properties) {
                if (properties)
                    for (let keys = $Object.keys(properties), i = 0; i < keys.length; ++i)
                        if (properties[keys[i]] != null && keys[i] !== "__proto__")
                            this[keys[i]] = properties[keys[i]];
            };

            /**
             * SparseTensor elemType.
             * @member {number} elemType
             * @memberof onnx.TypeProto.SparseTensor
             * @instance
             */
            SparseTensor.prototype.elemType = 0;

            /**
             * SparseTensor shape.
             * @member {onnx.TensorShapeProto.$Properties|null|undefined} shape
             * @memberof onnx.TypeProto.SparseTensor
             * @instance
             */
            SparseTensor.prototype.shape = null;

            /**
             * Creates a new SparseTensor instance using the specified properties.
             * @function create
             * @memberof onnx.TypeProto.SparseTensor
             * @static
             * @param {onnx.TypeProto.SparseTensor.$Properties=} [properties] Properties to set
             * @returns {onnx.TypeProto.SparseTensor} SparseTensor instance
             * @type {{
             *   (properties: onnx.TypeProto.SparseTensor.$Shape): onnx.TypeProto.SparseTensor & onnx.TypeProto.SparseTensor.$Shape;
             *   (properties?: onnx.TypeProto.SparseTensor.$Properties): onnx.TypeProto.SparseTensor;
             * }}
             */
            SparseTensor.create = function(properties) {
                return new SparseTensor(properties);
            };

            /**
             * Encodes the specified SparseTensor message. Does not implicitly {@link onnx.TypeProto.SparseTensor.verify|verify} messages.
             * @function encode
             * @memberof onnx.TypeProto.SparseTensor
             * @static
             * @param {onnx.TypeProto.SparseTensor.$Properties} message SparseTensor message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            SparseTensor.encode = function (message, writer, _depth) {
                if (!writer)
                    writer = $Writer.create();
                if (_depth === $undefined)
                    _depth = 0;
                if (_depth > $util.recursionLimit)
                    throw $Error("max depth exceeded");
                if (message.elemType != null && $Object.hasOwnProperty.call(message, "elemType"))
                    writer.uint32(/* id 1, wireType 0 =*/8).int32(message.elemType);
                if (message.shape != null && $Object.hasOwnProperty.call(message, "shape"))
                    $root.onnx.TensorShapeProto.encode(message.shape, writer.uint32(/* id 2, wireType 2 =*/18).fork(), _depth + 1).ldelim();
                if (message.$unknowns != null && $Object.hasOwnProperty.call(message, "$unknowns"))
                    for (let i = 0; i < message.$unknowns.length; ++i)
                        writer.raw(message.$unknowns[i]);
                return writer;
            };

            /**
             * Encodes the specified SparseTensor message, length delimited. Does not implicitly {@link onnx.TypeProto.SparseTensor.verify|verify} messages.
             * @function encodeDelimited
             * @memberof onnx.TypeProto.SparseTensor
             * @static
             * @param {onnx.TypeProto.SparseTensor.$Properties} message SparseTensor message or plain object to encode
             * @param {$protobuf.Writer} [writer] Writer to encode to
             * @returns {$protobuf.Writer} Writer
             */
            SparseTensor.encodeDelimited = function(message, writer) {
                return this.encode(message, (writer || $Writer.create()).fork()).ldelim();
            };

            /**
             * Decodes a SparseTensor message from the specified reader or buffer.
             * @function decode
             * @memberof onnx.TypeProto.SparseTensor
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @param {number} [length] Message length if known beforehand
             * @returns {onnx.TypeProto.SparseTensor & onnx.TypeProto.SparseTensor.$Shape} SparseTensor
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            SparseTensor.decode = function (reader, length, _end, _depth, _target) {
                if (!(reader instanceof $Reader))
                    reader = $Reader.create(reader);
                if (_depth === $undefined)
                    _depth = 0;
                if (_depth > $Reader.recursionLimit)
                    throw $Error("max depth exceeded");
                let end = length === $undefined ? reader.len : reader.pos + length, message = _target || new $root.onnx.TypeProto.SparseTensor();
                while (reader.pos < end) {
                    let start = reader.pos;
                    let tag = reader.tag();
                    if (tag === _end) {
                        _end = $undefined;
                        break;
                    }
                    let wireType = tag & 7;
                    switch (tag >>>= 3) {
                    case 1: {
                            if (wireType !== 0)
                                break;
                            message.elemType = reader.int32();
                            continue;
                        }
                    case 2: {
                            if (wireType !== 2)
                                break;
                            message.shape = $root.onnx.TensorShapeProto.decode(reader, reader.uint32(), $undefined, _depth + 1, message.shape);
                            continue;
                        }
                    }
                    reader.skipType(wireType, _depth, tag);
                    if (!reader.discardUnknown) {
                        $util.makeProp(message, "$unknowns", false);
                        (message.$unknowns || (message.$unknowns = [])).push(reader.raw(start, reader.pos));
                    }
                }
                if (_end !== $undefined)
                    throw $Error("missing end group");
                return message;
            };

            /**
             * Decodes a SparseTensor message from the specified reader or buffer, length delimited.
             * @function decodeDelimited
             * @memberof onnx.TypeProto.SparseTensor
             * @static
             * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
             * @returns {onnx.TypeProto.SparseTensor & onnx.TypeProto.SparseTensor.$Shape} SparseTensor
             * @throws {Error} If the payload is not a reader or valid buffer
             * @throws {$protobuf.util.ProtocolError} If required fields are missing
             */
            SparseTensor.decodeDelimited = function(reader) {
                if (!(reader instanceof $Reader))
                    reader = new $Reader(reader);
                return this.decode(reader, reader.uint32());
            };

            /**
             * Verifies a SparseTensor message.
             * @function verify
             * @memberof onnx.TypeProto.SparseTensor
             * @static
             * @param {Object.<string,*>} message Plain object to verify
             * @returns {string|null} `null` if valid, otherwise the reason why it is not
             */
            SparseTensor.verify = function (message, _depth) {
                if (typeof message !== "object" || message === null)
                    return "object expected";
                if (_depth === $undefined)
                    _depth = 0;
                if (_depth > $util.recursionLimit)
                    return "max depth exceeded";
                if (message.elemType != null && $Object.hasOwnProperty.call(message, "elemType"))
                    if (!$util.isInteger(message.elemType))
                        return "elemType: integer expected";
                if (message.shape != null && $Object.hasOwnProperty.call(message, "shape")) {
                    let error = $root.onnx.TensorShapeProto.verify(message.shape, _depth + 1);
                    if (error)
                        return "shape." + error;
                }
                return null;
            };

            /**
             * Creates a SparseTensor message from a plain object. Also converts values to their respective internal types.
             * @function fromObject
             * @memberof onnx.TypeProto.SparseTensor
             * @static
             * @param {Object.<string,*>} object Plain object
             * @returns {onnx.TypeProto.SparseTensor} SparseTensor
             */
            SparseTensor.fromObject = function (object, _depth) {
                if (object instanceof $root.onnx.TypeProto.SparseTensor)
                    return object;
                if (!$util.isObject(object))
                    throw $TypeError(".onnx.TypeProto.SparseTensor: object expected");
                if (_depth === $undefined)
                    _depth = 0;
                if (_depth > $util.recursionLimit)
                    throw $Error("max depth exceeded");
                let message = new $root.onnx.TypeProto.SparseTensor();
                if (object.elemType != null)
                    message.elemType = object.elemType | 0;
                if (object.shape != null) {
                    if (!$util.isObject(object.shape))
                        throw $TypeError(".onnx.TypeProto.SparseTensor.shape: object expected");
                    message.shape = $root.onnx.TensorShapeProto.fromObject(object.shape, _depth + 1);
                }
                return message;
            };

            /**
             * Creates a plain object from a SparseTensor message. Also converts values to other types if specified.
             * @function toObject
             * @memberof onnx.TypeProto.SparseTensor
             * @static
             * @param {onnx.TypeProto.SparseTensor} message SparseTensor
             * @param {$protobuf.IConversionOptions} [options] Conversion options
             * @returns {Object.<string,*>} Plain object
             */
            SparseTensor.toObject = function (message, options, _depth) {
                if (!options)
                    options = {};
                if (_depth === $undefined)
                    _depth = 0;
                if (_depth > $util.recursionLimit)
                    throw $Error("max depth exceeded");
                let object = {};
                if (options.defaults) {
                    object.elemType = 0;
                    object.shape = null;
                }
                if (message.elemType != null && $Object.hasOwnProperty.call(message, "elemType"))
                    object.elemType = message.elemType;
                if (message.shape != null && $Object.hasOwnProperty.call(message, "shape"))
                    object.shape = $root.onnx.TensorShapeProto.toObject(message.shape, options, _depth + 1);
                return object;
            };

            /**
             * Converts this SparseTensor to JSON.
             * @function toJSON
             * @memberof onnx.TypeProto.SparseTensor
             * @instance
             * @returns {Object.<string,*>} JSON object
             */
            SparseTensor.prototype.toJSON = function() {
                return SparseTensor.toObject(this, $protobuf.util.toJSONOptions);
            };

            /**
             * Gets the type url for SparseTensor
             * @function getTypeUrl
             * @memberof onnx.TypeProto.SparseTensor
             * @static
             * @param {string} [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
             * @returns {string} The type url
             */
            SparseTensor.getTypeUrl = function(prefix) {
                if (prefix === $undefined)
                    prefix = "type.googleapis.com";
                return prefix + "/onnx.TypeProto.SparseTensor";
            };

            return SparseTensor;
        })();

        return TypeProto;
    })();

    onnx.OperatorSetIdProto = (function() {

        /**
         * Properties of an OperatorSetIdProto.
         * @typedef {Object} onnx.OperatorSetIdProto.$Properties
         * @property {string|null} [domain] OperatorSetIdProto domain
         * @property {number|Long|null} [version] OperatorSetIdProto version
         * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding when enabled
         */

        /**
         * Properties of an OperatorSetIdProto.
         * @memberof onnx
         * @interface IOperatorSetIdProto
         * @augments onnx.OperatorSetIdProto.$Properties
         * @deprecated Use onnx.OperatorSetIdProto.$Properties instead.
         */

        /**
         * Shape of an OperatorSetIdProto.
         * @typedef {onnx.OperatorSetIdProto.$Properties} onnx.OperatorSetIdProto.$Shape
         */

        /**
         * Constructs a new OperatorSetIdProto.
         * @memberof onnx
         * @classdesc Represents an OperatorSetIdProto.
         * @constructor
         * @param {onnx.OperatorSetIdProto.$Properties=} [properties] Properties to set
         * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding when enabled
         */
        const OperatorSetIdProto = function (properties) {
            if (properties)
                for (let keys = $Object.keys(properties), i = 0; i < keys.length; ++i)
                    if (properties[keys[i]] != null && keys[i] !== "__proto__")
                        this[keys[i]] = properties[keys[i]];
        };

        /**
         * OperatorSetIdProto domain.
         * @member {string} domain
         * @memberof onnx.OperatorSetIdProto
         * @instance
         */
        OperatorSetIdProto.prototype.domain = "";

        /**
         * OperatorSetIdProto version.
         * @member {number|Long} version
         * @memberof onnx.OperatorSetIdProto
         * @instance
         */
        OperatorSetIdProto.prototype.version = $util.Long ? $util.Long.fromBits(0,0,false) : 0;

        /**
         * Creates a new OperatorSetIdProto instance using the specified properties.
         * @function create
         * @memberof onnx.OperatorSetIdProto
         * @static
         * @param {onnx.OperatorSetIdProto.$Properties=} [properties] Properties to set
         * @returns {onnx.OperatorSetIdProto} OperatorSetIdProto instance
         * @type {{
         *   (properties: onnx.OperatorSetIdProto.$Shape): onnx.OperatorSetIdProto & onnx.OperatorSetIdProto.$Shape;
         *   (properties?: onnx.OperatorSetIdProto.$Properties): onnx.OperatorSetIdProto;
         * }}
         */
        OperatorSetIdProto.create = function(properties) {
            return new OperatorSetIdProto(properties);
        };

        /**
         * Encodes the specified OperatorSetIdProto message. Does not implicitly {@link onnx.OperatorSetIdProto.verify|verify} messages.
         * @function encode
         * @memberof onnx.OperatorSetIdProto
         * @static
         * @param {onnx.OperatorSetIdProto.$Properties} message OperatorSetIdProto message or plain object to encode
         * @param {$protobuf.Writer} [writer] Writer to encode to
         * @returns {$protobuf.Writer} Writer
         */
        OperatorSetIdProto.encode = function (message, writer, _depth) {
            if (!writer)
                writer = $Writer.create();
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                throw $Error("max depth exceeded");
            if (message.domain != null && $Object.hasOwnProperty.call(message, "domain"))
                writer.uint32(/* id 1, wireType 2 =*/10).string(message.domain);
            if (message.version != null && $Object.hasOwnProperty.call(message, "version"))
                writer.uint32(/* id 2, wireType 0 =*/16).int64(message.version);
            if (message.$unknowns != null && $Object.hasOwnProperty.call(message, "$unknowns"))
                for (let i = 0; i < message.$unknowns.length; ++i)
                    writer.raw(message.$unknowns[i]);
            return writer;
        };

        /**
         * Encodes the specified OperatorSetIdProto message, length delimited. Does not implicitly {@link onnx.OperatorSetIdProto.verify|verify} messages.
         * @function encodeDelimited
         * @memberof onnx.OperatorSetIdProto
         * @static
         * @param {onnx.OperatorSetIdProto.$Properties} message OperatorSetIdProto message or plain object to encode
         * @param {$protobuf.Writer} [writer] Writer to encode to
         * @returns {$protobuf.Writer} Writer
         */
        OperatorSetIdProto.encodeDelimited = function(message, writer) {
            return this.encode(message, (writer || $Writer.create()).fork()).ldelim();
        };

        /**
         * Decodes an OperatorSetIdProto message from the specified reader or buffer.
         * @function decode
         * @memberof onnx.OperatorSetIdProto
         * @static
         * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
         * @param {number} [length] Message length if known beforehand
         * @returns {onnx.OperatorSetIdProto & onnx.OperatorSetIdProto.$Shape} OperatorSetIdProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        OperatorSetIdProto.decode = function (reader, length, _end, _depth, _target) {
            if (!(reader instanceof $Reader))
                reader = $Reader.create(reader);
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $Reader.recursionLimit)
                throw $Error("max depth exceeded");
            let end = length === $undefined ? reader.len : reader.pos + length, message = _target || new $root.onnx.OperatorSetIdProto();
            while (reader.pos < end) {
                let start = reader.pos;
                let tag = reader.tag();
                if (tag === _end) {
                    _end = $undefined;
                    break;
                }
                let wireType = tag & 7;
                switch (tag >>>= 3) {
                case 1: {
                        if (wireType !== 2)
                            break;
                        message.domain = reader.string();
                        continue;
                    }
                case 2: {
                        if (wireType !== 0)
                            break;
                        message.version = reader.int64();
                        continue;
                    }
                }
                reader.skipType(wireType, _depth, tag);
                if (!reader.discardUnknown) {
                    $util.makeProp(message, "$unknowns", false);
                    (message.$unknowns || (message.$unknowns = [])).push(reader.raw(start, reader.pos));
                }
            }
            if (_end !== $undefined)
                throw $Error("missing end group");
            return message;
        };

        /**
         * Decodes an OperatorSetIdProto message from the specified reader or buffer, length delimited.
         * @function decodeDelimited
         * @memberof onnx.OperatorSetIdProto
         * @static
         * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
         * @returns {onnx.OperatorSetIdProto & onnx.OperatorSetIdProto.$Shape} OperatorSetIdProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        OperatorSetIdProto.decodeDelimited = function(reader) {
            if (!(reader instanceof $Reader))
                reader = new $Reader(reader);
            return this.decode(reader, reader.uint32());
        };

        /**
         * Verifies an OperatorSetIdProto message.
         * @function verify
         * @memberof onnx.OperatorSetIdProto
         * @static
         * @param {Object.<string,*>} message Plain object to verify
         * @returns {string|null} `null` if valid, otherwise the reason why it is not
         */
        OperatorSetIdProto.verify = function (message, _depth) {
            if (typeof message !== "object" || message === null)
                return "object expected";
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                return "max depth exceeded";
            if (message.domain != null && $Object.hasOwnProperty.call(message, "domain"))
                if (!$util.isString(message.domain))
                    return "domain: string expected";
            if (message.version != null && $Object.hasOwnProperty.call(message, "version"))
                if (!$util.isInteger(message.version) && !(message.version && $util.isInteger(message.version.low) && $util.isInteger(message.version.high)))
                    return "version: integer|Long expected";
            return null;
        };

        /**
         * Creates an OperatorSetIdProto message from a plain object. Also converts values to their respective internal types.
         * @function fromObject
         * @memberof onnx.OperatorSetIdProto
         * @static
         * @param {Object.<string,*>} object Plain object
         * @returns {onnx.OperatorSetIdProto} OperatorSetIdProto
         */
        OperatorSetIdProto.fromObject = function (object, _depth) {
            if (object instanceof $root.onnx.OperatorSetIdProto)
                return object;
            if (!$util.isObject(object))
                throw $TypeError(".onnx.OperatorSetIdProto: object expected");
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                throw $Error("max depth exceeded");
            let message = new $root.onnx.OperatorSetIdProto();
            if (object.domain != null)
                message.domain = $String(object.domain);
            if (object.version != null)
                if ($util.Long)
                    message.version = $util.Long.fromValue(object.version, false);
                else if (typeof object.version === "string")
                    message.version = $parseInt(object.version, 10);
                else if (typeof object.version === "number")
                    message.version = object.version;
                else if (typeof object.version === "object")
                    message.version = new $util.LongBits(object.version.low >>> 0, object.version.high >>> 0).toNumber();
            return message;
        };

        /**
         * Creates a plain object from an OperatorSetIdProto message. Also converts values to other types if specified.
         * @function toObject
         * @memberof onnx.OperatorSetIdProto
         * @static
         * @param {onnx.OperatorSetIdProto} message OperatorSetIdProto
         * @param {$protobuf.IConversionOptions} [options] Conversion options
         * @returns {Object.<string,*>} Plain object
         */
        OperatorSetIdProto.toObject = function (message, options, _depth) {
            if (!options)
                options = {};
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                throw $Error("max depth exceeded");
            let object = {};
            if (options.defaults) {
                object.domain = "";
                if ($util.Long) {
                    let long = new $util.Long(0, 0, false);
                    object.version = options.longs === $String ? long.toString() : options.longs === $Number ? long.toNumber() : typeof $BigInt !== "undefined" && options.longs === $BigInt ? long.toBigInt() : long;
                } else
                    object.version = options.longs === $String ? "0" : typeof $BigInt !== "undefined" && options.longs === $BigInt ? $BigInt("0") : 0;
            }
            if (message.domain != null && $Object.hasOwnProperty.call(message, "domain"))
                object.domain = message.domain;
            if (message.version != null && $Object.hasOwnProperty.call(message, "version"))
                if (typeof $BigInt !== "undefined" && options.longs === $BigInt)
                    object.version = typeof message.version === "number" ? $BigInt(message.version) : $util.Long.fromBits(message.version.low >>> 0, message.version.high >>> 0, false).toBigInt();
                else if (typeof message.version === "number")
                    object.version = options.longs === $String ? $String(message.version) : message.version;
                else
                    object.version = options.longs === $String ? $util.Long.prototype.toString.call(message.version) : options.longs === $Number ? new $util.LongBits(message.version.low >>> 0, message.version.high >>> 0).toNumber() : message.version;
            return object;
        };

        /**
         * Converts this OperatorSetIdProto to JSON.
         * @function toJSON
         * @memberof onnx.OperatorSetIdProto
         * @instance
         * @returns {Object.<string,*>} JSON object
         */
        OperatorSetIdProto.prototype.toJSON = function() {
            return OperatorSetIdProto.toObject(this, $protobuf.util.toJSONOptions);
        };

        /**
         * Gets the type url for OperatorSetIdProto
         * @function getTypeUrl
         * @memberof onnx.OperatorSetIdProto
         * @static
         * @param {string} [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
         * @returns {string} The type url
         */
        OperatorSetIdProto.getTypeUrl = function(prefix) {
            if (prefix === $undefined)
                prefix = "type.googleapis.com";
            return prefix + "/onnx.OperatorSetIdProto";
        };

        return OperatorSetIdProto;
    })();

    /**
     * OperatorStatus enum.
     * @name onnx.OperatorStatus
     * @enum {number}
     * @property {number} EXPERIMENTAL=0 EXPERIMENTAL value
     * @property {number} STABLE=1 STABLE value
     */
    onnx.OperatorStatus = (function() {
        const valuesById = $Object.create(null), values = $Object.create(valuesById);
        values[valuesById[0] = "EXPERIMENTAL"] = 0;
        values[valuesById[1] = "STABLE"] = 1;
        return values;
    })();

    onnx.FunctionProto = (function() {

        /**
         * Properties of a FunctionProto.
         * @typedef {Object} onnx.FunctionProto.$Properties
         * @property {string|null} [name] FunctionProto name
         * @property {Array.<string>|null} [input] FunctionProto input
         * @property {Array.<string>|null} [output] FunctionProto output
         * @property {Array.<string>|null} [attribute] FunctionProto attribute
         * @property {Array.<onnx.AttributeProto.$Properties>|null} [attributeProto] FunctionProto attributeProto
         * @property {Array.<onnx.NodeProto.$Properties>|null} [node] FunctionProto node
         * @property {string|null} [docString] FunctionProto docString
         * @property {Array.<onnx.OperatorSetIdProto.$Properties>|null} [opsetImport] FunctionProto opsetImport
         * @property {string|null} [domain] FunctionProto domain
         * @property {string|null} [overload] FunctionProto overload
         * @property {Array.<onnx.ValueInfoProto.$Properties>|null} [valueInfo] FunctionProto valueInfo
         * @property {Array.<onnx.StringStringEntryProto.$Properties>|null} [metadataProps] FunctionProto metadataProps
         * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding when enabled
         */

        /**
         * Properties of a FunctionProto.
         * @memberof onnx
         * @interface IFunctionProto
         * @augments onnx.FunctionProto.$Properties
         * @deprecated Use onnx.FunctionProto.$Properties instead.
         */

        /**
         * Shape of a FunctionProto.
         * @typedef {{
         *   name?: string|null;
         *   input?: Array.<string>|null;
         *   output?: Array.<string>|null;
         *   attribute?: Array.<string>|null;
         *   attributeProto?: Array.<onnx.AttributeProto.$Shape>|null;
         *   node?: Array.<onnx.NodeProto.$Shape>|null;
         *   docString?: string|null;
         *   opsetImport?: Array.<onnx.OperatorSetIdProto.$Shape>|null;
         *   domain?: string|null;
         *   overload?: string|null;
         *   valueInfo?: Array.<onnx.ValueInfoProto.$Shape>|null;
         *   metadataProps?: Array.<onnx.StringStringEntryProto.$Shape>|null;
         *   $unknowns?: Array.<Uint8Array>;
         * }} onnx.FunctionProto.$Shape
         */

        /**
         * Constructs a new FunctionProto.
         * @memberof onnx
         * @classdesc Represents a FunctionProto.
         * @constructor
         * @param {onnx.FunctionProto.$Properties=} [properties] Properties to set
         * @property {Array.<Uint8Array>} [$unknowns] Unknown fields preserved while decoding when enabled
         */
        const FunctionProto = function (properties) {
            this.input = [];
            this.output = [];
            this.attribute = [];
            this.attributeProto = [];
            this.node = [];
            this.opsetImport = [];
            this.valueInfo = [];
            this.metadataProps = [];
            if (properties)
                for (let keys = $Object.keys(properties), i = 0; i < keys.length; ++i)
                    if (properties[keys[i]] != null && keys[i] !== "__proto__")
                        this[keys[i]] = properties[keys[i]];
        };

        /**
         * FunctionProto name.
         * @member {string} name
         * @memberof onnx.FunctionProto
         * @instance
         */
        FunctionProto.prototype.name = "";

        /**
         * FunctionProto input.
         * @member {Array.<string>} input
         * @memberof onnx.FunctionProto
         * @instance
         */
        FunctionProto.prototype.input = $util.emptyArray;

        /**
         * FunctionProto output.
         * @member {Array.<string>} output
         * @memberof onnx.FunctionProto
         * @instance
         */
        FunctionProto.prototype.output = $util.emptyArray;

        /**
         * FunctionProto attribute.
         * @member {Array.<string>} attribute
         * @memberof onnx.FunctionProto
         * @instance
         */
        FunctionProto.prototype.attribute = $util.emptyArray;

        /**
         * FunctionProto attributeProto.
         * @member {Array.<onnx.AttributeProto.$Properties>} attributeProto
         * @memberof onnx.FunctionProto
         * @instance
         */
        FunctionProto.prototype.attributeProto = $util.emptyArray;

        /**
         * FunctionProto node.
         * @member {Array.<onnx.NodeProto.$Properties>} node
         * @memberof onnx.FunctionProto
         * @instance
         */
        FunctionProto.prototype.node = $util.emptyArray;

        /**
         * FunctionProto docString.
         * @member {string} docString
         * @memberof onnx.FunctionProto
         * @instance
         */
        FunctionProto.prototype.docString = "";

        /**
         * FunctionProto opsetImport.
         * @member {Array.<onnx.OperatorSetIdProto.$Properties>} opsetImport
         * @memberof onnx.FunctionProto
         * @instance
         */
        FunctionProto.prototype.opsetImport = $util.emptyArray;

        /**
         * FunctionProto domain.
         * @member {string} domain
         * @memberof onnx.FunctionProto
         * @instance
         */
        FunctionProto.prototype.domain = "";

        /**
         * FunctionProto overload.
         * @member {string} overload
         * @memberof onnx.FunctionProto
         * @instance
         */
        FunctionProto.prototype.overload = "";

        /**
         * FunctionProto valueInfo.
         * @member {Array.<onnx.ValueInfoProto.$Properties>} valueInfo
         * @memberof onnx.FunctionProto
         * @instance
         */
        FunctionProto.prototype.valueInfo = $util.emptyArray;

        /**
         * FunctionProto metadataProps.
         * @member {Array.<onnx.StringStringEntryProto.$Properties>} metadataProps
         * @memberof onnx.FunctionProto
         * @instance
         */
        FunctionProto.prototype.metadataProps = $util.emptyArray;

        /**
         * Creates a new FunctionProto instance using the specified properties.
         * @function create
         * @memberof onnx.FunctionProto
         * @static
         * @param {onnx.FunctionProto.$Properties=} [properties] Properties to set
         * @returns {onnx.FunctionProto} FunctionProto instance
         * @type {{
         *   (properties: onnx.FunctionProto.$Shape): onnx.FunctionProto & onnx.FunctionProto.$Shape;
         *   (properties?: onnx.FunctionProto.$Properties): onnx.FunctionProto;
         * }}
         */
        FunctionProto.create = function(properties) {
            return new FunctionProto(properties);
        };

        /**
         * Encodes the specified FunctionProto message. Does not implicitly {@link onnx.FunctionProto.verify|verify} messages.
         * @function encode
         * @memberof onnx.FunctionProto
         * @static
         * @param {onnx.FunctionProto.$Properties} message FunctionProto message or plain object to encode
         * @param {$protobuf.Writer} [writer] Writer to encode to
         * @returns {$protobuf.Writer} Writer
         */
        FunctionProto.encode = function (message, writer, _depth) {
            if (!writer)
                writer = $Writer.create();
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                throw $Error("max depth exceeded");
            if (message.name != null && $Object.hasOwnProperty.call(message, "name"))
                writer.uint32(/* id 1, wireType 2 =*/10).string(message.name);
            if (message.input != null && message.input.length)
                for (let i = 0; i < message.input.length; ++i)
                    writer.uint32(/* id 4, wireType 2 =*/34).string(message.input[i]);
            if (message.output != null && message.output.length)
                for (let i = 0; i < message.output.length; ++i)
                    writer.uint32(/* id 5, wireType 2 =*/42).string(message.output[i]);
            if (message.attribute != null && message.attribute.length)
                for (let i = 0; i < message.attribute.length; ++i)
                    writer.uint32(/* id 6, wireType 2 =*/50).string(message.attribute[i]);
            if (message.node != null && message.node.length)
                for (let i = 0; i < message.node.length; ++i)
                    $root.onnx.NodeProto.encode(message.node[i], writer.uint32(/* id 7, wireType 2 =*/58).fork(), _depth + 1).ldelim();
            if (message.docString != null && $Object.hasOwnProperty.call(message, "docString"))
                writer.uint32(/* id 8, wireType 2 =*/66).string(message.docString);
            if (message.opsetImport != null && message.opsetImport.length)
                for (let i = 0; i < message.opsetImport.length; ++i)
                    $root.onnx.OperatorSetIdProto.encode(message.opsetImport[i], writer.uint32(/* id 9, wireType 2 =*/74).fork(), _depth + 1).ldelim();
            if (message.domain != null && $Object.hasOwnProperty.call(message, "domain"))
                writer.uint32(/* id 10, wireType 2 =*/82).string(message.domain);
            if (message.attributeProto != null && message.attributeProto.length)
                for (let i = 0; i < message.attributeProto.length; ++i)
                    $root.onnx.AttributeProto.encode(message.attributeProto[i], writer.uint32(/* id 11, wireType 2 =*/90).fork(), _depth + 1).ldelim();
            if (message.valueInfo != null && message.valueInfo.length)
                for (let i = 0; i < message.valueInfo.length; ++i)
                    $root.onnx.ValueInfoProto.encode(message.valueInfo[i], writer.uint32(/* id 12, wireType 2 =*/98).fork(), _depth + 1).ldelim();
            if (message.overload != null && $Object.hasOwnProperty.call(message, "overload"))
                writer.uint32(/* id 13, wireType 2 =*/106).string(message.overload);
            if (message.metadataProps != null && message.metadataProps.length)
                for (let i = 0; i < message.metadataProps.length; ++i)
                    $root.onnx.StringStringEntryProto.encode(message.metadataProps[i], writer.uint32(/* id 14, wireType 2 =*/114).fork(), _depth + 1).ldelim();
            if (message.$unknowns != null && $Object.hasOwnProperty.call(message, "$unknowns"))
                for (let i = 0; i < message.$unknowns.length; ++i)
                    writer.raw(message.$unknowns[i]);
            return writer;
        };

        /**
         * Encodes the specified FunctionProto message, length delimited. Does not implicitly {@link onnx.FunctionProto.verify|verify} messages.
         * @function encodeDelimited
         * @memberof onnx.FunctionProto
         * @static
         * @param {onnx.FunctionProto.$Properties} message FunctionProto message or plain object to encode
         * @param {$protobuf.Writer} [writer] Writer to encode to
         * @returns {$protobuf.Writer} Writer
         */
        FunctionProto.encodeDelimited = function(message, writer) {
            return this.encode(message, (writer || $Writer.create()).fork()).ldelim();
        };

        /**
         * Decodes a FunctionProto message from the specified reader or buffer.
         * @function decode
         * @memberof onnx.FunctionProto
         * @static
         * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
         * @param {number} [length] Message length if known beforehand
         * @returns {onnx.FunctionProto & onnx.FunctionProto.$Shape} FunctionProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        FunctionProto.decode = function (reader, length, _end, _depth, _target) {
            if (!(reader instanceof $Reader))
                reader = $Reader.create(reader);
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $Reader.recursionLimit)
                throw $Error("max depth exceeded");
            let end = length === $undefined ? reader.len : reader.pos + length, message = _target || new $root.onnx.FunctionProto();
            while (reader.pos < end) {
                let start = reader.pos;
                let tag = reader.tag();
                if (tag === _end) {
                    _end = $undefined;
                    break;
                }
                let wireType = tag & 7;
                switch (tag >>>= 3) {
                case 1: {
                        if (wireType !== 2)
                            break;
                        message.name = reader.string();
                        continue;
                    }
                case 4: {
                        if (wireType !== 2)
                            break;
                        if (!(message.input && message.input.length))
                            message.input = [];
                        message.input.push(reader.string());
                        continue;
                    }
                case 5: {
                        if (wireType !== 2)
                            break;
                        if (!(message.output && message.output.length))
                            message.output = [];
                        message.output.push(reader.string());
                        continue;
                    }
                case 6: {
                        if (wireType !== 2)
                            break;
                        if (!(message.attribute && message.attribute.length))
                            message.attribute = [];
                        message.attribute.push(reader.string());
                        continue;
                    }
                case 11: {
                        if (wireType !== 2)
                            break;
                        if (!(message.attributeProto && message.attributeProto.length))
                            message.attributeProto = [];
                        message.attributeProto.push($root.onnx.AttributeProto.decode(reader, reader.uint32(), $undefined, _depth + 1));
                        continue;
                    }
                case 7: {
                        if (wireType !== 2)
                            break;
                        if (!(message.node && message.node.length))
                            message.node = [];
                        message.node.push($root.onnx.NodeProto.decode(reader, reader.uint32(), $undefined, _depth + 1));
                        continue;
                    }
                case 8: {
                        if (wireType !== 2)
                            break;
                        message.docString = reader.string();
                        continue;
                    }
                case 9: {
                        if (wireType !== 2)
                            break;
                        if (!(message.opsetImport && message.opsetImport.length))
                            message.opsetImport = [];
                        message.opsetImport.push($root.onnx.OperatorSetIdProto.decode(reader, reader.uint32(), $undefined, _depth + 1));
                        continue;
                    }
                case 10: {
                        if (wireType !== 2)
                            break;
                        message.domain = reader.string();
                        continue;
                    }
                case 13: {
                        if (wireType !== 2)
                            break;
                        message.overload = reader.string();
                        continue;
                    }
                case 12: {
                        if (wireType !== 2)
                            break;
                        if (!(message.valueInfo && message.valueInfo.length))
                            message.valueInfo = [];
                        message.valueInfo.push($root.onnx.ValueInfoProto.decode(reader, reader.uint32(), $undefined, _depth + 1));
                        continue;
                    }
                case 14: {
                        if (wireType !== 2)
                            break;
                        if (!(message.metadataProps && message.metadataProps.length))
                            message.metadataProps = [];
                        message.metadataProps.push($root.onnx.StringStringEntryProto.decode(reader, reader.uint32(), $undefined, _depth + 1));
                        continue;
                    }
                }
                reader.skipType(wireType, _depth, tag);
                if (!reader.discardUnknown) {
                    $util.makeProp(message, "$unknowns", false);
                    (message.$unknowns || (message.$unknowns = [])).push(reader.raw(start, reader.pos));
                }
            }
            if (_end !== $undefined)
                throw $Error("missing end group");
            return message;
        };

        /**
         * Decodes a FunctionProto message from the specified reader or buffer, length delimited.
         * @function decodeDelimited
         * @memberof onnx.FunctionProto
         * @static
         * @param {$protobuf.Reader|Uint8Array} reader Reader or buffer to decode from
         * @returns {onnx.FunctionProto & onnx.FunctionProto.$Shape} FunctionProto
         * @throws {Error} If the payload is not a reader or valid buffer
         * @throws {$protobuf.util.ProtocolError} If required fields are missing
         */
        FunctionProto.decodeDelimited = function(reader) {
            if (!(reader instanceof $Reader))
                reader = new $Reader(reader);
            return this.decode(reader, reader.uint32());
        };

        /**
         * Verifies a FunctionProto message.
         * @function verify
         * @memberof onnx.FunctionProto
         * @static
         * @param {Object.<string,*>} message Plain object to verify
         * @returns {string|null} `null` if valid, otherwise the reason why it is not
         */
        FunctionProto.verify = function (message, _depth) {
            if (typeof message !== "object" || message === null)
                return "object expected";
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                return "max depth exceeded";
            if (message.name != null && $Object.hasOwnProperty.call(message, "name"))
                if (!$util.isString(message.name))
                    return "name: string expected";
            if (message.input != null && $Object.hasOwnProperty.call(message, "input")) {
                if (!$Array.isArray(message.input))
                    return "input: array expected";
                for (let i = 0; i < message.input.length; ++i)
                    if (!$util.isString(message.input[i]))
                        return "input: string[] expected";
            }
            if (message.output != null && $Object.hasOwnProperty.call(message, "output")) {
                if (!$Array.isArray(message.output))
                    return "output: array expected";
                for (let i = 0; i < message.output.length; ++i)
                    if (!$util.isString(message.output[i]))
                        return "output: string[] expected";
            }
            if (message.attribute != null && $Object.hasOwnProperty.call(message, "attribute")) {
                if (!$Array.isArray(message.attribute))
                    return "attribute: array expected";
                for (let i = 0; i < message.attribute.length; ++i)
                    if (!$util.isString(message.attribute[i]))
                        return "attribute: string[] expected";
            }
            if (message.attributeProto != null && $Object.hasOwnProperty.call(message, "attributeProto")) {
                if (!$Array.isArray(message.attributeProto))
                    return "attributeProto: array expected";
                for (let i = 0; i < message.attributeProto.length; ++i) {
                    let error = $root.onnx.AttributeProto.verify(message.attributeProto[i], _depth + 1);
                    if (error)
                        return "attributeProto." + error;
                }
            }
            if (message.node != null && $Object.hasOwnProperty.call(message, "node")) {
                if (!$Array.isArray(message.node))
                    return "node: array expected";
                for (let i = 0; i < message.node.length; ++i) {
                    let error = $root.onnx.NodeProto.verify(message.node[i], _depth + 1);
                    if (error)
                        return "node." + error;
                }
            }
            if (message.docString != null && $Object.hasOwnProperty.call(message, "docString"))
                if (!$util.isString(message.docString))
                    return "docString: string expected";
            if (message.opsetImport != null && $Object.hasOwnProperty.call(message, "opsetImport")) {
                if (!$Array.isArray(message.opsetImport))
                    return "opsetImport: array expected";
                for (let i = 0; i < message.opsetImport.length; ++i) {
                    let error = $root.onnx.OperatorSetIdProto.verify(message.opsetImport[i], _depth + 1);
                    if (error)
                        return "opsetImport." + error;
                }
            }
            if (message.domain != null && $Object.hasOwnProperty.call(message, "domain"))
                if (!$util.isString(message.domain))
                    return "domain: string expected";
            if (message.overload != null && $Object.hasOwnProperty.call(message, "overload"))
                if (!$util.isString(message.overload))
                    return "overload: string expected";
            if (message.valueInfo != null && $Object.hasOwnProperty.call(message, "valueInfo")) {
                if (!$Array.isArray(message.valueInfo))
                    return "valueInfo: array expected";
                for (let i = 0; i < message.valueInfo.length; ++i) {
                    let error = $root.onnx.ValueInfoProto.verify(message.valueInfo[i], _depth + 1);
                    if (error)
                        return "valueInfo." + error;
                }
            }
            if (message.metadataProps != null && $Object.hasOwnProperty.call(message, "metadataProps")) {
                if (!$Array.isArray(message.metadataProps))
                    return "metadataProps: array expected";
                for (let i = 0; i < message.metadataProps.length; ++i) {
                    let error = $root.onnx.StringStringEntryProto.verify(message.metadataProps[i], _depth + 1);
                    if (error)
                        return "metadataProps." + error;
                }
            }
            return null;
        };

        /**
         * Creates a FunctionProto message from a plain object. Also converts values to their respective internal types.
         * @function fromObject
         * @memberof onnx.FunctionProto
         * @static
         * @param {Object.<string,*>} object Plain object
         * @returns {onnx.FunctionProto} FunctionProto
         */
        FunctionProto.fromObject = function (object, _depth) {
            if (object instanceof $root.onnx.FunctionProto)
                return object;
            if (!$util.isObject(object))
                throw $TypeError(".onnx.FunctionProto: object expected");
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                throw $Error("max depth exceeded");
            let message = new $root.onnx.FunctionProto();
            if (object.name != null)
                message.name = $String(object.name);
            if (object.input) {
                if (!$Array.isArray(object.input))
                    throw $TypeError(".onnx.FunctionProto.input: array expected");
                message.input = $Array(object.input.length);
                for (let i = 0; i < object.input.length; ++i)
                    message.input[i] = $String(object.input[i]);
            }
            if (object.output) {
                if (!$Array.isArray(object.output))
                    throw $TypeError(".onnx.FunctionProto.output: array expected");
                message.output = $Array(object.output.length);
                for (let i = 0; i < object.output.length; ++i)
                    message.output[i] = $String(object.output[i]);
            }
            if (object.attribute) {
                if (!$Array.isArray(object.attribute))
                    throw $TypeError(".onnx.FunctionProto.attribute: array expected");
                message.attribute = $Array(object.attribute.length);
                for (let i = 0; i < object.attribute.length; ++i)
                    message.attribute[i] = $String(object.attribute[i]);
            }
            if (object.attributeProto) {
                if (!$Array.isArray(object.attributeProto))
                    throw $TypeError(".onnx.FunctionProto.attributeProto: array expected");
                message.attributeProto = $Array(object.attributeProto.length);
                for (let i = 0; i < object.attributeProto.length; ++i) {
                    if (!$util.isObject(object.attributeProto[i]))
                        throw $TypeError(".onnx.FunctionProto.attributeProto: object expected");
                    message.attributeProto[i] = $root.onnx.AttributeProto.fromObject(object.attributeProto[i], _depth + 1);
                }
            }
            if (object.node) {
                if (!$Array.isArray(object.node))
                    throw $TypeError(".onnx.FunctionProto.node: array expected");
                message.node = $Array(object.node.length);
                for (let i = 0; i < object.node.length; ++i) {
                    if (!$util.isObject(object.node[i]))
                        throw $TypeError(".onnx.FunctionProto.node: object expected");
                    message.node[i] = $root.onnx.NodeProto.fromObject(object.node[i], _depth + 1);
                }
            }
            if (object.docString != null)
                message.docString = $String(object.docString);
            if (object.opsetImport) {
                if (!$Array.isArray(object.opsetImport))
                    throw $TypeError(".onnx.FunctionProto.opsetImport: array expected");
                message.opsetImport = $Array(object.opsetImport.length);
                for (let i = 0; i < object.opsetImport.length; ++i) {
                    if (!$util.isObject(object.opsetImport[i]))
                        throw $TypeError(".onnx.FunctionProto.opsetImport: object expected");
                    message.opsetImport[i] = $root.onnx.OperatorSetIdProto.fromObject(object.opsetImport[i], _depth + 1);
                }
            }
            if (object.domain != null)
                message.domain = $String(object.domain);
            if (object.overload != null)
                message.overload = $String(object.overload);
            if (object.valueInfo) {
                if (!$Array.isArray(object.valueInfo))
                    throw $TypeError(".onnx.FunctionProto.valueInfo: array expected");
                message.valueInfo = $Array(object.valueInfo.length);
                for (let i = 0; i < object.valueInfo.length; ++i) {
                    if (!$util.isObject(object.valueInfo[i]))
                        throw $TypeError(".onnx.FunctionProto.valueInfo: object expected");
                    message.valueInfo[i] = $root.onnx.ValueInfoProto.fromObject(object.valueInfo[i], _depth + 1);
                }
            }
            if (object.metadataProps) {
                if (!$Array.isArray(object.metadataProps))
                    throw $TypeError(".onnx.FunctionProto.metadataProps: array expected");
                message.metadataProps = $Array(object.metadataProps.length);
                for (let i = 0; i < object.metadataProps.length; ++i) {
                    if (!$util.isObject(object.metadataProps[i]))
                        throw $TypeError(".onnx.FunctionProto.metadataProps: object expected");
                    message.metadataProps[i] = $root.onnx.StringStringEntryProto.fromObject(object.metadataProps[i], _depth + 1);
                }
            }
            return message;
        };

        /**
         * Creates a plain object from a FunctionProto message. Also converts values to other types if specified.
         * @function toObject
         * @memberof onnx.FunctionProto
         * @static
         * @param {onnx.FunctionProto} message FunctionProto
         * @param {$protobuf.IConversionOptions} [options] Conversion options
         * @returns {Object.<string,*>} Plain object
         */
        FunctionProto.toObject = function (message, options, _depth) {
            if (!options)
                options = {};
            if (_depth === $undefined)
                _depth = 0;
            if (_depth > $util.recursionLimit)
                throw $Error("max depth exceeded");
            let object = {};
            if (options.arrays || options.defaults) {
                object.input = [];
                object.output = [];
                object.attribute = [];
                object.node = [];
                object.opsetImport = [];
                object.attributeProto = [];
                object.valueInfo = [];
                object.metadataProps = [];
            }
            if (options.defaults) {
                object.name = "";
                object.docString = "";
                object.domain = "";
                object.overload = "";
            }
            if (message.name != null && $Object.hasOwnProperty.call(message, "name"))
                object.name = message.name;
            if (message.input && message.input.length) {
                object.input = $Array(message.input.length);
                for (let j = 0; j < message.input.length; ++j)
                    object.input[j] = message.input[j];
            }
            if (message.output && message.output.length) {
                object.output = $Array(message.output.length);
                for (let j = 0; j < message.output.length; ++j)
                    object.output[j] = message.output[j];
            }
            if (message.attribute && message.attribute.length) {
                object.attribute = $Array(message.attribute.length);
                for (let j = 0; j < message.attribute.length; ++j)
                    object.attribute[j] = message.attribute[j];
            }
            if (message.node && message.node.length) {
                object.node = $Array(message.node.length);
                for (let j = 0; j < message.node.length; ++j)
                    object.node[j] = $root.onnx.NodeProto.toObject(message.node[j], options, _depth + 1);
            }
            if (message.docString != null && $Object.hasOwnProperty.call(message, "docString"))
                object.docString = message.docString;
            if (message.opsetImport && message.opsetImport.length) {
                object.opsetImport = $Array(message.opsetImport.length);
                for (let j = 0; j < message.opsetImport.length; ++j)
                    object.opsetImport[j] = $root.onnx.OperatorSetIdProto.toObject(message.opsetImport[j], options, _depth + 1);
            }
            if (message.domain != null && $Object.hasOwnProperty.call(message, "domain"))
                object.domain = message.domain;
            if (message.attributeProto && message.attributeProto.length) {
                object.attributeProto = $Array(message.attributeProto.length);
                for (let j = 0; j < message.attributeProto.length; ++j)
                    object.attributeProto[j] = $root.onnx.AttributeProto.toObject(message.attributeProto[j], options, _depth + 1);
            }
            if (message.valueInfo && message.valueInfo.length) {
                object.valueInfo = $Array(message.valueInfo.length);
                for (let j = 0; j < message.valueInfo.length; ++j)
                    object.valueInfo[j] = $root.onnx.ValueInfoProto.toObject(message.valueInfo[j], options, _depth + 1);
            }
            if (message.overload != null && $Object.hasOwnProperty.call(message, "overload"))
                object.overload = message.overload;
            if (message.metadataProps && message.metadataProps.length) {
                object.metadataProps = $Array(message.metadataProps.length);
                for (let j = 0; j < message.metadataProps.length; ++j)
                    object.metadataProps[j] = $root.onnx.StringStringEntryProto.toObject(message.metadataProps[j], options, _depth + 1);
            }
            return object;
        };

        /**
         * Converts this FunctionProto to JSON.
         * @function toJSON
         * @memberof onnx.FunctionProto
         * @instance
         * @returns {Object.<string,*>} JSON object
         */
        FunctionProto.prototype.toJSON = function() {
            return FunctionProto.toObject(this, $protobuf.util.toJSONOptions);
        };

        /**
         * Gets the type url for FunctionProto
         * @function getTypeUrl
         * @memberof onnx.FunctionProto
         * @static
         * @param {string} [prefix] Custom type url prefix, defaults to `"type.googleapis.com"`
         * @returns {string} The type url
         */
        FunctionProto.getTypeUrl = function(prefix) {
            if (prefix === $undefined)
                prefix = "type.googleapis.com";
            return prefix + "/onnx.FunctionProto";
        };

        return FunctionProto;
    })();

    return onnx;
})();

export {
  $root as default
};
