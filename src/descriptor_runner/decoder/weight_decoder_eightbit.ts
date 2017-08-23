/**
 * @module webdnn
 */
/** Don't Remove This comment block */

import WeightDecoder from "./weight_decoder";

/**
 * @private
 */
declare const Zlib: any;

/**
 * @protected
 */
export default class WeightDecoderEightbit implements WeightDecoder {
    static decode_table = [0.0, 2.750000021e-06, 7.249999726e-06, 1.875000089e-05, 3.624999954e-05, 5.874999624e-05, 8.624999464e-05,
        1.437500032e-04, 2.312500001e-04, 3.187500115e-04, 4.062500084e-04, 5.187499919e-04, 6.562499912e-04,
        7.937499322e-04, 9.312499315e-04, 1.218750025e-03, 1.656249980e-03, 2.093750052e-03, 2.531250007e-03,
        2.968749963e-03, 3.406249918e-03, 3.843750106e-03, 4.281249829e-03, 4.843750037e-03, 5.531250034e-03,
        6.218749564e-03, 6.906249560e-03, 7.593749557e-03, 8.281249553e-03, 8.968749084e-03, 9.656248614e-03,
        1.109374966e-02, 1.328125037e-02, 1.546875015e-02, 1.765624993e-02, 1.984374970e-02, 2.203124948e-02,
        2.421874925e-02, 2.640625089e-02, 2.859375067e-02, 3.078125045e-02, 3.296874836e-02, 3.515625000e-02,
        3.734375164e-02, 3.953124955e-02, 4.171875119e-02, 4.390624911e-02, 4.671875015e-02, 5.015625060e-02,
        5.359374732e-02, 5.703124776e-02, 6.046874821e-02, 6.390624493e-02, 6.734374911e-02, 7.078124583e-02,
        7.421874255e-02, 7.765624672e-02, 8.109374344e-02, 8.453124017e-02, 8.796874434e-02, 9.140624106e-02,
        9.484373778e-02, 9.828124195e-02, 1.054687500e-01, 1.164062470e-01, 1.273437440e-01, 1.382812560e-01,
        1.492187530e-01, 1.601562500e-01, 1.710937470e-01, 1.820312440e-01, 1.929687560e-01, 2.039062530e-01,
        2.148437500e-01, 2.257812470e-01, 2.367187440e-01, 2.476562560e-01, 2.585937381e-01, 2.695312500e-01,
        2.804687619e-01, 2.914062440e-01, 3.023437560e-01, 3.132812381e-01, 3.242187500e-01, 3.351562619e-01,
        3.460937440e-01, 3.570312560e-01, 3.679687381e-01, 3.789062500e-01, 3.898437619e-01, 4.007812440e-01,
        4.117187560e-01, 4.226562381e-01, 4.335937500e-01, 4.445312619e-01, 4.585937560e-01, 4.757812321e-01,
        4.929687381e-01, 5.101562142e-01, 5.273437500e-01, 5.445312262e-01, 5.617187023e-01, 5.789062381e-01,
        5.960937142e-01, 6.132812500e-01, 6.304687262e-01, 6.476562023e-01, 6.648437381e-01, 6.820312142e-01,
        6.992186904e-01, 7.164062262e-01, 7.335937023e-01, 7.507811785e-01, 7.679687142e-01, 7.851561904e-01,
        8.023436666e-01, 8.195312023e-01, 8.367186785e-01, 8.539061546e-01, 8.710936904e-01, 8.882811666e-01,
        9.054686427e-01, 9.226561785e-01, 9.398436546e-01, 9.570311308e-01, 9.742186666e-01, 9.914061427e-01, 1.0,
    ];

    async decode(data: Uint8Array): Promise<Float32Array> {
        // FIXME: store decoded total size in 'data'
        // currently, decoding each block and concatenating them at the end are needed.
        let decoded_arrays: Float32Array[] = [];
        let total_dst_length = 0;
        let data_view = new DataView(data.buffer, data.byteOffset);
        let src_offset = 0;
        while (src_offset < data.length) {
            let dst_offset = data_view.getInt32(src_offset, true);
            src_offset += 4;
            let body_size = data_view.getInt32(src_offset, true);
            src_offset += 4;
            let scale = data_view.getFloat32(src_offset, true);
            src_offset += 8;
            let scaled_table = new Float32Array(256);
            for (let i = 0; i < 256; i++) {
                scaled_table[i] = WeightDecoderEightbit.decode_table[i & 0x7F] * scale * (i < 128 ? 1.0 : -1.0);
            }

            // do decode
            let src_data_view = new Uint8Array(data.buffer, data.byteOffset + src_offset, body_size);
            let inflate = new Zlib.Inflate(src_data_view);
            let decompressed = inflate.decompress();
            let dec_size = decompressed.length;
            let decoded_array = new Float32Array(dec_size);
            for (let s = 0; s < dec_size; s++) {
                decoded_array[s] = scaled_table[decompressed[s]];
            }
            decoded_arrays.push(decoded_array);
            total_dst_length += dec_size;
            src_offset += body_size;
        }
        let dst = new Float32Array(total_dst_length);
        let dst_offset = 0;
        for (let i = 0; i < decoded_arrays.length; i++) {
            dst.set(decoded_arrays[i], dst_offset);
            dst_offset += decoded_arrays[i].length;
        }
        return dst;
    }
}
