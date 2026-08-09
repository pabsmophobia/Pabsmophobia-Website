const fs = require('fs');
const path = require('path');
const cheerio = require('cheerio');

// Scan the root directory for HTML files
const files = fs.readdirSync('.').filter(file => file.endsWith('.html'));

files.forEach(file => {
  let html = fs.readFileSync(file, 'utf8');
  const $ = cheerio.load(html, { decodeEntities: false });

  // 1. Remove all page-level internal <style> blocks
  $('head style').remove();

  // 2. Ensure standard external stylesheet link exists
  if ($('head link[href="style.css"]').length === 0) {
    $('head').append('  <link rel="stylesheet" href="style.css">\n');
  }

  // Write the cleaned HTML back to the file
  fs.writeFileSync(file, $.html());
  console.log(`Successfully normalized: ${file}`);
});
