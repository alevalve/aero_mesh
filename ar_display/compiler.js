const { OfflineCompiler } = require('./mind-ar-js/src/image-target/offline-compiler.js');
const { writeFile } = require('fs/promises');
const { loadImage } = require('canvas');

const inputImagePath = process.argv[2]; 
const outputMindPath = process.argv[3];

async function run() {
    try {
        if (!inputImagePath || !outputMindPath) process.exit(1);

        const images = await Promise.all([loadImage(inputImagePath)]);
        const compiler = new OfflineCompiler();
        
        await compiler.compileImageTargets(images, () => {});

        const buffer = compiler.exportData();
        await writeFile(outputMindPath, buffer);
        
        process.exit(0);
    } catch (err) {
        process.exit(1);
    }
}

run();