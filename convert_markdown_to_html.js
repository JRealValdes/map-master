const fs = require('fs');
const path = require('path');
const { Transformer } = require('markmap-lib');
const { fillTemplate } = require('markmap-render');
const yamlFront = require('yaml-front-matter');

const markdownDir = path.join(__dirname, 'markdowns');
const outputDir = path.join(__dirname, 'templates');

const transformer = new Transformer();

function convertMarkdownToHtml(markdown, title) {
  const { root, features } = transformer.transform(markdown);
  const keys = Object.keys(features);
  const assets = transformer.getAssets(keys);
  let html = fillTemplate(root, assets);

  // Insert the title into the HTML
  html = html.replace('<title>Markmap</title>', `<title>${title}</title>`);
  return html;
}

fs.readdir(markdownDir, (err, files) => {
  if (err) {
    return console.error('Unable to scan directory:', err);
  }

  files.forEach((file) => {
    if (path.extname(file) === '.md') {
      const markdownPath = path.join(markdownDir, file);
      const outputFilePath = path.join(outputDir, path.basename(file, '.md') + '.html');

      fs.readFile(markdownPath, 'utf8', (err, markdown) => {
        if (err) {
          return console.error('Unable to read file:', err);
        }

        // Extract YAML front matter and the content
        const parsedMarkdown = yamlFront.loadFront(markdown);

        const title = parsedMarkdown.markmap.title || 'Document';
        const content = parsedMarkdown.__content;

        const html = convertMarkdownToHtml(content, title);

        fs.writeFile(outputFilePath, html, (err) => {
          if (err) {
            return console.error('Unable to write HTML file:', err);
          }

          console.log(`HTML file generated: ${outputFilePath}`);
        });
      });
    }
  });
});
