const fs = require('fs');
const path = require('path');

const filepath = path.join(__dirname, 'Constituição do Estado do Ceará.md');

const content = fs.readFileSync(filepath, 'utf-8');
const lines = content.split('\n');

console.log(`Total lines before processing: ${lines.length}`);

// Track lines to remove
const linesToRemove = new Set();

for (let i = 0; i < lines.length; i++) {
    const stripped = lines[i].trim();
    const lower = stripped.toLowerCase();
    
    // Pattern 1: Lines that are revogado markers
    if (/\((?:R|r)evogad[oa]\)/.test(stripped)) {
        linesToRemove.add(i);
        
        // Get the prefix before (Revogado)
        const match = stripped.match(/^(.+?)\s*\((?:R|r)evogad[oa]\)/);
        if (match) {
            const prefixClean = match[1].trim().replace(/\.+$/, '').trim();
            
            // Search backwards for the original text
            let j = i - 1;
            while (j >= 0) {
                const prevStripped = lines[j].trim();
                
                if (!prevStripped || prevStripped === '---') {
                    j--;
                    continue;
                }
                
                if (prevStripped.startsWith(prefixClean)) {
                    linesToRemove.add(j);
                    
                    // Check continuation lines between original and revogado marker
                    for (let k = j + 1; k < i; k++) {
                        const nextStripped = lines[k].trim();
                        if (nextStripped && !/^(§|Art\.|[IVXLCDM]+\s*[–-]|[a-z]\)|\()/.test(nextStripped) && nextStripped !== '---') {
                            linesToRemove.add(k);
                        }
                    }
                    
                    // Check if original text spans backwards
                    let m = j - 1;
                    while (m >= 0) {
                        const prevPrev = lines[m].trim();
                        if (!prevPrev || prevPrev === '---') break;
                        if (!/^(§|Art\.|[IVXLCDM]+\s*[–-]|[a-z]\)|Parágrafo|\d+$|####)/.test(prevPrev)) {
                            linesToRemove.add(m);
                        } else {
                            break;
                        }
                        m--;
                    }
                    break;
                }
                
                if (/^(####|Art\.\s|§\s|Seção|CAPÍTULO|TÍTULO|Subseção)/.test(prevStripped)) {
                    break;
                }
                
                j--;
            }
        }
    }
    
    // Pattern 2: Revocation explanation lines
    if (/^\((?:R|r)evogad[oa] pela\s/.test(stripped) || /^\((?:R|r)evogada? pela\s/.test(stripped)) {
        linesToRemove.add(i);
    }
}

// Build new content
const newLines = lines.filter((_, i) => !linesToRemove.has(i));

// Clean up multiple consecutive empty lines
const cleanedLines = [];
let emptyCount = 0;
for (const line of newLines) {
    if (line.trim() === '' || line.trim() === '\r') {
        emptyCount++;
        if (emptyCount <= 2) {
            cleanedLines.push(line);
        }
    } else {
        emptyCount = 0;
        cleanedLines.push(line);
    }
}

console.log(`Lines removed: ${linesToRemove.size}`);
console.log(`Total lines after processing: ${cleanedLines.length}`);

// Backup
const backupPath = filepath + '.backup';
if (!fs.existsSync(backupPath)) {
    fs.writeFileSync(backupPath, content, 'utf-8');
    console.log(`Backup saved to: ${backupPath}`);
}

// Write processed file
fs.writeFileSync(filepath, cleanedLines.join('\n'), 'utf-8');
console.log(`Processed file saved.`);

// Verify
const remaining = cleanedLines.filter(l => /revogad/i.test(l));
console.log(`\nRemaining lines with 'revogad': ${remaining.length}`);
remaining.slice(0, 10).forEach(l => console.log(`  ${l.trim().substring(0, 120)}`));
