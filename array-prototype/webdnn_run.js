var $M, $Mg;

async function main() {
  $M = WebDNN;
  let backend = await $M.init();
  console.log(`backend: ${backend}`);
  $Mg = $M.gpu;

  // demo
  let m_a = new $M.MatrixCPU([2, 2], new Float32Array([1, 2, 3, 5.1]));
  let m_b = new $M.MatrixCPU([2, 2], new Float32Array([2, 3, 5, 2.3]));
  let mg_a = $Mg.toGPU(m_a);
  let mg_b = $Mg.toGPU(m_b);
  let mg_c = $Mg.add(mg_a, mg_b);
  let m_c = await $Mg.toCPU(mg_c);
  console.log(`${m_a.data} + ${m_b.data} = ${m_c.data}`);
}
