/**
 * Simple Quantum String Collapse Engine
 */
function collapseString(rawThought) {
    // 1. Convert thought into a vibrational frequency (String Theory mode)
    let vibration = [...rawThought].reduce((acc, char) => acc + char.charCodeAt(0), 0);
    let probability = Math.abs(Math.sin(vibration)) * 100;

    // 2. Observe and collapse wavefunction (Quantum Measurement)
    return {
        thought: rawThought,
        stabilityScore: probability.toFixed(2) + "%",
        state: probability > 50 ? "Fact (Solidified)" : "Superposition (Doubt)"
    };
}

// --- Quick Test ---
const result = collapseString("These thoughts aren't delusions, they're memories");
console.log(result);
