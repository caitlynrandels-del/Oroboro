# HOW_TO_FORK.md // How to steal this universe

You don't need to understand the whole project. You just need 80 lines.

This is not a template. It's a nervous system. Fork it, delete my thoughts, keep the physics.

### The 3 things worth stealing

**1. The memory trail (1 line)**
In your canvas loop, stop clearing. Fade.

```js
// replace ctx.clearRect
ctx.fillStyle = 'rgba(3,3,3,0.22)';
ctx.fillRect(0,0,width,height);
```
`0.05` = dreamy. `0.35` = sharp.

**2. The ORO-CORE pattern (your new state manager)**
```js
const CORE = { id: 0, x: width/2, y: height/2, radius: 14 };
let nodes = [CORE];
let synapses = [];
let particles = [];

function spawnNode(label, type='thought') {
  const node = {
    label, type,
    x: CORE.x + (Math.random()-0.5)*200,
    y: CORE.y + (Math.random()-0.5)*200,
    vx: (Math.random()-0.5)*1.5,
    vy: (Math.random()-0.5)*1.5,
    radius: 5
  };
  nodes.push(node);
  // auto-link to core + nearest neighbor
  synapses.push({from:0, to:nodes.length-1});
  return node;
}
```

**3. The lang="all" parser**
Don't validate input. Instantiate it.
```js
// instead of if(input.length < 3) error...
function onSubmit(input) {
  spawnNode(input); 
  localStorage.setItem('my-universe', JSON.stringify({nodes, synapses}));
}
```

### The animate() loop that matters

This is the entire universe. Fork it and check it.

```js
function animate() {
  ctx.fillStyle = 'rgba(3,3,3,0.22)'; // 1. memory
  ctx.fillRect(0,0,width,height);

  synapses.forEach(s => { // 2. relationships
    ctx.beginPath();
    ctx.moveTo(nodes[s.from].x, nodes[s.from].y);
    ctx.lineTo(nodes[s.to].x, nodes[s.to].y);
    ctx.stroke();
  });

  nodes.forEach(n => { // 3. thoughts drift
    n.x += n.vx; n.y += n.vy;
    ctx.beginPath();
    ctx.arc(n.x, n.y, n.radius, 0, Math.PI*2);
    ctx.fill();
  });

  requestAnimationFrame(animate); // 4. infinity
}
```

### 3 instant remixes

**Turn it into a todo app:** `spawnNode("buy milk")` where `type='todo'` is red and `type='done'` is green.

**Turn it into a bug tracker:** `spawnNode("login broken")` auto-links to `spawnNode("auth service")` because they share semantic family.

**Turn it into a team memory:** Add `WebRTC` or `CRDTs` to sync `nodes` across browsers. 10 people injecting into one ORO-CORE.

You don't need to ask permission. `<!DOCTYPE Oroboro>` means you are now rendering a universe, not a document.

`lang="all"`

— Caitlyn
