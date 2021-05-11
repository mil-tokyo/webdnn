function wait() {
  return new Promise((resolve) => {
    setTimeout(resolve, 1);
  });
}

async function runTest(optimized) {
  let caseDirs = [];
  const resultDom = document.getElementById("result");
  const previousResultList = document.getElementById("resultList");
  if (previousResultList) {
    resultDom.removeChild(previousResultList);
  }
  const resultList = document.createElement("ol");
  resultDom.appendChild(resultList);

  // URLに?case=xxx があればケースxxxだけを実行
  const usp = new URLSearchParams(location.search);
  const selectedCase = usp.get("case");
  if (selectedCase) {
    caseDirs.push(`model/${selectedCase}/`);
  } else {
    const listJSON = await (await fetch("model/cases.json")).json();
    for (const name of listJSON) {
      caseDirs.push(`model/${name}/`);
    }
  }
  const checkboxes = document.getElementsByName("backend");
  const backendOrders = [["cpu"]];
  for (const checkbox of checkboxes) {
    if (checkbox.checked) {
      backendOrders.push([checkbox.value, "cpu"]);
    }
  }
  let allOk = true;
  const allResults = {};
  for (const caseDir of caseDirs) {
    for (const backendOrder of backendOrders) {
      console.log("test", caseDir, backendOrder);
      const ok = await runTestOne(caseDir, backendOrder, optimized);
      allOk &= ok;
      allResults[caseDir] = ok;
      resultList.innerHTML += `<li><span class="${
        ok ? "result-ok" : "result-fail"
      }">${ok ? "OK" : "Fail"}, ${caseDir}, ${backendOrder[0]}</span></li>`;
      await wait();
    }
  }
  console.log("done all test");
  if (allOk) {
    console.log("all ok");
    resultList.innerHTML += `<li><span class="result-ok">Done. All cases OK.</span></li>`;
  } else {
    console.error("failed", allResults);resultList.innerHTML += `<li><span class="result-fail">Some cases failed.</span></li>`;
  }
}

async function runTestOne(directory, backendOrder, optimized) {
  const runner = await WebDNN.load(optimized ? `${directory}optimized/` : directory, { backendOrder, optimized });
  const expectedTensors = await runner
    .getTensorLoader(directory + "expected.bin")
    .loadAll();
  const inputTensors = runner
    .getInputNames()
    .map((iname) => expectedTensors.get(iname));
  console.time(`Run ${directory}`);
  const outputTensors = await runner.run(inputTensors);
  console.timeEnd(`Run ${directory}`);
  const isClose = (expected, actual, name) => {
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
      if (Math.abs(e - a) > Math.abs(e) * 1e-3 + 1e-5) {
        console.error(`${name}: index ${i}, expected ${e} !== actual ${a}`);
        return false;
      }
    }

    return true;
  };

  const check = runner
    .getOutputNames()
    .every((oname, i) =>
      isClose(expectedTensors.get(oname), outputTensors[i], oname)
    );
  return check;
}

window.addEventListener("DOMContentLoaded", async () => {
  const usp = new URLSearchParams(location.search);
  const backends = (usp.get("backend") || "").split(",");
  const checkboxes = document.getElementsByName("backend");
  for (const checkbox of checkboxes) {
    if (backends.includes(checkbox.value)) {
      checkbox.checked = true;
    }
  }
});
