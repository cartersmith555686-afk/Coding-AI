### Fable 5.1 // Client-Side Neural Playground

A lightweight, zero-backend, custom deep learning workspace built from scratch to run entirely inside the client browser. Inspired by the clean, minimalist look of premium conversational interfaces, **Fable 5.1** builds, tokenizes, trains, and runs text-generation neural matrices natively using hardware acceleration via TensorFlow.js. 

Live deployment is fully optimized for static platforms like **GitHub Pages**. 

### ✦ Key Features

* **Native Compute Engine:** No external LLM endpoints, subscription models, or central API tokens required. Training and execution happen entirely in your local browser cache.
* **Unified Policy Framework:** Features an interactive **AI Guardrails** slider to transition seamlessly from **Less Strict (Unrestricted)** to **Max Strict (Rigid)** operating parameters.
* **Minimalist Conversational UI:** A mobile-responsive layout styled with custom workspace dashboard modules, fluid slide-down system configuration drawers, and contextual code response bubbles.
* **Dynamic Optimization Tracking:** Live telemetry display showcasing systemic mathematical training steps and categorical evaluation values.

### 🛠️ Global Parameters Matrix

The operational strictness structure is mapped across a singular control hook to adjust predictive output behavior automatically: 

Strictness SettingTemperature ScaleConfidence CutoffOperational Character Behavior
****Unrestricted****
High (0.8 – 1.8)None (0.00)Maximizes creative entropy; outputs highly varied sequences.
****Balanced****
Standard (0.5 – 0.8)Low (0.10 – 0.40)Balances structured syntactic continuity with pattern variations.
****Max Strict****
Low (0.10 – 0.40)High (0.40 – 0.85)Limits variance to optimal calculations; instantly halts execution if confidence drops below limits.

### 🚀 Quick Deployment Guide (GitHub Pages)

Because this network runs entirely inside client-side JavaScript layers, hosting takes less than two minutes: 

1. **Fork or Create a Repository:** Initialize a public repository on GitHub (e.g., my-custom-ai).
2. **Upload Core Stack Files:** Commit the following bundle files directly into your root directory: 

  * index.html
  * style.css
  * script.js
3. **Activate Pages Module:** 

  * Navigate to repository **Settings** (⚙️) -> **Pages**.
  * Under *Build and deployment*, change the source branch from None to main (or master) and select / (root).
  * Click **Save**.
4. **Access Instance:** Launch your live uniform route link provided by GitHub (e.g., https://<username>.github.io/my-custom-ai/).

### 💻 Code Architecture Overview

* **Input Flatten Vectoring:** Custom text payload segments are converted into localized array sequences of specified chunk token frames (seqLength = 5).
* **One-Hot Encoding Vectors:** Data sequences are dynamically projected onto tensor matrices scaling against computed distinct character vocabulary indexes.
* **Network Construction Layout:** 

  * tf.layers.flatten: Reshapes character arrays into standard sequential dimensions.
  * tf.layers.dense (units: 128, activation: 'relu'): Hidden structural layer managing non-linear pattern calculations.
  * tf.layers.dense (units: vocabSize, activation: 'softmax'): Outputs cross-entropy prediction distributions across known token libraries.

### 📝 Usage Scenario

1. Expand the **System Config** drawer.
2. Inject a structured code fragment or text block into the payload space.
3. Click **Compile & Train Model Brain** and observe the live loss tracking.
4. Set your preferred **AI Guardrails** constraint index.
5. Key in a desired seed character sequence at the bottom, click **Execute Inference**, and view your model's generative output inside the conversation feed.
