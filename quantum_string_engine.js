/**
 * Quantum String Theory State Engine
 * Models multi-dimensional vibrational loops and wavefunction collapse.
 */
class QuantumStringEngine {
    constructor(dimensions = 11, stringTension = 1.618) {
        this.dimensions = dimensions;
        this.tension = stringTension; // Modeled on golden ratio tension
        this.superpositionPool = [];
    }

    /**
     * Spawns a multidimensional closed string vibrating in a probability matrix.
     */
    vibrateString(identifier, rawFrequencyData) {
        let stringState = {
            id: identifier,
            modes: [],
            collapsed: false
        };

        // Generate harmonic modes across n-dimensions (String Theory topology)
        for (let d = 1; d <= this.dimensions; d++) {
            let harmonic = Math.sin(d * this.tension) * hashCode(rawFrequencyData);
            stringState.modes.push({ dimension: d, amplitude: harmonic });
        }

        this.superpositionPool.push(stringState);
        return stringState;
    }

    /**
     * Forces wavefunction collapse (Quantum Measurement Problem) 
     * using an observer function (The Oroboro Loop).
     */
    observeAndCollapse(stringIdentifier) {
        let stringIndex = this.superpositionPool.findIndex(s => s.id === stringIdentifier);
        if (stringIndex === -1) return "String State Not Found in Superposition";

        let targetString = this.superpositionPool[stringIndex];
        
        // Sum the vibrational amplitudes to determine the collapsed real state
        let totalAmplitude = targetString.modes.reduce((acc, mode) => acc + mode.amplitude, 0);
        let probabilityWave = Math.abs(Math.cos(totalAmplitude)) * 100;

        targetString.collapsed = true;
        
        return {
            status: "Wavefunction Collapsed",
            stringId: targetString.id,
            resolvedProbability: probabilityWave.toFixed(4) + "%",
            stableRealityState: probabilityWave > 50 ? "Macro-State: Fact/Memory" : "Macro-State: Superposition/Doubt"
        };
    }
}

/**
 * Utility hash function for frequency generation.
 */
function hashCode(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        hash = (hash << 5) - hash + str.charCodeAt(i);
        hash |= 0;
    }
    return hash;
}

// --- Execution Test ---
const qEngine = new QuantumStringEngine(11, 1.618);

// Inject a raw logic chain bundle as a vibrational frequency
const stringA = qEngine.vibrateString("STRING-ORB-001", "These thoughts aren't delusions, they're memories");
console.log("Initialized 11-Dimensional Closed Loop String:", JSON.stringify(stringA, null, 2));

// Collapse the wavefunction via observation
const observationResult = qEngine.observeAndCollapse("STRING-ORB-001");
console.log("\n--- Observation Event ---");
console.log(JSON.stringify(observationResult, null, 2));
