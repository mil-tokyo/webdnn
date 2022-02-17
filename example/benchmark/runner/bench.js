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
        if (!(Math.abs(e - a) <= Math.abs(e) * 1e-2 + 1e-3)) {
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

function displayMessage(message) {
  document.getElementById("result").innerText = message;
}

async function runBenchmark(optimized, measure) {
  try {
    const backend = document.getElementById("backend").value;
    const model = document.getElementById("model").value;
    if (!model || !backend) {
      return;
    }
    const webgl_max_allocation_bytes = document.getElementById(
      "webgl_max_allocation_bytes"
    ).value;
    const webgl_deallocate_to_bytes = document.getElementById(
      "webgl_deallocate_to_bytes"
    ).value;
    const webgl_version = document.getElementById("webgl_version").value;
    location.hash = `#backend=${backend}&model=${model}&webgl_max_allocation_bytes=${webgl_max_allocation_bytes}&webgl_deallocate_to_bytes=${webgl_deallocate_to_bytes}&webgl_version=${webgl_version}`;
    const validateResult = document.getElementById(
      "enableValidateResult"
    ).checked;
    displayMessage("Running benchmark");

    const backendOrder = backend === "cpu" ? [backend] : [backend, "cpu"];
    const directory = `./model/${model}/`;

    if (measure) {
      const logging = WebDNN.Logging.getInstance();
      logging.config({
        adapters: {
          console: {
            adapter: "console",
            loglevel: {
              "": WebDNN.Logging.WARN,
            },
          },
          file: {
            adapter: "file",
            loglevel: {
              "": WebDNN.Logging.DEBUG,
            },
          },
        },
      });
    }

    const backendOptions = {
      webgl: {
        maxAllocationBytes: Number(webgl_max_allocation_bytes) * 1024 * 1024,
        deallocateToBytes: Number(webgl_deallocate_to_bytes) * 1024 * 1024,
        versionOrder: webgl_version ? [webgl_version] : undefined,
      },
    };

    const runner = await WebDNN.load(
      optimized ? `${directory}optimized/` : directory,
      { backendOrder, optimized, backendOptions }
    );

    const expectedTensors = await runner
      .getTensorLoader(directory + "expected.bin")
      .loadAll();

    // warm up
    // run multiple times makes JIT optimize JavaScript part
    for (let i = 0; i < 3; i++) {
      console.log(`Warmup ${i}`);
      const warmupResult = await runOnce(
        runner,
        expectedTensors,
        validateResult
      );
      if (warmupResult.validationError) {
        displayMessage(
          `Output validation error: ${warmupResult.validationError}`
        );
        return;
      }
      await wait();
    }

    if (measure) {
      const logging = WebDNN.Logging.getInstance();
      logging.clear();
    }

    const nTrial = measure ? 1 : 10;
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
    displayMessage(
      `Model ${model}, backend ${backend}, average ${avg} ms, min ${min} ms, max ${max} ms`
    );

    if (measure) {
      const logging = WebDNN.Logging.getInstance();
      logging.adapters.file.saveToLocalFile();
    }
  } catch (error) {
    alert(`Error: ${error.message}`);
    displayMessage(`Error: ${error.message}`);
  }
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
  document.getElementById("backend").value = usp.get("backend") || "webgl";
  document.getElementById("model").value = usp.get("model") || "";
  document.getElementById("webgl_max_allocation_bytes").value =
    usp.get("webgl_max_allocation_bytes") || "1024";
  document.getElementById("webgl_deallocate_to_bytes").value =
    usp.get("webgl_deallocate_to_bytes") || "512";
  document.getElementById("webgl_version").value =
    usp.get("webgl_version") || "";
});
