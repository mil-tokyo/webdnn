import { getOpEntries as getOpEntriesCPU } from "../operators/cpu/opEntriesAll";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
declare let WebDNN: any;

function injectOperators() {
  console.log("injecting wasm operators");
  if (WebDNN.injectOperators) {
    WebDNN.injectOperators({ operatorEntries: [...getOpEntriesCPU()] });
  } else {
    console.error(
      "WebDNN.injectOperators not found. webdnn-core.js seems to be not imported."
    );
  }
}

injectOperators();
