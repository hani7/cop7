import { useEffect, useRef, useState } from 'react';
import { X, LoaderCircle, FolderOpen, Save, Search, ChevronDown, BriefcaseBusiness, Plus, Check } from 'lucide-react';
import { statusLabels } from './utils';
import PasswordInput from './PasswordInput';

export function Badge({ status }) { return <span className={`badge status-${status.toLowerCase()}`}>{statusLabels[status] || status}</span>; }
export function Spinner() { return <LoaderCircle size={18} className="spin" aria-label="Chargement" />; }
export function Empty({ title = 'Aucun résultat', text = 'Les éléments apparaîtront ici dès leur création.', action }) {
  return <div className="empty"><span className="empty-icon"><FolderOpen size={30} /></span><h3>{title}</h3><p>{text}</p>{action}</div>;
}
export function Modal({ title, children, onClose, wide = false, titleIcon, headerExtra }) {
  const ref = useRef(null);
  useEffect(() => {
    const dialog = ref.current;
    dialog.showModal();
    return () => dialog.close();
  }, []);
  return <dialog ref={ref} className={wide ? 'modal wide' : 'modal'} onCancel={e => { e.preventDefault(); onClose(); }}>
    <header className="modal-header"><div className="modal-title">{titleIcon}<h2>{title}</h2></div>{headerExtra && <div className="modal-header-extra">{headerExtra}</div>}<button className="icon-button" onClick={onClose} aria-label="Fermer"><X size={21} /></button></header>{children}
  </dialog>;
}
export function Field({ label, children, hint, wide = false, className = '' }) {
  return <label className={`field${wide ? ' field-wide' : ''}${className ? ` ${className}` : ''}`}><span>{label}</span>{children}{hint && <small>{hint}</small>}</label>;
}

function SearchableSelect({ id, label, options, value, required, multiple = false, onChange }) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [activeIndex, setActiveIndex] = useState(0);
  const inputRef = useRef(null);
  const selectedValues = multiple ? (Array.isArray(value) ? value : []).map(String) : [];
  const selectedOptions = multiple
    ? options.filter(option => selectedValues.includes(String(option.value)))
    : [];
  const selected = multiple ? null : options.find(option => String(option.value) === String(value));
  const matches = options.filter(option => option.label.toLocaleLowerCase().includes(query.trim().toLocaleLowerCase()));
  const selectOption = option => {
    if (multiple) {
      const updatedValues = selectedValues.includes(String(option.value))
        ? selectedValues.filter(selectedValue => selectedValue !== String(option.value))
        : [...selectedValues, String(option.value)];
      onChange(updatedValues);
      setQuery('');
      setActiveIndex(0);
      inputRef.current?.focus();
      return;
    }
    onChange(option.value);
    inputRef.current?.setCustomValidity('');
    setQuery('');
    setOpen(false);
  };

  return <div className="search-select">
    <div className="search-select-input">
      <Search size={15} aria-hidden="true" />
      <input
        ref={inputRef}
        id={id}
        type="text"
        role="combobox"
        aria-label={label}
        aria-autocomplete="list"
        aria-expanded={open}
        aria-controls={`${id}-options`}
        autoComplete="off"
        required={required && !(multiple ? selectedValues.length : value)}
        value={open || multiple ? query : selected?.label || ''}
        placeholder={multiple ? `Rechercher ${label.toLocaleLowerCase()}...` : 'Rechercher un client...'}
        onFocus={() => { setQuery(''); setActiveIndex(0); setOpen(true); }}
        onChange={event => {
          setQuery(event.target.value);
          setActiveIndex(0);
          if (!multiple) {
            onChange('');
            event.target.setCustomValidity('');
          }
        }}
        onInvalid={event => event.currentTarget.setCustomValidity(`Sélectionnez ${multiple ? 'au moins une option' : 'un client'} dans la liste.`)}
        onKeyDown={event => {
          if (event.key === 'ArrowDown') {
            event.preventDefault();
            setActiveIndex(index => Math.min(index + 1, matches.length - 1));
          } else if (event.key === 'ArrowUp') {
            event.preventDefault();
            setActiveIndex(index => Math.max(index - 1, 0));
          } else if (event.key === 'Enter' && open && matches[activeIndex]) {
            event.preventDefault();
            selectOption(matches[activeIndex]);
          } else if (event.key === 'Escape') {
            event.preventDefault();
            setOpen(false);
            setQuery('');
          }
        }}
        onBlur={() => { setOpen(false); setQuery(''); }}
      />
      <ChevronDown size={15} aria-hidden="true" />
    </div>
    {multiple && selectedOptions.length > 0 && <div className="search-select-chips">
      {selectedOptions.map(option => <span className="search-select-chip" key={option.value}>
        {option.label}
        <button type="button" aria-label={`Retirer ${option.label}`} onMouseDown={event => event.preventDefault()} onClick={() => selectOption(option)}><X size={13} aria-hidden="true" /></button>
      </span>)}
    </div>}
    {open && <div className="search-select-options" id={`${id}-options`} role="listbox" aria-label={label} aria-multiselectable={multiple || undefined}>
      {matches.length ? matches.map((option, index) => <button
        key={option.value}
        type="button"
        role="option"
        aria-selected={multiple ? selectedValues.includes(String(option.value)) : String(option.value) === String(value)}
        className={`${index === activeIndex ? 'active' : ''}${multiple && selectedValues.includes(String(option.value)) ? ' selected' : ''}`}
        onMouseDown={event => event.preventDefault()}
        onClick={() => selectOption(option)}
      ><span>{option.label}</span>{multiple && (selectedValues.includes(String(option.value)) ? <Check size={15} aria-hidden="true" /> : <Plus size={15} aria-hidden="true" />)}</button>) : <span className="search-select-empty">Aucun résultat trouvé</span>}
    </div>}
  </div>;
}

export function RecordForm({ fields, initial, onSave, onClose, submitLabel = 'Enregistrer', fullWidthActions = false, fieldLabelsUppercase = false, children }) {
  const [values, setValues] = useState(initial);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const update = (key, value) => setValues(old => ({ ...old, [key]: value }));
  const resolved = typeof fields === 'function' ? fields(values) : fields;
  const renderField = f => f.render ? <div className={f.wide === false ? '' : 'field-wide'} key={f.name}>{f.render(values, update, busy)}</div> : ['searchable-select', 'searchable-multiselect'].includes(f.type) ? <div key={f.name} className={`field${f.wide ? ' field-wide' : ''}${f.required ? ' field-required' : ''}`}>
    <label htmlFor={`field-${f.name}`}>{f.label}</label>
    <SearchableSelect id={`field-${f.name}`} label={f.label} options={f.options} value={values[f.name] ?? (f.type === 'searchable-multiselect' ? [] : '')} required={f.required} multiple={f.type === 'searchable-multiselect'} onChange={value => update(f.name, value)} />
    {f.hint && <small>{f.hint}</small>}
  </div> : <Field key={f.name} label={f.label} hint={f.hint} wide={f.wide} className={`${f.className || ''}${f.required ? ' field-required' : ''}`}>
    {f.type === 'select' ? <select required={f.required} value={values[f.name] ?? ''} onChange={e => update(f.name, e.target.value)}>
      <option value="">Sélectionner…</option>{f.options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
    </select> : f.type === 'multiselect' ? <select multiple value={(values[f.name] || []).map(String)} onChange={e => update(f.name, [...e.target.selectedOptions].map(o => Number(o.value)))}>
      {f.options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
    </select> : f.type === 'textarea' ? <textarea rows={3} required={f.required} maxLength={f.maxLength} value={values[f.name] ?? ''} onChange={e => update(f.name, e.target.value)} />
      : f.type === 'checkbox' ? <input type="checkbox" checked={!!values[f.name]} onChange={e => update(f.name, e.target.checked)} />
      : f.type === 'switch' ? <span className="account-switch">
        <input className="status-switch" type="checkbox" role="switch" aria-label={f.label} checked={!!values[f.name]} onChange={e => update(f.name, e.target.checked)} />
        <span aria-hidden="true">{values[f.name] ? 'Actif' : 'Inactif'}</span>
      </span>
        : f.type === 'password' && f.generate ? <PasswordInput value={values[f.name] ?? ''} required={f.required} disabled={busy} onChange={value => update(f.name, value)} />
        : <input type={f.type || 'text'} required={f.required} min={f.min} max={f.max} step={f.step} minLength={f.minLength} maxLength={f.maxLength} pattern={f.pattern} inputMode={f.inputMode} autoComplete={f.autocomplete || 'off'} value={values[f.name] ?? ''} onChange={e => update(f.name, e.target.value)} />}
  </Field>;
  async function submit(event) {
    event.preventDefault(); setBusy(true); setError('');
    try { await onSave(values); } catch (err) { setError(err.message); setBusy(false); }
  }
  return <form onSubmit={submit} className={`record-form${fieldLabelsUppercase ? ' field-labels-uppercase' : ''}`}>
    <fieldset disabled={busy} className="form-fields"><div className="form-grid">
      {resolved.filter(f => !f.hidden).map(f => f.type === 'group' ? <section className={`form-field-group field-wide ${f.className || ''}`} key={f.name}>
        <h3><BriefcaseBusiness size={16} aria-hidden="true" />{f.label}</h3>
        <div className="form-grid">{f.fields.filter(field => !field.hidden).map(renderField)}</div>
      </section> : renderField(f))}
    </div>{children?.(values, update)}</fieldset>
    {error && <div className="alert error" role="alert">{error}</div>}
    <footer className={`form-footer${fullWidthActions ? ' form-footer-split' : ''}`}><button type="button" className="button secondary" onClick={onClose} disabled={busy}><X size={16} aria-hidden="true" />Annuler</button><button type="submit" className="button" disabled={busy}>{busy ? <Spinner /> : <Save size={17} aria-hidden="true" />}{submitLabel}</button></footer>
  </form>;
}

export function Table({ columns, rows, rowKey = 'id', empty }) {
  if (!rows.length) return empty || <Empty />;
  return <div className="table-scroll"><table><thead><tr>{columns.map(c => <th key={c.label}>{c.label}</th>)}</tr></thead><tbody>{rows.map(row => <tr key={row[rowKey]}>{columns.map(c => <td key={c.label}>{c.render(row)}</td>)}</tr>)}</tbody></table></div>;
}
