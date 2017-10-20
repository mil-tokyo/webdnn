((global) => {
    const IS_IOS_SAFARI = /iPhone/.test(navigator.userAgent) &&
        /Safari/.test(navigator.userAgent) &&
        !(/CriOS/.test(navigator.userAgent)) &&
        !(/FxiOS/.test(navigator.userAgent));

    class UnsupportedError extends Error {
    }

    const FacingMode = {
        Environment: 'environment',
        User: 'user'
    };

    class WebCam {
        constructor() {
            if (!('mediaDevices' in navigator)) throw new UnsupportedError('"navigator.mediaDevices" is not supported in this browser');

            this.activeFacingMode = null;
            this.activeMediaStream = null;
        }

        async getNextDeviceStream() {
            if (this.activeMediaStream) {
                this._deactivateMediaStream();
            }

            let newFacingMode = this.activeFacingMode === FacingMode.User ? FacingMode.Environment : FacingMode.User;
            let stream;
            try {
                stream = await this._getStream(newFacingMode);
            } catch (err) {
                console.error(err);
                newFacingMode = this.activeFacingMode;
                stream = await this._getStream(newFacingMode);
            }

            this.activeFacingMode = newFacingMode;
            this.activeMediaStream = stream;
            return stream;
        }

        _deactivateMediaStream() {
            let stream = this.activeMediaStream;
            if (!stream) return;

            stream.getTracks().forEach(track => track.stop());
            this.activeMediaStream = null;
        }

        async _getStream(facingMode) {
            console.log('facingMode', facingMode);
            await this.ready;

            if (IS_IOS_SAFARI && 'getUserMedia' in navigator) {
                return new Promise((resolve, reject) => {
                    navigator.getUserMedia({
                        video: {
                            facingMode: {exact: facingMode}
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

    global.WebCam = WebCam;
})(this);
