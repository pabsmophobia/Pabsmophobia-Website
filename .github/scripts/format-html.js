const fs = require('fs');
const path = require('path');
const cheerio = require('cheerio');

// Function to process HTML files recursively or in a directory
function processDirectory(dirPath) {
  const files = fs.readdirSync(dirPath);

  files.forEach((file) => {
    const fullPath = path.join(dirPath, file);
    const stat = fs.statSync(fullPath);

    if (stat.isDirectory() && !file.startsWith('.') && file !== 'node_modules') {
      processDirectory(fullPath);
    } else if (file.endsWith('.html')) {
      cleanHtmlFile(fullPath);
    }
  });
}

function cleanHtmlFile(filePath) {
  const htmlContent = fs.readFileSync(filePath, 'utf8');
  const $ = cheerio.load(htmlContent, { decodeEntities: false });

  // 1. Find all styles.css links in head
  const cssLinks = $('head link[href*="styles.css"]');

  if (cssLinks.length > 0) {
    // Keep only the first instance and remove all duplicates
    cssLinks.slice(1).remove();
  } else {
    // Append it once if it was missing completely
    $('head').append('  <link rel="stylesheet" href="styles.css">\n');
  }

  // 2. Write cleaned HTML back to disk
  fs.writeFileSync(filePath, $.html());
  console.log(`Normalized: ${filePath}`);
}

// Run against your repository root
processDirectory(path.join(__dirname, '../../'));
