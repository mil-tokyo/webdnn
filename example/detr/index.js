function initDragDrop() {
  resultCanvas.addEventListener("dragover", (event) => {
    event.preventDefault();
  });

  resultCanvas.addEventListener("drop", (event) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    if (file) {
      const image = new Image();
      const reader = new FileReader();
      reader.onload = (readerEv) => {
        image.onload = () => {
          updateSrcImage(image);
        };
        image.src = readerEv.target.result;
      };
      reader.readAsDataURL(file);
    }
  });
}

window.addEventListener("DOMContentLoaded", async () => {
  srcCanvas = document.getElementById("source");
  resultCanvas = document.getElementById("result");
  updateMessage("Loading model");

  initDragDrop();
  loadDefaultImage();
  await loadModel("output/");
  updateMessage(`Model loaded (backend: ${runner.backendName})`);
});

async function run() {
  const timeStart = Date.now();
  const w = Number(document.getElementById("rescaleWidth").value);
  const h = Math.round(srcImageSize.height * (w / srcImageSize.width));

  const imageArray = await WebDNN.Image.getImageArray(srcCanvas, {
    dstW: w,
    dstH: h,
    color: WebDNN.Image.Color.RGB,
    order: WebDNN.Image.Order.CHW,
    bias: [0.485 * 255, 0.456 * 255, 0.406 * 255],
    scale: [0.229 * 255, 0.224 * 255, 0.225 * 255],
  });
  const transformedImage = new WebDNN.CPUTensor(
    [1, 3, h, w],
    "float32",
    imageArray
  );
  const embedPos = makeEmbed(
    h,
    w,
    inputArrays.get("row_embed"),
    inputArrays.get("col_embed")
  );

  const [pred_logits, pred_boxes] = await runner.run([
    transformedImage,
    embedPos,
    inputArrays.get("query_pos_us"),
  ]);

  const { probas, bboxes_scaled } = outputTransform(pred_logits, pred_boxes, [
    srcImageSize.width,
    srcImageSize.height,
  ]);
  const bboxes = computeBboxInfo(probas, bboxes_scaled);
  const timeElapsed = Date.now() - timeStart;
  console.log(JSON.stringify(bboxes));
  displayResult(bboxes);
  updateMessage(`Elapsed: ${timeElapsed} ms`);
}

const sampleResult = [
  {
    x: 16.653976440429688,
    y: 52.35057067871094,
    width: 292.99012756347656,
    height: 416.5459442138672,
    className: "cat",
    probability: "1.00",
  },
  {
    x: 39.0250358581543,
    y: 70.67089080810547,
    width: 136.10809707641602,
    height: 43.70653533935547,
    className: "remote",
    probability: "1.00",
  },
  {
    x: 342.2518005371094,
    y: 22.124719619750977,
    width: 297.6031188964844,
    height: 348.1928462982178,
    className: "cat",
    probability: "1.00",
  },
  {
    x: 0.4102325439453125,
    y: 1.1359834671020508,
    width: 639.8812103271484,
    height: 472.57141399383545,
    className: "couch",
    probability: "0.88",
  },
  {
    x: 0.10654449462890625,
    y: 0.6757020950317383,
    width: 639.9820175170898,
    height: 474.05180644989014,
    className: "bed",
    probability: "0.93",
  },
  {
    x: 336.30902099609375,
    y: 78.0080795288086,
    width: 29.0863037109375,
    height: 111.13500213623047,
    className: "remote",
    probability: "0.78",
  },
];

function displaySampleResult() {
  displayResult(sampleResult);
}
