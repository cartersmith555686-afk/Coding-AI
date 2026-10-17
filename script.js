let model;
let chars = [];
let charToIdx = {};
let idxToChar = {};
const seqLength = 5; 

// Dynamic Mapping Elements
const strictnessSlider = document.getElementById('strictness-slider');
const strictnessVal = document.getElementById('strictness-val');

// Global backend variables managed by your singular frontend slider
let currentTemp = 0.7;
let minConfidence = 0.3;

function updateInternalParameters() {
    const sliderVal = parseInt(strictnessSlider.value);

    if (sliderVal < 35) {
        // Less Strict / Unrestricted Configuration Matrix
        strictnessVal.textContent = "Unrestricted";
        strictnessVal.className = "status-badge unrestricted";
        // Interpolate parameters to scale to 1.8 creativity and remove confidence cutoffs entirely
        currentTemp = 0.8 + ((35 - sliderVal) / 35) * 1.0; 
        minConfidence = 0.0; 
    } else if (sliderVal >= 35 && sliderVal <= 70) {
        // Balanced Normal Behavior Block
        strictnessVal.textContent = "Balanced";
        strictnessVal.className = "status-badge standard";
        currentTemp = 0.5 + ((70 - sliderVal) / 35) * 0.3;
        minConfidence = 0.1 + ((sliderVal - 35) / 35) * 0.3;
    } else {
        // More Strict / Rigid Precision Matrix
        strictnessVal.textContent = "Max Strict";
        strictnessVal.className = "status-badge strict";
        // Force the model to pick only highly probable tokens or quit immediately
        currentTemp = 0.4 - ((sliderVal - 70) / 30) * 0.3; 
        minConfidence = 0.4 + ((sliderVal - 70) / 30) * 0.45;
    }
}

// Attach listener hooks
strictnessSlider.addEventListener('input', updateInternalParameters);
updateInternalParameters(); // Initialize states on startup

// Core Compiler/Trainer Pipeline
async function trainModel() {
    const statusBox = document.getElementById('status-box');
    const trainBtn = document.getElementById('train-btn');
    const text = document.getElementById('training-data').value;
    
    if (text.length <= seqLength) {
        statusBox.textContent = "CRITICAL_ERROR: Dataset string configuration too low.";
        return;
    }

    trainBtn.disabled = true;
    statusBox.textContent = "INITIALIZING: Creating vector vocabulary arrays...";

    chars = Array.from(new Set(text));
    charToIdx = {};
    idxToChar = {};
    chars.forEach((char, i) => {
        charToIdx[char] = i;
        idxToChar[i] = char;
    });

    const vocabSize = chars.length;
    const inputs = [];
    const labels = [];
    for (let i = 0; i < text.length - seqLength; i++) {
        inputs.push(text.substring(i, i + seqLength).split('').map(c => charToIdx[c]));
        labels.push(charToIdx[text.charAt(i + seqLength)]);
    }

    const xs = tf.oneHot(tf.tensor2d(inputs, [inputs.length, seqLength], 'int32'), vocabSize);
    const ys = tf.oneHot(tf.tensor1d(labels, 'int32'), vocabSize);

    statusBox.textContent = "COMPILING: Mounting Core Layer Matrices...";

    model = tf.sequential();
    model.add(tf.layers.flatten({ inputShape: [seqLength, vocabSize] }));
    model.add(tf.layers.dense({ units: 128, activation: 'relu' }));
    model.add(tf.layers.dense({ units: vocabSize, activation: 'softmax' }));

    model.compile({
        optimizer: tf.train.adam(0.01),
        loss: 'categoricalCrossentropy'
    });

    statusBox.textContent = "COMPUTE_ACTIVE: Fitting weights on execution matrix...";

    await model.fit(xs, ys, {
        epochs: 50,
        batchSize: 32,
        callbacks: {
            onEpochEnd: (epoch, logs) => {
                statusBox.textContent = `RUNNING: Epoch ${epoch + 1}/50\nLOSS_METRIC: ${logs.loss.toFixed(4)}`;
            }
        }
    });

    statusBox.textContent = "ONLINE: Neural system compilation stable. Inferencing unlocked.";
    document.getElementById('generate-btn').disabled = false;
    trainBtn.disabled = false;
    
    xs.dispose();
    ys.dispose();
}

// Inference Engine Routine
function generateText() {
    const outputBox = document.getElementById('output-box');
    const seed = document.getElementById('seed-input').value;
    
    if (!seed || !charToIdx.hasOwnProperty(seed)) {
        outputBox.textContent = `// RUNTIME_ERROR: Seed character '${seed}' missing from compiled training vocab registry.`;
        return;
    }

    let currentSeq = seed.repeat(seqLength).substring(0, seqLength);
    let generatedText = seed;
    outputBox.textContent = ""; 
    
    for (let i = 0; i < 150; i++) {
        let halted = false;

        tf.tidy(() => {
            const inputIndices = currentSeq.split('').map(c => charToIdx[c] || 0);
            const inputTensor = tf.oneHot(tf.tensor2d([inputIndices], [1, seqLength], 'int32'), chars.length);
            const rawPrediction = model.predict(inputTensor);
            
            // Validate absolute highest structural verification confidence
            const highestProb = rawPrediction.max().dataSync()[0];
            if (highestProb < minConfidence) {
                generatedText += `\n\n[EXECUTION_HALTED: Prediction confidence metric ${highestProb.toFixed(2)} drops below strict safety parameter threshold limit (${minConfidence.toFixed(2)})]`;
                halted = true;
                return;
            }

            // Apply Temperature Scaling
            const logPrediction = tf.div(tf.log(tf.add(rawPrediction, 1e-7)), currentTemp);
            const finalProbabilities = tf.softmax(logPrediction);
            
            const predictedIdx = tf.multinomial(finalProbabilities, 1).dataSync()[0];
            const nextChar = idxToChar[predictedIdx];
            
            generatedText += nextChar;
            currentSeq = currentSeq.substring(1) + nextChar;
        });

        if (halted) break;
    }
    
    outputBox.textContent = generatedText;
}

document.getElementById('train-btn').addEventListener('click', trainModel);
document.getElementById('generate-btn').addEventListener('click', generateText);
