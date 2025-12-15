# Face Expression Classifier

A real-time image classification project that detects **Happy**, **Sad**, and **Neutral** facial expressions using your webcam. Checks for `model/model.json` in the project directory.

## 🚀 Getting Started

### 1. Train your Model
1. Go to [Teachable Machine](https://teachablemachine.withgoogle.com/train/image).
2. Create a generic **Image Project**.
3. Create 3 Classes:
   - **Class 1**: Rename to `Happy` and record samples of you smiling.
   - **Class 2**: Rename to `Sad` and record samples of you looking sad.
   - **Class 3**: Rename to `Neutral` and record samples of your neutral face.
4. Click **Train Model**.
5. Once trained, click **Export Model**.
6. Select the **TensorFlow.js** tab and choose **Download** (do NOT choose Upload if you want to use local files, but Upload is easier for hosted links).
7. Download the zip file, unzip it.
8. Create a folder named `model` inside this project directory.
9. Place the `model.json` and `metadata.json` files into the `model/` folder.

   Structure should look like:
   ```
   Image Classifier/
   ├── index.html
   ├── script.js
   ├── style.css
   ├── README.md
   └── model/
       ├── model.json
       └── metadata.json
   ```

### 2. Run the Application
Due to browser security restrictions (CORS), you cannot simply double-click `index.html` to load local models. You must run a local server.

**Recommended Option: VS Code Live Server**
1. Open this folder in VS Code.
2. Install the **Live Server** extension.
3. Right-click `index.html` and select **Open with Live Server**.

The application will open in your browser. Click **Start Webcam** to verify it works!

## 🛠️ Tech Stack
- **HTML5/CSS3**: Frontend UI.
- **JavaScript (ES6)**: Application logic.
- **TensorFlow.js**: Machine Learning runtime.
- **Google Teachable Machine**: Model training platform.
