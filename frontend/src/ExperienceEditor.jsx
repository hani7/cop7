import { useEffect, useId, useLayoutEffect, useRef, useState } from 'react';
import { AlignLeft, AlignCenter, AlignRight, Bold, Italic, Underline, List, ListOrdered, CornerDownLeft, Minus, Undo2, Redo2, RemoveFormatting } from 'lucide-react';
import { EXPERIENCE_LIMIT, experienceHtml, serializeExperience } from './richText';
import './experience.css';

const actions = [
  ['bold', 'Gras', Bold], ['italic', 'Italique', Italic], ['underline', 'Souligné', Underline],
  ['justifyLeft', 'Aligner à gauche', AlignLeft], ['justifyCenter', 'Centrer', AlignCenter], ['justifyRight', 'Aligner à droite', AlignRight],
  ['insertUnorderedList', 'Liste à puces', List], ['insertOrderedList', 'Liste numérotée', ListOrdered],
  ['insertLineBreak', 'Nouvelle ligne', CornerDownLeft], ['insertHorizontalRule', 'Ligne de séparation', Minus],
  ['undo', 'Annuler la modification', Undo2], ['redo', 'Rétablir la modification', Redo2],
  ['removeFormat', 'Effacer la mise en forme', RemoveFormatting],
];
const toggles = new Set(['bold', 'italic', 'underline', 'justifyLeft', 'justifyCenter', 'justifyRight', 'insertUnorderedList', 'insertOrderedList']);

export default function ExperienceEditor({ value = '', onChange, disabled = false }) {
  const id = useId();
  const editor = useRef(null);
  const selection = useRef(null);
  const emitted = useRef(null);
  const [active, setActive] = useState({});
  const [error, setError] = useState('');

  useLayoutEffect(() => {
    if (value !== emitted.current) {
      editor.current.innerHTML = experienceHtml(value);
      selection.current = null;
      emitted.current = value;
      setError('');
    }
  }, [value]);

  useEffect(() => {
    function rememberSelection() {
      const current = window.getSelection();
      if (!current.rangeCount || !editor.current.contains(current.anchorNode) || !editor.current.contains(current.focusNode)) return;
      selection.current = current.getRangeAt(0).cloneRange();
      setActive(Object.fromEntries([...toggles].map(command => [command, document.queryCommandState(command)])));
    }
    document.addEventListener('selectionchange', rememberSelection);
    return () => document.removeEventListener('selectionchange', rememberSelection);
  }, []);

  function sync() {
    const next = serializeExperience(editor.current.innerHTML);
    if (next.length > EXPERIENCE_LIMIT) {
      editor.current.innerHTML = experienceHtml(value);
      selection.current = null;
      setError('Limite de 20 000 caractères atteinte, mise en forme comprise. Raccourcissez le texte avant d’en ajouter.');
      return;
    }
    emitted.current = next;
    setError('');
    onChange(next);
  }

  function command(name, text) {
    if (disabled) return;
    editor.current.focus();
    const current = window.getSelection();
    if (selection.current && editor.current.contains(selection.current.commonAncestorContainer)) {
      current.removeAllRanges();
      current.addRange(selection.current);
    }
    // Native editing keeps the browser's selection and undo history intact.
    document.execCommand(name === 'insertLineBreak' ? 'insertHTML' : name, false, name === 'insertLineBreak' ? '<br>' : text);
    sync();
    setActive(Object.fromEntries([...toggles].map(command => [command, document.queryCommandState(command)])));
  }

  return <div className="field experience-field">
    <span id={`${id}-label`}>Expérience professionnelle</span>
    <div className="experience-editor" aria-disabled={disabled}>
      <div className="experience-toolbar" role="group" aria-label="Mise en forme de l’expérience">
        {actions.map(([name, label, Icon]) => <button key={name} type="button" className="icon-button" title={label} aria-label={label}
          aria-pressed={toggles.has(name) ? !!active[name] : undefined} disabled={disabled}
          onMouseDown={event => event.preventDefault()} onClick={() => command(name)}><Icon size={17} /></button>)}
      </div>
      <div ref={editor} className="experience-content experience-input" contentEditable={!disabled} suppressContentEditableWarning
        role="textbox" aria-multiline="true" aria-labelledby={`${id}-label`} aria-describedby={`${id}-hint`} aria-invalid={!!error}
        data-placeholder="Décrivez les postes, missions et années d’expérience…" spellCheck
        onInput={event => { if (!event.nativeEvent.isComposing) sync(); }} onCompositionEnd={sync}
        onPaste={event => { event.preventDefault(); command('insertText', event.clipboardData.getData('text/plain')); }}
        onDrop={event => event.preventDefault()} />
    </div>
    <small id={`${id}-hint`}>Sélectionnez du texte pour le mettre en forme. Entrée : nouveau paragraphe · Maj + Entrée : nouvelle ligne.</small>
    {error && <small className="experience-error" role="alert">{error}</small>}
  </div>;
}

export function ExperienceText({ value }) {
  return <div className="experience-content" dangerouslySetInnerHTML={{ __html: experienceHtml(value) }} />;
}
