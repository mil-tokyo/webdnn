let resultCanvas, srcCanvas;
let srcImageSize;
let inputArrays, runner;

async function loadModel(directory) {
  const optimized =location.pathname.includes("optimized");
  const usp = new URLSearchParams(location.search);
  const backendOrder = (usp.get("backend") || "webgl").split(",");
  if (!backendOrder.includes("cpu")) {
    backendOrder.push("cpu");
  }
  const options = {backendOrder};
  if (optimized) {
    directory += "optimized/"
    options.optimized = true;
    options.progressCallback = (loaded, total) => {
      updateMessage(`Loading model: ${loaded} / ${total} bytes`);
    };
  }
  runner = await WebDNN.load(directory, options);
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

function displayTopClasses(pred_scores) {
  const records = [];
  for (let i = 0; i < imagenet_classes.length; i++) {
    records.push([imagenet_classes[i], pred_scores.getValue([0, i])]);
  }
  records.sort((a, b) => b[1] - a[1]); //sort in reverse order of probability
  console.log(records);

  const tbody = document.getElementById("result-lines");
  let innerHTML = "";

  for (let i = 0; i < 5; i++) {
    innerHTML += `<tr><td>${records[i][0]}</td><td>${
      (records[i][1] * 100) | 0
    }%</td></tr>`;
  }
  tbody.innerHTML = innerHTML;
}

async function run() {
  const timeStart = Date.now();
  const w = 224;
  const h = 224;

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

  const [pred_scores] = await runner.run([transformedImage]);

  const timeElapsed = Date.now() - timeStart;
  displayTopClasses(pred_scores);

  updateMessage(`Elapsed: ${timeElapsed} ms`);
}
