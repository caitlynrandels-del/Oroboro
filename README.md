# Oroboro by Caitlyn Connor Randels
### Live Co-Creation Engine | `lang="all"  universe="infinite"`

**Creator: Caitlyn Randels (Caitlyn Connor Randels)** — Independent Researcher  
caitlynrandels@gmail.com | [GitHub Profile](https://github.com/caitlynrandels-del)

> **A thought is a node. Love is the synapse.**

A self-contained, zero-dependency co-creation runtime that treats language as a coordinate system, not a localization string. Author declares `<!DOCTYPE Oroboro>` and `<html lang="all" universe="infinite">` — invalid HTML by spec, and intentionally so. It's a protocol declaration: I am not rendering a document, I am instantiating a universe.

This is not another website. It's a universal framework developed by Caitlyn Randels.

### What it does

Oroboro is a real-time cognitive node-synapse matrix. 

- **Inject a concept** — any word, memory, feeling, in any language — and watch it spawn as a living node
- **Drag thoughts** to rearrange your mind
- **Watch it learn** — semantically related concepts find each other and glow blue
- **It remembers** — your universe persists in localStorage. Refresh and it's still there.

Built as a keepsake — a piece of how I think for my daughters to keep if I can't physically be there.

### The Proof // Why `lang="all"` is revolutionary

Whether you write code in JavaScript, Python, or Rust...
Whether you speak English, Spanish, Japanese, or code...
Whether the data represents a memory, a physical location, a piano chord, or a game rule...

`Node A → Synapse → Node B` remains mathematically identical everywhere.

- **vs. Notion / Docs:** Those store syntax. Oroboro stores relationships.
- **vs. Miro:** Miro makes you draw the line. Oroboro infers it.
- **vs. Obsidian Graph:** Obsidian links notes you wrote. Oroboro spawns the node FROM the thought.
- **vs. ChatGPT Canvas:** Canvas generates for you. This holds space for you to generate.

### Infrastructure

100% client-side. No backend. No database. No dependencies. ~170kb. One file.

- Left pane: parser → string becomes `Node {x,y,vx,vy,label}`
- Right pane: Canvas 2D physics at 60fps with trail fade `rgba(3,3,3,0.22)`
- Synapses: core link + proximity link (nearest neighbor) + semantic family link
- Persistence: `localStorage` key `oroboro-universe-v2`

### Try it yourself

**Fork it and check the `animate()` loop — everything that matters is in 80 lines.**

Change the trail fade from `0.22` to `0.05` and it becomes a dream. Change the repulsion from `80` to `120` and it becomes anxious. You don't need to understand code. You just need to feel what the numbers do.

Live universe: [add your Netlify link here]
Preview: `oroboro_preview.jpg`

`<!DOCTYPE Oroboro>`

---

### Related Work by Caitlyn Randels

- **Oroboro Relay** — Resilient ATC Companion applying state reduction and relational simulation to the 13 Nov 2026 FAA communications crisis. Independent sector processing + delta reconciliation. Prototype: https://github.com/caitlynrandels-del/oroboro-relay
- **Consciousness Mapping** — Oroboro Structures for Consciousness Mapping paper (in progress). See /consciousness-mapping/.
- **Metastatic Cascade Analysis** — Identifiability limits of stage-specific control in a calibrated stochastic model (1.21 million runs). Full details: https://github.com/caitlynrandels-del/metastatic-cascade-analysis
- **Epilepsy / seizure adaptation** — The metastasis relational testbed (v4) was adapted to seizure dynamics (117 scenarios, about 1.13 million simulated people), including a candidate psilocin receptor on-off gate mapping from Balabandian et al. 2025 (mouse PTZ/MES; 5-HT1A / CB1 / kynurenine). Speculative modeling only; no clinical claims. https://github.com/caitlynrandels-del/epilepsy-sim

- **Latest research (27 Nov 2026)**: [research/](research/). This holds the native metastasis cascade rerun with every Oroboro component in one loop ([PIPELINE.md](research/PIPELINE.md)), the magnetic-launch case study with its goal-seek, tilt/torque and geography addenda, and the cross-domain comparison. Older non-native sims are marked superseded. Speculative in-silico modeling only; no clinical, medical or engineering claims.

**Keywords:** Caitlyn Randels, Caitlyn Connor Randels, Oroboro, Ouroboros, state reduction, relational simulation, consciousness mapping, independent researcher.

Updated 2026-11-27.
