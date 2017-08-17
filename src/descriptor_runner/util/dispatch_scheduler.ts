/**
 * @module webdnn
 */
/** Don't Remove This comment block */

/**
 * @private
 */
const NOT_SCHEDULED = -1;

/**
 * Schedule function which is called too much frequently.
 *
 * @private
 */
export default class DispatchScheduler {
    private scheduledCallbackId: number = NOT_SCHEDULED;
    private fn: () => any;

    /**
     * Register scheduled function. If already other function is scheduled, it is canceled and dispatcher will dispatch only
     * function which is registered at last.
     * @param fn scheduled function
     */
    request(fn: () => any) {
        this.fn = fn;
        if (this.scheduledCallbackId == NOT_SCHEDULED) {
            this.scheduledCallbackId = requestAnimationFrame(() => this.forceDispatch());
        }
    }

    /**
     * Dispatch scheduled function just now. If no function is scheduled, dispatcher do nothing.
     */
    forceDispatch() {
        if (this.scheduledCallbackId == NOT_SCHEDULED) return;

        this.cancel();
        this.fn();
    }

    /**
     * Cancel scheduled function. If no function is scheduled, dispatcher do nothing.
     */
    cancel() {
        if (this.scheduledCallbackId == NOT_SCHEDULED) return;

        cancelAnimationFrame(this.scheduledCallbackId);
        this.scheduledCallbackId = NOT_SCHEDULED;
    }
}
