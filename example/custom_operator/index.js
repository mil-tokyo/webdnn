let runner;

window.addEventListener("DOMContentLoaded", async () => {
  srcCanvas = document.getElementById("source");
  resultCanvas = document.getElementById("result");
  updateMessage("Loading model");

  runner = await WebDNN.load("output/", {optimized: true});
  updateMessage(`Model loaded (backend: ${runner.backendName})`);
});

function updateMessage(message) {
  document.getElementById("msg").innerText = message;
}

async function run() {
  const cols = 4, rows = 3;
  const inputArray = new Float32Array(cols * rows);
  for (let i = 0; i < inputArray.length; i++) {
    inputArray[i] = Math.random() - 0.5;
  }
  const input = new WebDNN.CPUTensor([rows, cols], "float32", inputArray);

  const [output] = await runner.run([input]);

  displayResult(input, output);

  updateMessage(`Completed`);
}

function displayResult(input, output) {
  const resultDom = document.getElementById("result");
  while (resultDom.firstChild) {
    resultDom.removeChild(resultDom.firstChild);
  }

  const inputTensorDom = displayTensor(input);
  const outputTensorDom = displayTensor(output);
  resultDom.appendChild(inputTensorDom);
  resultDom.appendChild(document.createTextNode("⇒"));
  resultDom.appendChild(outputTensorDom);
}

function displayTensor(tensor) {
  const element = document.createElement("table");
  let html = "<tbody>";
  for (let row = 0; row < tensor.dims[0]; row++) {
    html += "<tr>";
    for (let col = 0; col < tensor.dims[1]; col++) {
      html += `<td>${tensor.getValue([row, col]).toFixed(2)}</td>`;
    }
    html += "</tr>";
  }
  html += "</tbody>";
  element.innerHTML = html;
  return element;
}