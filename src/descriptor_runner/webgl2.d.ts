declare namespace WebGL2RenderingContext {
}


declare class WebGL2RenderingContext extends WebGLRenderingContext {
    RED: GLenum;
    RGBA32F: GLenum;
    R32F: GLenum;
    SYNC_GPU_COMMANDS_COMPLETE: GLenum;
    ALREADY_SIGNALED: GLenum;
    CONDITION_SATISFIED: GLenum;

    createVertexArray(): WebGLVertexArrayObject;

    bindVertexArray(vertexArray: WebGLVertexArrayObject): void;

    fenceSync(condition: GLenum, flags: GLbitfield): WebGLSync;

    clientWaitSync(sync: WebGLSync, flags: GLbitfield, timeout: 0): GLenum;

    deleteSync(sync: WebGLSync): void;
}

declare class WebGLVertexArrayObject {

}

declare class WebGLSync {

}

declare interface WebGLVertexArrayObjectExtension {
    bindVertexArrayOES(vertexArray: WebGLVertexArrayObject): void;

    createVertexArrayOES(): WebGLVertexArrayObject;
}
