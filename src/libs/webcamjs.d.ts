declare let Webcam: {
    set: (config: { [key: string]: any }) => void;
    on: (type: string, handler: (...args: any[]) => any) => void;
    off: (type: string, handler: (...args: any[]) => any) => void;
    attach: (query: string) => void;
    reset: () => void;
    snap: (callback: (...args: any[])=>any, cnavas: HTMLCanvasElement) => void;
};