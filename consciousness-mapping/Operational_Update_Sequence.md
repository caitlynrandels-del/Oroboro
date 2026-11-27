# Operational Update Sequence

**Protocol for code, model, and parameter handling in Oroboro simulations**

Independent Research Note  
Caitlyn Connor Randels · November 2026

## Sequence

When applying updates, corrections, or parameter changes to simulation code or model state, use the following sequence:

**Use quick fix → UPDATE ALL → undo → Timestamp → do it again → use “syntax” to “autocorrect”.**

### Step meanings (as applied in the current metastasis simulation)

- **Quick fix:** Stage the change on a copy first.
- **UPDATE ALL:** Push the change to everything that depends on it.
- **Undo:** Roll it back and verify the original returns exactly.
- **Timestamp:** Log the change with the time.
- **Do it again:** Reapply the change and confirm the result matches the first application.
- **“Syntax” to “autocorrect”:** Validate values and fix only clear formatting errors, logging each fix.

This sequence is the active handling path for updates and corrections in the running public-dataset + sponge simulation and should be followed in related Oroboro model work.

Speculative modeling / architecture description only. No clinical claims.

---
*Added from chat history operational directive.*
