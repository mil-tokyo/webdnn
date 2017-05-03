///<reference path="./weight_decoder.ts" />
///<reference path="./weight_decoder_raw.ts" />
///<reference path="./weight_decoder_eightbit.ts" />

namespace WebDNN {
    export function get_weight_decoder(name: string): WeightDecoder {
        switch (name) {
            case 'raw':
                return new WeightDecoderRaw();
            case 'eightbit':
                return new WeightDecoderEightbit();
            default:
                throw new Error('Unknown weight encoding');
        }
    }
}
