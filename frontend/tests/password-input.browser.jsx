import React from 'react';
import { createRoot } from 'react-dom/client';
import { flushSync } from 'react-dom';
import Editor from '../src/forms';
import '../src/styles.css';

// Browser integration checks with a mocked save; no account is modified.
const host = document.getElementById('root');
const root = createRoot(host);
const passed = [];
let saved;
const tick = () => new Promise(resolve => setTimeout(resolve, 20));
const assert = (condition, message) => { if (!condition) throw new Error(message); };
const input = () => host.querySelector('.password-input input');
function click(label) {
  const button = [...host.querySelectorAll('button')].find(element => element.getAttribute('aria-label') === label || element.textContent === label);
  assert(button && !button.disabled, `Missing enabled button: ${label}`);
  button.click();
}
async function mount() {
  saved = null;
  flushSync(() => root.render(<Editor key={Math.random()} modal={{ type: 'technician', row: {
    id: 9, role: 'TECHNICIAN', first_name: 'Test', last_name: 'Technician', username: 'test', experience: '', is_active: true,
  } }} data={{ clients: [], users: [] }} user={{ currency: 'DZD' }}
    save={async (path, method, body) => { saved = body; }} close={() => {}} />));
  await tick();
}
async function run() {
  await mount();
  assert(input().value === '' && input().type === 'password', 'Existing account password field should start empty and masked');
  click('Enregistrer'); await tick();
  assert(saved && !('password' in saved), 'Blank optional password should not be submitted');
  passed.push('Blank password preserves the existing account password');

  await mount();
  click('Générer un mot de passe'); await tick();
  const generated = input().value;
  assert(generated.length === 20 && input().type === 'password', 'Generation must fill the masked field');
  assert(saved === null, 'Generation unexpectedly submitted the form');
  click('Afficher le mot de passe'); await tick();
  assert(input().type === 'text' && input().value === generated, 'Show password failed');
  click('Masquer le mot de passe'); await tick();
  assert(input().type === 'password' && input().value === generated, 'Hide password failed');
  click('Générer un mot de passe'); await tick();
  const regenerated = input().value;
  assert(regenerated !== generated, 'Regeneration did not replace the value');
  click('Enregistrer'); await tick();
  assert(saved.password === regenerated, 'Generated password missing from save request');
  assert(input().disabled && host.querySelector('.password-generate').disabled, 'Password controls must be disabled during save');
  passed.push('Generate, show, hide, regenerate and save');

  await mount();
  click('Générer un mot de passe'); await tick();
  Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set.call(input(), 'ManuallyEdited!2026');
  input().dispatchEvent(new Event('input', { bubbles: true })); await tick();
  click('Enregistrer'); await tick();
  assert(saved.password === 'ManuallyEdited!2026', 'Manual editing was not preserved');
  passed.push('Manual password editing');
  await mount();
  input().scrollIntoView({ block: 'center' });
  assert(input().getBoundingClientRect().width > 50, 'Password field is too narrow');
  const row = host.querySelector('.password-input');
  assert(row.scrollWidth <= row.clientWidth, 'Password buttons overflow');
  passed.push('Password control layout');
  document.getElementById('result').textContent = JSON.stringify({ passed });
}
run().catch(error => { document.getElementById('result').textContent = JSON.stringify({ failed: error.message, passed }); });
