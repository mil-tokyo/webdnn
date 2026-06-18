import { getOpEntries as getOpEntriesCPU } from "../operators/cpu/opEntriesAll";
import { getOpEntries as getOpEntriesWebGL } from "../operators/webgl/opEntriesAll";

declare let WebDNN: any;

function injectOperators() {
  if (WebDNN.injectOperators) {
    WebDNN.injectOperators({
      operatorEntries: [...getOpEntriesCPU(), ...getOpEntriesWebGL()],
    });
  } else {
    console.error(
      "WebDNN.injectOperators not found. webdnn-core.js seems to be not imported.",
    );
  }
}

injectOperators();
