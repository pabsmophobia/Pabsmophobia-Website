const fs = require('fs');
const path = require('path');
const matter = require('gray-matter');

const newsletterDir = path.join(__dirname, '../../newsletter');
const outputFile = path.join(__dirname, '../../newsletter-manifest.json');

function generateManifest() {
    if (!fs.existsSync(newsletterDir)) {
        console.error("Newsletter directory not found.");
        return;
    }

    const files = fs.readdirSync(newsletterDir).filter(file => file.endsWith('.md'));
    const articles = [];

    files.forEach(file => {
        const filePath = path.join(newsletterDir, file);
        const fileContent = fs.readFileSync(filePath, 'utf8');
        const { data } = matter(fileContent);

        let category = 'ARTICLE';
        if (data.tags) {
            if (Array.isArray(data.tags)) {
                category = data.tags[0].toUpperCase();
            } else if (typeof data.tags === 'string') {
                category = data.tags.split(',')[0].trim().toUpperCase();
            }
        }

        let formattedDate = '2026-01-01';
        if (data.date) {
            const parsed = new Date(data.date);
            if (!isNaN(parsed.getTime())) {
                formattedDate = parsed.toISOString().split('T')[0];
            } else {
                formattedDate = String(data.date).split('T')[0];
            }
        }

        articles.push({
            file: `newsletter/${file}`,
            title: data.title || file.replace('.md', ''),
            date: formattedDate,
            category: category,
            excerpt: data.description || ''
        });
    });

    // Sort by date descending (newest first)
    articles.sort((a, b) => new Date(b.date) - new Date(a.date));

    fs.writeFileSync(outputFile, JSON.stringify(articles, null, 2));
    console.log(`Generated manifest with ${articles.length} articles.`);
}

generateManifest();
