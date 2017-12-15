/**
 * Webcam library
 *
 * (C) Yuichiro Kikura (y.kikura@gmail.com), MIT License, 2017.
 */

"use strict";

const IS_IOS_SAFARI = /iPhone/.test(navigator.userAgent) &&
    /Safari/.test(navigator.userAgent) &&
    !(/CriOS/.test(navigator.userAgent)) &&
    !(/FxiOS/.test(navigator.userAgent));

class UnsupportedError extends Error {
}

class WebCam {
    constructor() {
        this.activeMediaStream = null;
        this.activeFacingMode = 'user';
        if (!('mediaDevices' in navigator))
            throw new UnsupportedError('"navigator.mediaDevices" is not supported in this browser');
        this.ready = this.initAsync();
    }

    async initAsync() {
        let deviceInfos = await navigator.mediaDevices.enumerateDevices();
        deviceInfos = deviceInfos
            .filter(info => info.kind == 'videoinput');
        this.deviceInfoMap = new Map(deviceInfos.map(info => [info.deviceId, info]));
    }

    /**
     * Return next device's media stream
     * @returns {Promise<MediaStream>}
     */
    async getNextDeviceStream() {
        if (this.activeMediaStream) {
            this.deactivateMediaStream();
        }
        let newFacingMode = this.activeFacingMode == 'user' ? 'environment' : 'user';
        let stream;
        try {
            stream = await this.getStream(newFacingMode);
        }
        catch (err) {
            console.error(err);
            newFacingMode = this.activeFacingMode;
            stream = await this.getStream(newFacingMode);
        }
        this.activeFacingMode = newFacingMode;
        this.activeMediaStream = stream;
        return stream;
    }

    deactivateMediaStream() {
        let stream = this.activeMediaStream;
        if (!stream)
            return;
        stream.getTracks().forEach(track => track.stop());
        this.activeMediaStream = null;
    }

    async getStream(facingMode) {
        console.log('facingMode', facingMode);
        await this.ready;
        if (IS_IOS_SAFARI && 'getUserMedia' in navigator) {
            return new Promise((resolve, reject) => {
                navigator.getUserMedia({
                    video: {
                        facingMode: {exact: facingMode}
                    }
                }, resolve, reject);
            });
        }
        else {
            return await navigator.mediaDevices.getUserMedia({
                video: {
                    facingMode: facingMode
                }
            });
        }
    }
}
