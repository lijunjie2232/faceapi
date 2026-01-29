const fs = require('fs');
const https = require('https');
const path = require('path');

// Directory to store models
const modelsDir = path.join(__dirname, 'public', 'models');
if (!fs.existsSync(modelsDir)) {
  fs.mkdirSync(modelsDir, { recursive: true });
}

// List of models to download
const modelFiles = [
  'tiny_face_detector_model-weights_manifest.json',
  'tiny_face_detector_model-shard1',
  'face_landmark_68_model-weights_manifest.json',
  'face_landmark_68_model-shard1',
  'face_landmark_68_tiny_model-weights_manifest.json',
  'face_landmark_68_tiny_model-shard1',
  'face_recognition_model-weights_manifest.json',
  'face_recognition_model-shard1',
  'face_recognition_model-shard2',
  'face_recognition_model-shard3',
  'age_gender_model-weights_manifest.json',
  'age_gender_model-shard1',
  'age_gender_model-shard2',
  'face_expression_model-weights_manifest.json',
  'face_expression_model-shard1',
];

// Base URL for models
const baseUrl = 'https://raw.githubusercontent.com/vladmandic/face-api/master/models/';

console.log('Downloading face-api.js models...');

modelFiles.forEach((filename, index) => {
  const url = baseUrl + filename;
  const filePath = path.join(modelsDir, filename);

  console.log(`Downloading ${filename}...`);

  const file = fs.createWriteStream(filePath);

  https.get(url, (response) => {
    if (response.statusCode === 200) {
      response.pipe(file);
      file.on('finish', () => {
        file.close();
        console.log(`${filename} downloaded successfully.`);
        
        // Check if all files are downloaded
        if (index === modelFiles.length - 1) {
          console.log('All models downloaded successfully!');
        }
      });
    } else {
      console.error(`Failed to download ${filename}. Status code: ${response.statusCode}`);
    }
  }).on('error', (err) => {
    console.error(`Error downloading ${filename}:`, err.message);
    file.close();
    fs.unlink(filePath, () => {}); // Delete the file if there's an error
  });
});