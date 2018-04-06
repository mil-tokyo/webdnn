/**
 * @module webdnn/image
 */

/** Don't Remove This comment block */

/**
 * The data order
 */
export enum Order {
    /** `[Channel, Height, Width]` format */
    CHW,

        /** `[Height, Width, Channel]` format */
    HWC
}

/**
 * The color format
 */
export enum Color {
    /** RGB format */
    RGB,

        /** BGR format */
    BGR,

        /** grey scale */
    GREY,

    /** RGBA format */
    RGBA,

    /** BGRA format */
    BGRA,

}
