const fs = require('fs');
const path = require('path');
const cheerio = require('cheerio');

// Define the root directory of your project
const projectRoot = path.resolve(__dirname, '../../');

// Recursively process directory to find all HTML files
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

  // Calculate correct relative path to styles.css based on file depth
  const relativeDir = path.relative(path.dirname(filePath), projectRoot);
  const correctHref = relativeDir ? path.join(relativeDir, 'styles.css').replace(/\\/g, '/') : 'styles.css';

  // Find exact stylesheet links matching styles.css (ignoring third-party like sib-styles.css)
  const exactCssLinks = $('head link[rel="stylesheet"]').filter((_, el) => {
    const href = $(el).attr('href');
    if (!href) return false;
    return href === 'styles.css' || href.endsWith('/styles.css');
  });

  if (exactCssLinks.length > 0) {
    // Update the first match with the correct relative path
    $(exactCssLinks[0]).attr('href', correctHref);
    // Remove any accidental duplicate links to styles.css
    exactCssLinks.slice(1).remove();
  } else {
    // Append styles.css if it is missing completely
    $('head').append(`  <link rel="stylesheet" href="${correctHref}">\n`);
  }

  // Save the normalized HTML back to disk
  fs.writeFileSync(filePath, $.html());
  console.log(`Normalized: ${filePath}`);
}

// Execute script starting from project root
processDirectory(projectRoot);
