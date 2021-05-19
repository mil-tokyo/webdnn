function wait() {
  return new Promise((resolve) => {
    setTimeout(resolve, 1);
  });
}

async function runOnce(runner, expectedTensors, validateResult) {
  const inputTensors = runner
    .getInputNames()
    .map((iname) => expectedTensors.get(iname));
  const startTime = Date.now();
  const outputTensors = await runner.run(inputTensors);
  const endTime = Date.now();
  let errorMessage = null;
  if (validateResult) {
    const isClose = (expected, actual, name) => {
      if (expected.dims.length !== actual.dims.length) {
        return `${name}: expected.dims(${expected.dims}) !== actual.dims(${actual.dims})`;
      }
      if (expected.dims.some((nd, i) => nd !== actual.dims[i])) {
        return `${name}: expected.dims(${expected.dims}) !== actual.dims(${actual.dims})`;
      }

      if (expected.data.length !== actual.data.length) {
        return `${name}: data length mismatch`;
      }

      for (let i = 0; i < expected.data.length; i++) {
        const e = expected.data[i];
        const a = actual.data[i];
        if (Math.abs(e - a) > Math.abs(e) * 1e-3 + 1e-5) {
          // let kvs = "";
          // for (let j = 0; j < Math.min(2048, expected.data.length); j++) {
          //   kvs += `${j}=${actual.data[j]},`;
          // }
          // return `${kvs}`;
          return `${name}: index ${i}, expected ${e} !== actual ${a}`;
        }
      }

      return null;
    };
    const outputNames = runner.getOutputNames();
    for (let i = 0; i < outputNames.length; i++) {
      const oname = outputNames[i];
      errorMessage = isClose(
        expectedTensors.get(oname),
        outputTensors[i],
        oname
      );
      if (errorMessage) {
        break;
      }
    }
  }

  return { time: endTime - startTime, validationError: errorMessage };
}

async function runBenchmark(optimized) {
  const backend = document.getElementById("backend").value;
  const model = document.getElementById("model").value;
  if (!model || !backend) {
    return;
  }
  location.hash = `#backend=${backend}&model=${model}`;

  const backendOrder = backend === "cpu" ? [backend] : [backend, "cpu"];
  const directory = `./model/${model}/`;

  const runner = await WebDNN.load(
    optimized ? `${directory}optimized/` : directory,
    { backendOrder, optimized }
  );

  const expectedTensors = await runner
    .getTensorLoader(directory + "expected.bin")
    .loadAll();

  // warm up
  const warmupResult = await runOnce(runner, expectedTensors, true);
  if (warmupResult.validationError) {
    document.getElementById("result").innerText = "Output validation error";
    return;
  }
  await wait();

  const nTrial = 10;
  const times = [];
  for (let i = 0; i < nTrial; i++) {
    console.log(`Trial ${i}`);
    const trialResult = await runOnce(runner, expectedTensors, false);
    await wait();
    times.push(trialResult.time);
  }

  const avg = times.reduce((p, c) => p + c, 0) / nTrial;
  const max = Math.max(...times);
  const min = Math.min(...times);
  document.getElementById(
    "result"
  ).innerText = `Model ${model}, backend ${backend}, average ${avg} ms, min ${min} ms, max ${max} ms`;
}

window.addEventListener("DOMContentLoaded", async () => {
  const cases = await (await fetch("./model/cases.json")).json();
  const modelDom = document.getElementById("model");
  for (const caseName of cases) {
    const opt = document.createElement("option");
    opt.value = caseName;
    opt.innerText = caseName;
    modelDom.appendChild(opt);
  }
  const usp = new URLSearchParams(location.hash.substring(1));
  const backend = usp.get("backend") || "webgl";
  const model = usp.get("model") || "";
  document.getElementById("backend").value = backend;
  document.getElementById("model").value = model;
});
