import React from 'react';
import { createRoot } from 'react-dom/client';
import { flushSync } from 'react-dom';
import Editor from '../src/forms';
import { ExperienceText } from '../src/ExperienceEditor';
import { experienceHtml, RICH_TEXT_PREFIX, sanitizeExperience } from '../src/richText';
import '../src/styles.css';

// Run through Vite at /tests/experience-editor.html. Requests are mocked;
// these checks exercise the real editor, form serialization and profile renderer.
const host = document.getElementById('root');
const root = createRoot(host);
const passed = [];
let saved;
const assert = (condition, message) => { if (!condition) throw new Error(message); };
const tick = () => new Promise(resolve => setTimeout(resolve, 20));
const input = () => host.querySelector('[contenteditable]');
const click = label => {
  const button = [...host.querySelectorAll('button')].find(item => item.getAttribute('aria-label') === label || item.textContent === label);
  assert(button && !button.disabled, `Missing enabled button: ${label}`);
  button.click();
};
async function mount(experience) {
  saved = null;
  flushSync(() => root.render(<Editor key={Math.random()} modal={{ type: 'technician', row: {
    id: 9, role: 'TECHNICIAN', first_name: 'Test', last_name: 'Technician', username: 'test',
    experience, is_active: true, cv_url: '/api/users/9/cv/', cv_name: 'cv.pdf',
  } }} data={{ clients: [], users: [] }} user={{ currency: 'DZD' }}
    save={async (path, method, body) => { saved = body; }} close={() => {}} />));
  await tick();
}
async function selectAll() {
  input().focus();
  const range = document.createRange();
  range.selectNodeContents(input());
  const selection = window.getSelection();
  selection.removeAllRanges();
  selection.addRange(range);
  document.dispatchEvent(new Event('selectionchange'));
  await tick();
}
async function run() {
  await mount('Maintenance industrielle\n2020–2026');
  assert(input().innerText.includes('Maintenance industrielle\n2020–2026'), 'Plain CV text or newlines were lost');
  await selectAll();
  for (const label of ['Gras', 'Italique', 'Souligné']) { click(label); await tick(); }
  assert(input().querySelector('b, strong') && input().querySelector('i, em') && input().querySelector('u'), 'Inline formatting failed');
  assert(saved === null, 'Toolbar submitted the form');
  click('Enregistrer'); await tick();
  const formatted = saved.experience;
  assert(formatted.startsWith(RICH_TEXT_PREFIX), 'Formatting missing from save request');
  assert(input().contentEditable === 'false', 'Editor still editable during save');
  await mount(formatted);
  assert(input().querySelector('u'), 'Formatting lost on reopening');
  passed.push('Legacy CV text, inline formatting, save and reopen');

  flushSync(() => root.render(<ExperienceText value={formatted} />));
  assert(host.querySelector('b, strong') && host.querySelector('u'), 'Profile did not render formatting');
  passed.push('Profile displays saved formatting');

  for (const [label, alignment] of [['Centrer', 'center'], ['Aligner à droite', 'right'], ['Aligner à gauche', 'left']]) {
    await mount(RICH_TEXT_PREFIX + '<p style="text-align: right;">Maintenance</p><p>Installation</p>');
    input().focus();
    const range = document.createRange();
    range.selectNodeContents(input().firstElementChild);
    window.getSelection().removeAllRanges();
    window.getSelection().addRange(range);
    document.dispatchEvent(new Event('selectionchange')); await tick();
    click(label); await tick();
    assert(getComputedStyle(input().firstElementChild).textAlign === alignment, `${label} failed`);
    assert(host.querySelector(`button[aria-label="${label}"]`).getAttribute('aria-pressed') === 'true', 'Active alignment not indicated');
    assert(!['center', 'right'].includes(getComputedStyle(input().lastElementChild).textAlign), 'Unselected paragraph was aligned');
    click('Enregistrer'); await tick();
    const aligned = saved.experience;
    await mount(aligned);
    assert(getComputedStyle(input().firstElementChild).textAlign === alignment, 'Alignment lost on reopening');
    flushSync(() => root.render(<ExperienceText value={aligned} />));
    assert(getComputedStyle(host.querySelector('.experience-content').firstElementChild).textAlign === alignment, 'Profile alignment lost');
  }
  passed.push('Left, center and right alignment: selection, active button, save, reopen and profile');

  assert(sanitizeExperience('<p style="text-align:center;color:red;position:fixed" onclick="alert(1)">Safe</p>') === '<p style="text-align: center;">Safe</p>', 'Unexpected styles or handlers survived');
  assert(sanitizeExperience('<div align="right">Safe</div>') === '<div style="text-align: right;">Safe</div>', 'Legacy alignment attribute not normalized');
  assert(sanitizeExperience('<p style="text-align:justify">Safe</p>') === '<p>Safe</p>', 'Unsupported alignment survived');
  passed.push('Alignment sanitization retains only supported values');

  for (const [label, selector] of [['Liste à puces', 'ul li'], ['Liste numérotée', 'ol li']]) {
    await mount('Maintenance\nInstallation'); await selectAll(); click(label); await tick();
    assert(input().querySelector(selector), `${label} failed`);
    click('Enregistrer'); await tick();
    assert(experienceHtml(saved.experience).includes(`<${selector.slice(0, 2)}>`), 'List missing from save');
  }
  passed.push('Bulleted and numbered lists');

  await mount('Maintenance'); await selectAll();
  window.getSelection().collapseToEnd();
  document.dispatchEvent(new Event('selectionchange')); await tick();
  click('Nouvelle ligne'); await tick();
  assert(input().querySelector('br'), 'Line break failed');
  click('Ligne de séparation'); await tick();
  assert(input().querySelector('hr'), 'Separator failed');
  passed.push('Line breaks and horizontal separators');

  await mount('Maintenance'); await selectAll(); click('Gras'); await tick();
  click('Annuler la modification'); await tick();
  assert(!input().querySelector('b, strong'), 'Undo failed');
  click('Rétablir la modification'); await tick();
  assert(input().querySelector('b, strong'), 'Redo failed');
  await selectAll(); click('Effacer la mise en forme'); await tick();
  assert(!input().querySelector('b, strong'), 'Clear formatting failed');
  passed.push('Undo, redo and clear formatting');

  const unsafe = '<p onclick="alert(1)"><b>Safe</b><img src=x onerror="alert(1)"><a href="javascript:alert(1)">Link</a></p><script>alert(1)</script><svg onload="alert(1)"></svg>';
  assert(sanitizeExperience(unsafe) === '<p><b>Safe</b>Link</p>', 'Unsafe HTML was retained');
  flushSync(() => root.render(<ExperienceText value={RICH_TEXT_PREFIX + unsafe} />));
  assert(!host.querySelector('img, script, svg, a, [onclick]'), 'Unsafe HTML reached the profile');
  flushSync(() => root.render(<ExperienceText value={'Literal <b>text</b> & CV'} />));
  assert(host.textContent === 'Literal <b>text</b> & CV' && !host.querySelector('b'), 'Legacy plain text interpreted as HTML');
  passed.push('Safe rendering and literal legacy text');

  await mount('');
  window.fetch = async () => ({ ok: true, json: async () => ({ experience: 'Extracted CV experience\n2020–2026', warning: '' }) });
  click('Extraire l’expérience du CV enregistré'); await tick(); await tick();
  assert(input().innerText.includes('Extracted CV experience'), 'CV extraction did not update the editor');
  click('Enregistrer'); await tick();
  assert(saved.experience === 'Extracted CV experience\n2020–2026', 'Extracted text missing from save');
  passed.push('CV extraction still populates and saves the editor');

  await mount('Original'); await selectAll();
  const clipboardData = new DataTransfer();
  clipboardData.setData('text/plain', '<b>pasted literally</b>');
  clipboardData.setData('text/html', '<b onclick="alert(1)">pasted literally</b>');
  input().dispatchEvent(new ClipboardEvent('paste', { bubbles: true, cancelable: true, clipboardData }));
  await tick();
  assert(input().textContent === '<b>pasted literally</b>' && !input().querySelector('b'), 'Paste was not plain text');
  passed.push('Pasting keeps text without importing HTML');

  await mount('Original');
  input().textContent = 'x'.repeat(20001);
  input().dispatchEvent(new InputEvent('input', { bubbles: true })); await tick();
  assert(input().textContent === 'Original' && host.querySelector('[role=alert]'), 'Length limit did not preserve the last valid value');
  input().innerHTML = '<div><br></div>';
  input().dispatchEvent(new InputEvent('input', { bubbles: true })); await tick();
  click('Enregistrer'); await tick();
  assert(saved.experience === '', 'Cleared editor did not save as empty');
  passed.push('Length limit and clearing content');

  await mount(formatted);
  input().scrollIntoView({ block: 'center' });
  assert(input().clientHeight >= 200, 'Editor is too short');
  assert(input().scrollWidth <= input().clientWidth, 'Editor overflows horizontally');
  passed.push('Larger editor layout');
  document.getElementById('result').textContent = JSON.stringify({ passed });
}
run().catch(error => { document.getElementById('result').textContent = JSON.stringify({ failed: error.message, passed }); });
