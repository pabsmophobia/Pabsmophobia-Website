const fs = require('fs');
const path = require('path');
const matter = require('gray-matter');

// Replace with your custom domain or GitHub Pages URL
const domain = "https://pabsmophobia.github.io/Pabsmophobia-Website";
const postsDir = path.join(__dirname, 'newsletter');
const files = fs.readdirSync(postsDir);

let itemsXml = '';

files.forEach(file => {
  if (file.endsWith('.md')) {
    const filePath = path.join(postsDir, file);
    const fileContent = fs.readFileSync(filePath, 'utf8');
    const { data } = matter(fileContent);

    if (data.draft) return;

    const postUrl = `${domain}/post.html?file=${encodeURIComponent(file)}`;
    const pubDate = new Date(data.date).toUTCString();

    itemsXml += `
    <item>
      <title><![CDATA[${data.title}]]></title>
      <link>${postUrl}</link>
      <description><![CDATA[${data.description}]]></description>
      <pubDate>${pubDate}</pubDate>
      <guid>${postUrl}</guid>
    </item>`;
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

fs.writeFileSync(path.join(__dirname, 'feed.xml'), rssFeed);
console.log('RSS Feed successfully updated!');
