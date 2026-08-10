const fs = require('fs');
const path = require('path');
const matter = require('gray-matter');

// Replace with your custom domain or GitHub Pages URL
const domain = "https://pabsmophobia.github.io/Pabsmophobia-Website";
const postsDir = path.join(__dirname, 'newsletter');

// 1. Check if directory exists
if (!fs.existsSync(postsDir)) {
  console.error(`Error: Directory not found at ${postsDir}`);
  process.exit(1);
}

let files;
try {
  files = fs.readdirSync(postsDir);
} catch (err) {
  console.error("Error reading newsletter directory:", err);
  process.exit(1);
}

let itemsXml = '';

files.forEach(file => {
  if (file.endsWith('.md')) {
    const filePath = path.join(postsDir, file);
    
    try {
      const fileContent = fs.readFileSync(filePath, 'utf8');
      const { data } = matter(fileContent);

      // Skip draft posts
      if (data.draft) return;

      // Safe fallbacks for missing frontmatter fields
      const title = data.title || file.replace('.md', '');
      const description = data.description || '';
      
      // Safe Date Parsing
      let pubDate;
      if (data.date) {
        const parsedDate = new Date(data.date);
        pubDate = isNaN(parsedDate.getTime()) 
          ? new Date().toUTCString() 
          : parsedDate.toUTCString();
      } else {
        // Fallback to current date if missing
        pubDate = new Date().toUTCString();
      }

      const postUrl = `${domain}/post.html?file=${encodeURIComponent(file)}`;

      itemsXml += `
    <item>
      <title><![CDATA[${title}]]></title>
      <link>${postUrl}</link>
      <description><![CDATA[${description}]]></description>
      <pubDate>${pubDate}</pubDate>
      <guid>${postUrl}</guid>
    </item>`;
    } catch (parseError) {
      console.error(`Error processing file "${file}":`, parseError.message);
      // Skip bad file or rethrow if you want to fail the build intentionally
    }
  }
});

const rssFeed = `<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
  <channel>
    <title>The Pabsmophobia Monthly Haunt</title>
    <link>${domain}/blog.html</link>
    <description>Field notes, publication archives, and balanced investigation analysis.</description>
    <language>en-gb</language>
    ${itemsXml}
  </channel>
</rss>`;

try {
  fs.writeFileSync(path.join(__dirname, 'feed.xml'), rssFeed);
  console.log('RSS Feed successfully updated!');
} catch (writeError) {
  console.error("Error writing feed.xml:", writeError);
  process.exit(1);
}
