function isClose(expected, actual, name, rtol = 1e-3, atol = 1e-5) {
  if (expected.dims.length !== actual.dims.length) {
    console.error(
      `${name}: expected.dims(${expected.dims}) !== actual.dims(${actual.dims})`
    );
    return false;
  }
  if (expected.dims.some((nd, i) => nd !== actual.dims[i])) {
    console.error(
      `${name}: expected.dims(${expected.dims}) !== actual.dims(${actual.dims})`
    );
    return false;
  }

  if (expected.data.length !== actual.data.length) {
    console.error(`${name}: data length mismatch`);
    return false;
  }

  for (let i = 0; i < expected.data.length; i++) {
    const e = expected.data[i];
    const a = actual.data[i];
    // NaNの場合にエラーになるようにしている
    if (!(Math.abs(e - a) <= Math.abs(e) * rtol + atol)) {
      console.error(`${name}: index ${i}, expected ${e} !== actual ${a}`);
      return false;
    }
  }

  return true;
}

let testCaseTensors;

window.addEventListener("DOMContentLoaded", async () => {
  srcCanvas = document.getElementById("source");
  resultCanvas = document.getElementById("result");
  updateMessage("Loading model");

  loadDefaultImage();
  await loadModel("output/");
  testCaseTensors = await runner.getTensorLoader("output/test.bin").loadAll();
  updateMessage(`Model loaded (backend: ${runner.backendName})`);
});

const imageRescaleW = 1066,
  imageRescaleH = 800;

async function testEmbedding() {
  console.log("Testing position embedding generation");
  const embed = makeEmbed(
    imageRescaleH,
    imageRescaleW,
    inputArrays.get("row_embed"),
    inputArrays.get("col_embed")
  );
  console.log(
    "Match:",
    isClose(testCaseTensors.get("input_embed_const"), embed, "pos")
  );
}

async function testDNN() {
  console.log("Testing DNN core only");
  const [pred_logits, pred_boxes] = await runner.run([
    testCaseTensors.get("input_0"),
    testCaseTensors.get("input_embed_const"),
    inputArrays.get("query_pos_us"),
  ]);

  console.log(
    "Match of pred_logits:",
    isClose(
      testCaseTensors.get("output_logits"),
      pred_logits,
      "pred_logits",
      1e-2,
      1e-3
    )
  );
  console.log(
    "Match of pred_boxes:",
    isClose(
      testCaseTensors.get("output_boxes"),
      pred_boxes,
      "pred_boxes",
      1e-2,
      1e-3
    )
  );
}

// full pipelineは誤差が大きい
// 画像リサイズのわずかなアルゴリズム差で入力が変化し、その結果出力が大きく変化（特に物体なしのbounding box）
// 意味的にはあまり変わらない出力となるが、要素単位の一致をしない
async function testFull() {
  console.log("Testing full pipeline");

  const imageArray = await WebDNN.Image.getImageArray(srcCanvas, {
    dstW: imageRescaleW,
    dstH: imageRescaleH,
    color: WebDNN.Image.Color.RGB,
    order: WebDNN.Image.Order.CHW,
    bias: [0.485 * 255, 0.456 * 255, 0.406 * 255],
    scale: [0.229 * 255, 0.224 * 255, 0.225 * 255],
  });
  const transformedImage = new WebDNN.CPUTensor(
    [1, 3, imageRescaleH, imageRescaleW],
    "float32",
    imageArray
  );
  const embedPos = makeEmbed(
    imageRescaleH,
    imageRescaleW,
    inputArrays.get("row_embed"),
    inputArrays.get("col_embed")
  );

  const [pred_logits, pred_boxes] = await runner.run([
    transformedImage,
    embedPos,
    inputArrays.get("query_pos_us"),
  ]);

  console.log(
    "Match of pred_logits:",
    isClose(
      testCaseTensors.get("output_logits"),
      pred_logits,
      "pred_logits",
      0.1,
      0.01
    )
  );
  console.log(
    "Match of pred_boxes:",
    isClose(
      testCaseTensors.get("output_boxes"),
      pred_boxes,
      "pred_boxes",
      0.1,
      0.01
    )
  );
}
