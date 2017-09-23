declare function require(path: string): any;

const IS_IOS_SAFARI = /iPhone/.test(navigator.userAgent) &&
    /Safari/.test(navigator.userAgent) &&
    !(/CriOS/.test(navigator.userAgent)) &&
    !(/FxiOS/.test(navigator.userAgent));

export class UnsupportedError extends Error {
}

interface MediaDeviceInfo {
    deviceId: string
    groupId: string
    kind: 'videoinput' | 'audioinput' | 'audiooutput'
    label: string
}

type FacingMode = 'environment' | 'user';

export default class WebCam {
    private ready: Promise<void>;
    private deviceInfoMap: Map<string, MediaDeviceInfo>;
    private activeMediaStream: MediaStream | null = null;
    private activeFacingMode: FacingMode = 'user';

    constructor() {
        if (!('mediaDevices' in navigator)) throw new UnsupportedError('"navigator.mediaDevices" is not supported in this browser');

        this.ready = this.initAsync();
    }

    async initAsync() {
        let deviceInfos = await (navigator.mediaDevices.enumerateDevices() as Promise<MediaDeviceInfo[]>);

        deviceInfos = deviceInfos
            .filter(info => info.kind == 'videoinput');

        this.deviceInfoMap = new Map(deviceInfos.map(info => [info.deviceId, info] as [string, MediaDeviceInfo]));
    }

    /**
     * Return next device's media stream
     * @returns {Promise<MediaStream>}
     */
    async getNextDeviceStream(): Promise<MediaStream> {
        if (this.activeMediaStream) {
            this.deactivateMediaStream();
        }

        let newFacingMode: FacingMode = this.activeFacingMode == 'user' ? 'environment' : 'user';
        let stream: MediaStream;
        try {
            stream = await this.getStream(newFacingMode);
        } catch (err) {
            console.error(err);
            newFacingMode = this.activeFacingMode;
            stream = await this.getStream(newFacingMode);
        }

        this.activeFacingMode = newFacingMode;
        this.activeMediaStream = stream;
        return stream;
    }

    private deactivateMediaStream() {
        let stream = this.activeMediaStream;
        if (!stream) return;

        stream.getTracks().forEach(track => track.stop());
        this.activeMediaStream = null;
    }

    private async getStream(facingMode: FacingMode): Promise<MediaStream> {
        console.log('facingMode', facingMode);
        await this.ready;

        if (IS_IOS_SAFARI && 'getUserMedia' in navigator) {
            return new Promise<MediaStream>((resolve, reject) => {
                navigator.getUserMedia({
                    video: {
                        facingMode: { exact: facingMode }
                    }
                }, resolve, reject)
            });
        } else {
            return await navigator.mediaDevices.getUserMedia({
                video: {
                    facingMode: facingMode
                }
            });
        }
    }
}