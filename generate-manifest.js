const fs = require('fs');
const path = require('path');
const matter = require('gray-matter');

// Adjust this path to wherever your markdown newsletter/blog files are stored
const postsDirectory = path.join(__dirname, 'newsletter'); 
const manifestPath = path.join(__dirname, 'newsletter-manifest.json');

function generateManifest() {
  try {
    if (!fs.existsSync(postsDirectory)) {
      console.log(`Directory ${postsDirectory} does not exist.`);
      return;
    }

    const files = fs.readdirSync(postsDirectory);
    const articles = [];

    files.forEach(file => {
      if (path.extname(file) === '.md') {
        const filePath = path.join(postsDirectory, file);
        const fileContent = fs.readFileSync(filePath, 'utf8');
        
        // Parse YAML front matter
        const { data } = matter(fileContent);

        articles.push({
          title: data.title || 'Untitled',
          excerpt: data.description || '',
          category: data.tags ? data.tags[0] : 'General',
          file: `newsletter/${file}` // Path used by your frontend fetch
        });
    }
  });

  // Sort articles by date (newest first) if a date field exists
  articles.sort((a, b) => new Date(b.date) - new Date(a.date));

  // Write out the fresh manifest JSON
  fs.writeFileSync(manifestPath, JSON.stringify(articles, null, 2), 'utf8');
  console.log(`✅ Success! Generated manifest with ${articles.length} articles.`);
} catch (error) {
    console.error('Error generating manifest:', error);
  }
}

generateManifest();
