namespace WebDNN {
  export function add(a: MatrixCPU, b: MatrixCPU): MatrixCPU;
  export function add(a: MatrixGPUFallback, b: MatrixGPUFallback): MatrixGPUFallback;
  export function add(a: MatrixCPU | MatrixGPUFallback, b: MatrixCPU | MatrixGPUFallback): MatrixCPU | MatrixGPUFallback {
    if (a instanceof MatrixGPUFallback) {
      var ans = new MatrixGPUFallback(a.shape);
    } else {
      var ans = new MatrixCPU(a.shape);
    }
    var size = a.size;
    var a_data = a.data;
    var b_data = b.data;
    var ans_data = ans.data;
    for (let i = 0; i < size; i++) {
      ans_data[i] = a_data[i] + b_data[i];
    }

    return ans;
  }

  export function sub(a: MatrixCPU, b: MatrixCPU): MatrixCPU;
  export function sub(a: MatrixGPUFallback, b: MatrixGPUFallback): MatrixGPUFallback;
  export function sub(a: MatrixCPU | MatrixGPUFallback, b: MatrixCPU | MatrixGPUFallback): MatrixCPU | MatrixGPUFallback {
    if (a instanceof MatrixGPUFallback) {
      var ans = new MatrixGPUFallback(a.shape);
    } else {
      var ans = new MatrixCPU(a.shape);
    }
    var size = a.size;
    var a_data = a.data;
    var b_data = b.data;
    var ans_data = ans.data;
    for (let i = 0; i < size; i++) {
      ans_data[i] = a_data[i] - b_data[i];
    }

    return ans;
  }

  export function mul(a: MatrixCPU, b: MatrixCPU): MatrixCPU;
  export function mul(a: MatrixGPUFallback, b: MatrixGPUFallback): MatrixGPUFallback;
  export function mul(a: MatrixCPU | MatrixGPUFallback, b: MatrixCPU | MatrixGPUFallback): MatrixCPU | MatrixGPUFallback {
    if (a instanceof MatrixGPUFallback) {
      var ans = new MatrixGPUFallback(a.shape);
    } else {
      var ans = new MatrixCPU(a.shape);
    }
    var size = a.size;
    var a_data = a.data;
    var b_data = b.data;
    var ans_data = ans.data;
    for (let i = 0; i < size; i++) {
      ans_data[i] = a_data[i] * b_data[i];
    }

    return ans;
  }

  export function div(a: MatrixCPU, b: MatrixCPU): MatrixCPU;
  export function div(a: MatrixGPUFallback, b: MatrixGPUFallback): MatrixGPUFallback;
  export function div(a: MatrixCPU | MatrixGPUFallback, b: MatrixCPU | MatrixGPUFallback): MatrixCPU | MatrixGPUFallback {
    if (a instanceof MatrixGPUFallback) {
      var ans = new MatrixGPUFallback(a.shape);
    } else {
      var ans = new MatrixCPU(a.shape);
    }
    var size = a.size;
    var a_data = a.data;
    var b_data = b.data;
    var ans_data = ans.data;
    for (let i = 0; i < size; i++) {
      ans_data[i] = a_data[i] / b_data[i];
    }

    return ans;
  }
  /*  export function sub(a: MatrixCPU, b: MatrixCPU): MatrixCPU;
    export function sub(a: MatrixGPUFallback, b: MatrixGPUFallback): MatrixGPUFallback;
    export function sub(a: MatrixCPU | MatrixGPUFallback, b: MatrixCPU | MatrixGPUFallback): MatrixCPU | MatrixGPUFallback {
      if (a instanceof MatrixGPUFallback) {
        var ans = new MatrixGPUFallback(a.shape);
      } else {
        var ans = new MatrixCPU(a.shape);
      }
      var size = a.size;
      var a_data = a.data;
      var b_data = b.data;
      var ans_data = ans.data;
      for (let i = 0; i < size; i++) {
        ans_data[i] = a_data[i] YYY b_data[i];
      }
  
      return ans;
    }*/
}
