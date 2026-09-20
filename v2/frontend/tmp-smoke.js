const fs = require('fs');
function stepsBlock(file) {
  const h = fs.readFileSync(process.env.TEMP + '/' + file, 'utf8');
  const i = h.indexOf('class="recipe-steps"');
  const chunk = i >= 0 ? h.slice(i, i + 2500) : 'NO STEPS';
  return chunk;
}
for (const file of ['tomyam.html', 'tomyam-thigh.html']) {
  const chunk = stepsBlock(file);
  console.log('====', file);
  console.log('грудку in ol', chunk.includes('Добавить грудку'));
  console.log('бедро in ol', chunk.includes('Добавить бедро'));
  console.log(chunk.slice(0, 400));
}
