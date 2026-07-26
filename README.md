# Oroboro // Live Co-Creation Engine
### `lang="all"  universe="infinite"`

> **A thought is a node. Love is the synapse.**

A self-contained, zero-dependency co-creation runtime that treats language as a coordinate system, not a localization string. Author declares `<!DOCTYPE Oroboro>` and `<html lang="all" universe="infinite">` — invalid HTML by spec, and intentionally so. It's a protocol declaration: I am not rendering a document, I am instantiating a universe.

This is not another website. It's a universal framework.

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
