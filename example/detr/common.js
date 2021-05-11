const coco_classes = [
  "N/A",
  "person",
  "bicycle",
  "car",
  "motorcycle",
  "airplane",
  "bus",
  "train",
  "truck",
  "boat",
  "traffic light",
  "fire hydrant",
  "N/A",
  "stop sign",
  "parking meter",
  "bench",
  "bird",
  "cat",
  "dog",
  "horse",
  "sheep",
  "cow",
  "elephant",
  "bear",
  "zebra",
  "giraffe",
  "N/A",
  "backpack",
  "umbrella",
  "N/A",
  "N/A",
  "handbag",
  "tie",
  "suitcase",
  "frisbee",
  "skis",
  "snowboard",
  "sports ball",
  "kite",
  "baseball bat",
  "baseball glove",
  "skateboard",
  "surfboard",
  "tennis racket",
  "bottle",
  "N/A",
  "wine glass",
  "cup",
  "fork",
  "knife",
  "spoon",
  "bowl",
  "banana",
  "apple",
  "sandwich",
  "orange",
  "broccoli",
  "carrot",
  "hot dog",
  "pizza",
  "donut",
  "cake",
  "chair",
  "couch",
  "potted plant",
  "bed",
  "N/A",
  "dining table",
  "N/A",
  "N/A",
  "toilet",
  "N/A",
  "tv",
  "laptop",
  "mouse",
  "remote",
  "keyboard",
  "cell phone",
  "microwave",
  "oven",
  "toaster",
  "sink",
  "refrigerator",
  "N/A",
  "book",
  "clock",
  "vase",
  "scissors",
  "teddy bear",
  "hair drier",
  "toothbrush",
];

let resultCanvas, srcCanvas;
let srcImageSize;

function outputTransform(pred_logits, pred_boxes, im_size) {
  const n_queries = pred_logits.dims[1];
  const n_classes_p1 = pred_logits.dims[2];
  const pred_softmax = new WebDNN.CPUTensor([n_queries, n_classes_p1]);
  for (let q = 0; q < n_queries; q++) {
    let max = -Infinity;
    for (let c = 0; c < n_classes_p1; c++) {
      max = Math.max(max, pred_logits.getValue([0, q, c]));
    }
    let sum_exp = 0;
    for (let c = 0; c < n_classes_p1; c++) {
      const exp = Math.exp(pred_logits.getValue([0, q, c]));
      pred_softmax.setValue(exp, [q, c]);
      sum_exp += exp;
    }
    for (let c = 0; c < n_classes_p1; c++) {
      pred_softmax.setValue(pred_softmax.getValue([q, c]) / sum_exp, [q, c]);
    }
  }

  const n_classes = n_classes_p1 - 1;
  const probas_all = new WebDNN.CPUTensor([n_queries, n_classes]);
  for (let q = 0; q < n_queries; q++) {
    for (let c = 0; c < n_classes; c++) {
      probas_all.setValue(pred_softmax.getValue([q, c]), [q, c]);
    }
  }

  const keep = [];
  for (let q = 0; q < n_queries; q++) {
    let max_prob = 0;
    for (let c = 0; c < n_classes; c++) {
      max_prob = Math.max(max_prob, probas_all.getValue([q, c]));
    }
    if (max_prob > 0.7) {
      keep.push(q);
    }
  }

  const bboxes_scaled = new WebDNN.CPUTensor([keep.length, 4]);
  for (let qk = 0; qk < keep.length; qk++) {
    const x_c = pred_boxes.getValue([0, keep[qk], 0]);
    const y_c = pred_boxes.getValue([0, keep[qk], 1]);
    const w = pred_boxes.getValue([0, keep[qk], 2]);
    const h = pred_boxes.getValue([0, keep[qk], 3]);
    bboxes_scaled.setValue((x_c - 0.5 * w) * im_size[0], [qk, 0]);
    bboxes_scaled.setValue((y_c - 0.5 * h) * im_size[1], [qk, 1]);
    bboxes_scaled.setValue((x_c + 0.5 * w) * im_size[0], [qk, 2]);
    bboxes_scaled.setValue((y_c + 0.5 * h) * im_size[1], [qk, 3]);
  }
  const probas = new WebDNN.CPUTensor([keep.length, n_classes]);
  for (let qk = 0; qk < keep.length; qk++) {
    for (let c = 0; c < n_classes; c++) {
      probas.setValue(probas_all.getValue([keep[qk], c]), [qk, c]);
    }
  }
  return { probas, bboxes_scaled };
}

function displayResult(bboxes) {
  const ctx = resultCanvas.getContext("2d");
  ctx.drawImage(srcCanvas, 0, 0);
  let i = 3;
  for (const bbox of bboxes) {
    let color = `hsl(${i * 60}, 100%, 75%)`;
    let colorf = `hsla(${i * 60}, 100%, 50%, 0.5)`;
    i++;
    ctx.strokeStyle = color;
    ctx.lineWidth = 3;
    ctx.strokeRect(bbox.x, bbox.y, bbox.width, bbox.height);

    ctx.font = "20px sans-serif";
    const text = `${bbox.className}: ${bbox.probability}`;
    const metrics = ctx.measureText(text);
    console.log(metrics);
    ctx.fillStyle = colorf;
    const yofs = -2;
    const bpad = 2;
    let textX = bbox.x;
    let textY = bbox.y + yofs;
    let textBX = textX + metrics.actualBoundingBoxLeft - bpad;
    let textBY = textY - metrics.actualBoundingBoxAscent - bpad;
    let textWidth = metrics.width + 2 * bpad;
    let textHeight =
      metrics.actualBoundingBoxAscent -
      metrics.actualBoundingBoxDescent +
      2 * bpad;
    if (textBX < 0) {
      const ofs = -textBX;
      textX += ofs;
      textBX += ofs;
    }
    if (textBX + textWidth >= resultCanvas.width) {
      const ofs = resultCanvas.width - textBX + textWidth;
      textX += ofs;
      textBX += ofs;
    }
    if (textBY < 0) {
      const ofs = -textBY;
      textY += ofs;
      textBY += ofs;
    }
    if (textBY + textHeight >= resultCanvas.height) {
      const ofs = resultCanvas.height - textBY + textHeight;
      textY += ofs;
      textBY += ofs;
    }
    ctx.fillRect(textBX, textBY, textWidth, textHeight);
    ctx.fillStyle = color;
    ctx.fillText(text, textX, textY);
  }
}

function computeBboxInfo(probas, bboxes_scaled) {
  const bboxes = [];

  for (let q = 0; q < bboxes_scaled.dims[0]; q++) {
    const x0 = bboxes_scaled.getValue([q, 0]);
    const y0 = bboxes_scaled.getValue([q, 1]);
    const x1 = bboxes_scaled.getValue([q, 2]);
    const y1 = bboxes_scaled.getValue([q, 3]);
    let max_prob = 0;
    let max_class = 0;
    for (let c = 0; c < probas.dims[1]; c++) {
      const p = probas.getValue([q, c]);
      if (p > max_prob) {
        max_prob = p;
        max_class = c;
      }
    }
    bboxes.push({
      x: x0,
      y: y0,
      width: x1 - x0,
      height: y1 - y0,
      className: coco_classes[max_class],
      probability: max_prob.toFixed(2),
    });
  }

  return bboxes;
}

/**
 * ResNet50での出力画像サイズを計算する
 * @param {number} imageDim 画像の幅または高さ
 * @returns
 */
function calcEmbedDim(imageDim) {
  let dim = imageDim;
  for (let i = 0; i < 5; i++) {
    dim = Math.floor((dim - 1) / 2) + 1;
  }
  return dim;
}

function makeEmbed(h, w, rowEmbed, colEmbed) {
  const embedH = calcEmbedDim(h);
  const embedW = calcEmbedDim(w);
  const embedDim = rowEmbed.dims[1];
  const embed = new WebDNN.CPUTensor([embedH * embedW, 1, embedDim * 2]);
  for (let y = 0; y < embedH; y++) {
    for (let x = 0; x < embedW; x++) {
      for (let e = 0; e < embedDim; e++) {
        embed.setValue(colEmbed.getValue([x, e]), [y * embedW + x, 0, e]);
        embed.setValue(rowEmbed.getValue([y, e]), [
          y * embedW + x,
          0,
          e + embedDim,
        ]);
      }
    }
  }
  return embed;
}

let inputArrays, runner;

async function loadModel(directory) {
  runner = await WebDNN.load(directory, {backendOrder: ["webgl", "cpu"]});
  inputArrays = await runner
  .getTensorLoader(directory + "embedding.bin")
  .loadAll();
}

function updateSrcImage(image) {
  srcImageSize = { width: image.width, height: image.height };
  srcCanvas.width = srcImageSize.width;
  srcCanvas.height = srcImageSize.height;
  resultCanvas.width = srcImageSize.width;
  resultCanvas.height = srcImageSize.height;
  const srcCtx = srcCanvas.getContext("2d");
  srcCtx.drawImage(image, 0, 0);
  const resultCtx = resultCanvas.getContext("2d");
  resultCtx.drawImage(image, 0, 0);
}

function loadDefaultImage() {
  const image = new Image();
  image.onload = () => {
    updateSrcImage(image);
  };
  image.src = `output/000000039769.jpg`;
}

function updateMessage(message) {
  document.getElementById("msg").innerText = message;
}
