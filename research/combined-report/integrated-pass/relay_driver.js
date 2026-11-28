// Persistent driver around caitlynrandels-del/oroboro-relay OroboroPipeline (oroboro-core.js @ d3d0940,
// read-only clone). One JSON line in = one pipeline tick; one JSON line out.
// in: {register:{sectorId:{flights,status}}, radio:[text...], local:{sectorId:{flights,status}}}
const path = process.argv[2];
const { OroboroPipeline } = require(path);
const restLevy = parseInt(process.argv[3] || '10', 10);
const pipe = new OroboroPipeline({ alpha: 0.35, gain: 0.08, restLevy, pressureLimit: 0.5 });
const rl = require('readline').createInterface({ input: process.stdin });
rl.on('line', (line) => {
  const msg = JSON.parse(line);
  for (const [id, d] of Object.entries(msg.register || {})) {
    const prev = pipe.nexus.registry.get(id);
    // keep ISOLATED status set by mesh consensus until the next registration clears it via recombine
    pipe.nexus.register(id, { flights: d.flights, status: d.status });
  }
  for (const id of Array.from(pipe.nexus.registry.keys())) {
    if (id !== 'genesis' && !(id in (msg.register || {}))) pipe.nexus.registry.delete(id);
  }
  const s = pipe.tick(msg.radio || [], msg.local || {});
  const crit = (msg.radio || []).map(t => pipe.transcriber.isCritical(t));
  process.stdout.write(JSON.stringify({ ...s, critical: crit, metrics: pipe.nexus.metrics,
    chronicles: pipe.transcriber.chronicles.length, anon: pipe.transcriber.anonymousLog.length }) + '\n');
});
