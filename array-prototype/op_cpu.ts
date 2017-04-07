namespace WebDNN {
  export function add(a: MatrixCPU, b: MatrixCPU): MatrixCPU;
  export function add(a: MatrixGPUFallback, b: MatrixGPUFallback): MatrixGPUFallback;
  export function add(a: MatrixCPU | MatrixGPUFallback, b: MatrixCPU | MatrixGPUFallback): MatrixCPU | MatrixGPUFallback {
    let ans: MatrixCPU | MatrixGPUFallback;
    if (a instanceof MatrixCPU) {
      ans = new MatrixCPU(a.shape);
    } else if (a instanceof MatrixGPUFallback) {
      ans = new MatrixGPUFallback(a.shape);
    }
    let size = a.size;
    let a_data = a.data;
    let b_data = b.data;
    let ans_data = ans.data;
    for (let i = 0; i < size; i++) {
      ans_data[i] = a_data[i] + b_data[i];
    }

    return ans;
  }
  export function sub(a: MatrixCPU, b: MatrixCPU): MatrixCPU;
  export function sub(a: MatrixGPUFallback, b: MatrixGPUFallback): MatrixGPUFallback;
  export function sub(a: MatrixCPU | MatrixGPUFallback, b: MatrixCPU | MatrixGPUFallback): MatrixCPU | MatrixGPUFallback {
    let ans: MatrixCPU | MatrixGPUFallback;
    if (a instanceof MatrixCPU) {
      ans = new MatrixCPU(a.shape);
    } else if (a instanceof MatrixGPUFallback) {
      ans = new MatrixGPUFallback(a.shape);
    }
    let size = a.size;
    let a_data = a.data;
    let b_data = b.data;
    let ans_data = ans.data;
    for (let i = 0; i < size; i++) {
      ans_data[i] = a_data[i] - b_data[i];
    }

    return ans;
  }
  export function mul(a: MatrixCPU, b: MatrixCPU): MatrixCPU;
  export function mul(a: MatrixGPUFallback, b: MatrixGPUFallback): MatrixGPUFallback;
  export function mul(a: MatrixCPU | MatrixGPUFallback, b: MatrixCPU | MatrixGPUFallback): MatrixCPU | MatrixGPUFallback {
    let ans: MatrixCPU | MatrixGPUFallback;
    if (a instanceof MatrixCPU) {
      ans = new MatrixCPU(a.shape);
    } else if (a instanceof MatrixGPUFallback) {
      ans = new MatrixGPUFallback(a.shape);
    }
    let size = a.size;
    let a_data = a.data;
    let b_data = b.data;
    let ans_data = ans.data;
    for (let i = 0; i < size; i++) {
      ans_data[i] = a_data[i] * b_data[i];
    }

    return ans;
  }
  export function div(a: MatrixCPU, b: MatrixCPU): MatrixCPU;
  export function div(a: MatrixGPUFallback, b: MatrixGPUFallback): MatrixGPUFallback;
  export function div(a: MatrixCPU | MatrixGPUFallback, b: MatrixCPU | MatrixGPUFallback): MatrixCPU | MatrixGPUFallback {
    let ans: MatrixCPU | MatrixGPUFallback;
    if (a instanceof MatrixCPU) {
      ans = new MatrixCPU(a.shape);
    } else if (a instanceof MatrixGPUFallback) {
      ans = new MatrixGPUFallback(a.shape);
    }
    let size = a.size;
    let a_data = a.data;
    let b_data = b.data;
    let ans_data = ans.data;
    for (let i = 0; i < size; i++) {
      ans_data[i] = a_data[i] / b_data[i];
    }

    return ans;
  }
/*  export function XXX(a: MatrixCPU, b: MatrixCPU): MatrixCPU;
  export function XXX(a: MatrixGPUFallback, b: MatrixGPUFallback): MatrixGPUFallback;
  export function XXX(a: MatrixCPU | MatrixGPUFallback, b: MatrixCPU | MatrixGPUFallback): MatrixCPU | MatrixGPUFallback {
    let ans: MatrixCPU | MatrixGPUFallback;
    if (a instanceof MatrixCPU) {
      ans = new MatrixCPU(a.shape);
    } else if (a instanceof MatrixGPUFallback) {
      ans = new MatrixGPUFallback(a.shape);
    }
    let size = a.size;
    let a_data = a.data;
    let b_data = b.data;
    let ans_data = ans.data;
    for (let i = 0; i < size; i++) {
      ans_data[i] = a_data[i] YYY b_data[i];
    }

    return ans;
  }*/
}
