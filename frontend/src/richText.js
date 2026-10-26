// A marker distinguishes formatted entries from existing plain CV text.
export const RICH_TEXT_PREFIX = '<!--copetrolite-experience:v1-->';
export const EXPERIENCE_LIMIT = 20000;
const allowedTags = new Set(['P', 'DIV', 'BR', 'STRONG', 'B', 'EM', 'I', 'U', 'UL', 'OL', 'LI', 'HR']);
const alignmentTags = new Set(['P', 'DIV', 'UL', 'OL', 'LI']);
const alignments = new Set(['left', 'center', 'right']);
const discardedTags = new Set(['SCRIPT', 'STYLE', 'IFRAME', 'OBJECT', 'EMBED', 'SVG', 'MATH', 'TEMPLATE']);

export function sanitizeExperience(html) {
  const source = new DOMParser().parseFromString(html, 'text/html');
  const target = document.createElement('div');
  function copy(node, parent) {
    if (node.nodeType === Node.TEXT_NODE) {
      parent.append(document.createTextNode(node.textContent));
    } else if (node.nodeType === Node.ELEMENT_NODE && !discardedTags.has(node.tagName)) {
      // Rebuild allowed elements; retain only explicitly supported alignment.
      const next = allowedTags.has(node.tagName) ? document.createElement(node.tagName.toLowerCase()) : parent;
      if (next !== parent) {
        if (alignmentTags.has(node.tagName)) {
          const alignment = (node.style.textAlign || node.getAttribute('align') || '').toLowerCase();
          if (alignments.has(alignment)) next.style.textAlign = alignment;
        }
        parent.append(next);
      }
      for (const child of node.childNodes) copy(child, next);
    }
  }
  for (const child of source.body.childNodes) copy(child, target);
  return target.innerHTML;
}

export function experienceHtml(value = '') {
  if (value.startsWith(RICH_TEXT_PREFIX)) return sanitizeExperience(value.slice(RICH_TEXT_PREFIX.length));
  const text = document.createElement('div');
  text.textContent = value;
  return text.innerHTML.replace(/\r\n?|\n/g, '<br>');
}

export function serializeExperience(html) {
  const clean = sanitizeExperience(html);
  const element = document.createElement('div');
  element.innerHTML = clean;
  return element.textContent.trim() || element.querySelector('hr') ? RICH_TEXT_PREFIX + clean : '';
}
