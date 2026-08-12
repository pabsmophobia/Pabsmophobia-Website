const fs = require('fs');
const path = require('path');
const matter = require('gray-matter');

// 1. Updated domain to custom domain
const domain = "https://pabsmophobia.com";
const postsDir = path.join(__dirname, 'newsletter');

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

      if (data.draft) return;

      const title = data.title || file.replace('.md', '');
      const description = data.description || '';
      
      // 2. Strict pubDate fallback: Use file modification time (mtime) instead of new Date()
      let pubDate;
      if (data.date) {
        const parsedDate = new Date(data.date);
        pubDate = !isNaN(parsedDate.getTime()) 
          ? parsedDate.toUTCString() 
          : fs.statSync(filePath).mtime.toUTCString();
      } else {
        // Safe fallback: Uses file creation/modified timestamp so date NEVER changes on rebuilt
        pubDate = fs.statSync(filePath).mtime.toUTCString();
      }

      const postUrl = `${domain}/post.html?file=${encodeURIComponent(file)}`;

      // 3. Added isPermaLink="true" to enforce deduplication
      itemsXml += `
    <item>
      <title><![CDATA[${title}]]></title>
      <link>${postUrl}</link>
      <description><![CDATA[${description}]]></description>
      <pubDate>${pubDate}</pubDate>
      <guid isPermaLink="true">${postUrl}</guid>
    </item>`;
    } catch (parseError) {
      console.error(`Error processing file "${file}":`, parseError.message);
    }
  }
});

const rssFeed = `<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>The Pabsmophobia Monthly Haunt</title>
    <link>${domain}/blog.html</link>
    <description>Field notes, publication archives, and balanced investigation analysis.</description>
    <language>en-gb</language>
    <atom:link href="${domain}/feed.xml" rel="self" type="application/rss+xml" />
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
