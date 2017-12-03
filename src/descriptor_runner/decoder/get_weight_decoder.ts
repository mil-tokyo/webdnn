/**
 * @module webdnn
 */
/** Don't Remove This comment block */

import WeightDecoder from "./weight_decoder";
import WeightDecoderEightbit from "./weight_decoder_eightbit";
import WeightDecoderRaw from "./weight_decoder_raw";

/**
 * @protected
 */
export default function getWeightDecoder(name: string): WeightDecoder {
    switch (name) {
        case 'raw':
            return new WeightDecoderRaw();
        case 'eightbit':
            return new WeightDecoderEightbit();
        default:
            throw new Error('Unknown weight encoding');
    }
}
