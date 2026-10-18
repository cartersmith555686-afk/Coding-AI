let model;
let chars = [];
let charToIdx = {};
let idxToChar = {};
const seqLength = 5; 

// Form Query Interceptors
const toggleConfigBtn = document.getElementById('toggle-config-btn');
const configPanel = document.getElementById('config-panel');
const strictnessSlider = document.getElementById('strictness-slider');
const strictnessVal = document.getElementById('strictness-val');
const chatContainer = document.getElementById('chat-container');
const chatInput = document.getElementById('chat-input');
const generateBtn = document.getElementById('generate-btn');

let currentTemp = 0.7;
let minConfidence = 0.3;

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

function appendMessage(text, side) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('msg', side);
    msgDiv.innerHTML = `<div class="msg-content">${text}</div>`;
    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Deep Learning Model Compiler
async function trainModel() {
    const statusBox = document.getElementById('status-box');
    const trainBtn = document.getElementById('train-btn');
    const systemPromptText = document.getElementById('system-prompt').value.trim();
    const coreDatasetText = document.getElementById('training-data').value;
    
    const combinedTrainingText = systemPromptText + "\n" + coreDatasetText;
    
    if (combinedTrainingText.length <= seqLength) {
        statusBox.textContent = "Error: Settings payload requires more string content data.";
        return;
    }

    trainBtn.disabled = true;
    statusBox.textContent = "Injecting custom instructions matrix...";

    chars = Array.from(new Set(combinedTrainingText));
    charToIdx = {};
    idxToChar = {};
    chars.forEach((char, i) => {
        charToIdx[char] = i;
        idxToChar[i] = char;
    });

    const vocabSize = chars.length;
    const inputs = [];
    const labels = [];
    for (let i = 0; i < combinedTrainingText.length - seqLength; i++) {
        inputs.push(combinedTrainingText.substring(i, i + seqLength).split('').map(c => charToIdx[c]));
        labels.push(charToIdx[combinedTrainingText.charAt(i + seqLength)]);
    }

    const xs = tf.oneHot(tf.tensor2d(inputs, [inputs.length, seqLength], 'int32'), vocabSize);
    const ys = tf.oneHot(tf.tensor1d(labels, 'int32'), vocabSize);

    model = tf.sequential();
    model.add(tf.layers.flatten({ inputShape: [seqLength, vocabSize] }));
    model.add(tf.layers.dense({ units: 128, activation: 'relu' }));
    model.add(tf.layers.dense({ units: vocabSize, activation: 'softmax' }));

    model.compile({ optimizer: tf.train.adam(0.01), loss: 'categoricalCrossentropy' });

    await model.fit(xs, ys, {
        epochs: 45,
        batchSize: 32,
        callbacks: {
            onEpochEnd: (epoch, logs) => {
                statusBox.textContent = `Aligning Persona... Progress: ${Math.round(((epoch+1)/45)*100)}%`;
            }
        }
    });

    statusBox.textContent = "Custom AI Persona loaded successfully.";
    chatInput.disabled = false;
    generateBtn.disabled = false;
    chatInput.placeholder = "Message Claude Fable 5.1...";
    configPanel.classList.add('hidden');
    appendMessage("<em>Your customized system instructions have been compiled into the core model weights successfully.</em>", "system");

    xs.dispose();
    ys.dispose();
}

// Local Execution Loop
function generateText() {
    const textPrompt = chatInput.value.trim();
    if (!textPrompt) return;

    appendMessage(textPrompt, "user");
    chatInput.value = "";

    // Hidden seed extraction mechanics
    let seed = textPrompt.charAt(0);
    if (!charToIdx.hasOwnProperty(seed)) {
        seed = chars[Math.floor(Math.random() * chars.length)];
    }

    let currentSeq = seed.repeat(seqLength).substring(0, seqLength);
    let generatedText = "";
    
    for (let i = 0; i < 180; i++) {
        let halted = false;

        tf.tidy(() => {
            const inputIndices = currentSeq.split('').map(c => charToIdx[c] || 0);
            const inputTensor = tf.oneHot(tf.tensor2d([inputIndices], [1, seqLength], 'int32'), chars.length);
            const rawPrediction = model.predict(inputTensor);
            
            const highestProb = rawPrediction.max().dataSync();
            if (highestProb < minConfidence) {
                generatedText += `\n\n[Halted: Confidence falls below guardrails threshold]`;
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
generateBtn.addEventListener('click', generateText);
chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        generateText();
    }
});
