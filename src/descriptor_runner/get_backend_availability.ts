namespace WebDNN {
    function getBackendAvailabilityWebGPU() {
        return 'WebGPUComputeCommandEncoder' in window;
    }

    function getBackendAvailabilityWebAssembly() {
        return 'Worker' in window;
    }

    function getBackendAvailabilityFallback() {
        return true;
    }

    /**
     * Check backend availability
     * @returns List of backend availability and default selected backend order
     */
    export function getBackendAvailability() {
        let status: { [name: string]: boolean } = {
            'webgpu': getBackendAvailabilityWebGPU(),
            'webassembly': getBackendAvailabilityWebAssembly(),
            'fallback': getBackendAvailabilityFallback()
        };

        let order = ['webgpu', 'webassembly', 'fallback'].filter(backend => status[backend]);

        return {
            status: status,
            defaultOrder: order
        }
    }
}
