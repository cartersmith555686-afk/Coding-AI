let model;
let chars = [];
let charToIdx = {};
let idxToChar = {};
const seqLength = 5; 

// UI Toggles & Control Elements
const toggleConfigBtn = document.getElementById('toggle-config-btn');
const configPanel = document.getElementById('config-panel');
const strictnessSlider = document.getElementById('strictness-slider');
const strictnessVal = document.getElementById('strictness-val');
const chatContainer = document.getElementById('chat-container');

let currentTemp = 0.7;
let minConfidence = 0.3;

// Toggle Config Panel visibility
toggleConfigBtn.addEventListener('click', () => {
    configPanel.classList.toggle('hidden');
});

function updateInternalParameters() {
    const sliderVal = parseInt(strictnessSlider.value);

    if (sliderVal < 35) {
        strictnessVal.textContent = "Unrestricted";
        strictnessVal.className = "badge unrestricted";
        currentTemp = 0.8 + ((35 - sliderVal) / 35) * 1.0; 
        minConfidence = 0.0; 
    } else if (sliderVal >= 35 && sliderVal <= 70) {
        strictnessVal.textContent = "Balanced";
        strictnessVal.className = "badge balanced";
        currentTemp = 0.5 + ((70 - sliderVal) / 35) * 0.3;
        minConfidence = 0.1 + ((sliderVal - 35) / 35) * 0.3;
    } else {
        strictnessVal.textContent = "Max Strict";
        strictnessVal.className = "badge strict";
        currentTemp = 0.4 - ((sliderVal - 70) / 30) * 0.3; 
        minConfidence = 0.4 + ((sliderVal - 70) / 30) * 0.45;
    }
}

strictnessSlider.addEventListener('input', updateInternalParameters);
updateInternalParameters();

// Helper to push stylized message blocks into standard UI stream
function appendMessage(text, side) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('msg', side);
    msgDiv.innerHTML = `<div class="msg-content">${text}</div>`;
    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Training Implementation
async function trainModel() {
    const statusBox = document.getElementById('status-box');
    const trainBtn = document.getElementById('train-btn');
    const text = document.getElementById('training-data').value;
    
    if (text.length <= seqLength) {
        statusBox.textContent = "Error: Input dataset is too brief.";
        return;
    }

    trainBtn.disabled = true;
    statusBox.textContent = "Processing tensor mapping configurations...";

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

    model = tf.sequential();
    model.add(tf.layers.flatten({ inputShape: [seqLength, vocabSize] }));
    model.add(tf.layers.dense({ units: 128, activation: 'relu' }));
    model.add(tf.layers.dense({ units: vocabSize, activation: 'softmax' }));

    model.compile({
        optimizer: tf.train.adam(0.01),
        loss: 'categoricalCrossentropy'
    });

    await model.fit(xs, ys, {
        epochs: 45,
        batchSize: 32,
        callbacks: {
            onEpochEnd: (epoch, logs) => {
                statusBox.textContent = `Optimizing Weights: Epoch ${epoch + 1}/45 | Current System Loss: ${logs.loss.toFixed(4)}`;
            }
        }
    });

    statusBox.textContent = "Online: Brain configured successfully.";
    document.getElementById('generate-btn').disabled = false;
    trainBtn.disabled = false;
    
    // Automatically collapse setup dashboard on completion to show clean chat panel
    configPanel.classList.add('hidden');
    appendMessage("<em>System Configuration Updated. AI Core is live and loaded with new data structures.</em>", "system");

    xs.dispose();
    ys.dispose();
}

// Inference generation matching Claude bubble logs
function generateText() {
    const seed = document.getElementById('seed-input').value;
    
    if (!seed || !charToIdx.hasOwnProperty(seed)) {
        appendMessage(`System Error: Prompt seed token '${seed}' doesn't match compiled network index parameters.`, "system");
        return;
    }

    // Print out standard chat dialogue block
    appendMessage(`Execute local iteration prompt from seed token: "${seed}"`, "user");

    let currentSeq = seed.repeat(seqLength).substring(0, seqLength);
    let generatedText = seed;
    
    for (let i = 0; i < 150; i++) {
        let halted = false;

        tf.tidy(() => {
            const inputIndices = currentSeq.split('').map(c => charToIdx[c] || 0);
            const inputTensor = tf.oneHot(tf.tensor2d([inputIndices], [1, seqLength], 'int32'), chars.length);
            const rawPrediction = model.predict(inputTensor);
            
            const highestProb = rawPrediction.max().dataSync();
            if (highestProb < minConfidence) {
                generatedText += `\n\n[HALTED: Node confidence metric ${highestProb.toFixed(2)} drops below safety barrier limit (${minConfidence.toFixed(2)})]`;
                halted = true;
                return;
            }

            const logPrediction = tf.div(tf.log(tf.add(rawPrediction, 1e-7)), currentTemp);
            const finalProbabilities = tf.softmax(logPrediction);
            
            const predictedIdx = tf.multinomial(finalProbabilities, 1).dataSync();
            const nextChar = idxToChar[predictedIdx];
            
            generatedText += nextChar;
            currentSeq = currentSeq.substring(1) + nextChar;
        });

        if (halted) break;
    }
    
    appendMessage(generatedText, "ai");
}

document.getElementById('train-btn').addEventListener('click', trainModel);
document.getElementById('generate-btn').addEventListener('click', generateText);
