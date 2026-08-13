const fs = require('fs');
const path = require('path');

const newsletterDir = path.join(__dirname, '../newsletter');
const outputFile = path.join(__dirname, '../newsletter-manifest.json');

function parseFrontMatter(content) {
    const frontMatterRegex = /^---\s*([\s\S]*?)\s*---/;
    const match = content.match(frontMatterRegex);
    if (!match) return {};

    const frontMatterBlock = match[1];
    const data = {};
    frontMatterBlock.split('\n').forEach(line => {
        const parts = line.split(':');
        if (parts.length >= 2) {
            const key = parts[0].trim();
            let value = parts.slice(1).join(':').trim();
            // Remove surrounding quotes if present
            if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
                value = value.slice(1, -1);
            }
            data[key] = value;
        }
    });
    return data;
}

function generateManifest() {
    if (!fs.existsSync(newsletterDir)) {
        console.error("Newsletter directory not found.");
        return;
    }

    const files = fs.readdirSync(newsletterDir).filter(file => file.endsWith('.md'));
    const articles = [];

    files.forEach(file => {
        const filePath = path.join(newsletterDir, file);
        const content = fs.readFileSync(filePath, 'utf8');
        const meta = parseFrontMatter(content);

        articles.push({
            file: `newsletter/${file}`,
            title: meta.title || file.replace('.md', ''),
            date: meta.date || '2026-01-01',
            category: meta.tags ? meta.tags.replace(/[[\]']/g, '').split(',')[0].trim().toUpperCase() : 'ARTICLE',
            excerpt: meta.description || ''
        });
    });

    // Sort by date descending (newest first)
    articles.sort((a, b) => new Date(b.date) - new Date(a.date));

    fs.writeFileSync(outputFile, JSON.stringify(articles, null, 2));
    console.log(`Generated manifest with ${articles.length} articles.`);
}

generateManifest();
