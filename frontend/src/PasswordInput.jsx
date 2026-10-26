import { useRef, useState } from 'react';
import { Eye, EyeOff, RefreshCw } from 'lucide-react';
import { generatePassword } from './utils';

export default function PasswordInput({ value, onChange, required, disabled }) {
  const input = useRef(null);
  const [visible, setVisible] = useState(false);
  const [notice, setNotice] = useState('');
  function generate() {
    try {
      onChange(generatePassword());
      setNotice('Mot de passe généré. Utilisez l’œil pour le consulter, puis enregistrez la fiche.');
      input.current.focus();
    } catch {
      setNotice('Génération indisponible. Vous pouvez saisir un mot de passe manuellement.');
    }
  }
  return <>
    <div className="password-input">
      <input ref={input} type={visible ? 'text' : 'password'} value={value} required={required} disabled={disabled}
        autoComplete="new-password" spellCheck={false} autoCapitalize="none"
        onChange={event => { onChange(event.target.value); setNotice(''); }} />
      <button type="button" className="icon-button password-generate" disabled={disabled} onClick={generate}
        title="Générer un mot de passe" aria-label="Générer un mot de passe"><RefreshCw size={17} /></button>
      <button type="button" className="icon-button" disabled={disabled} onClick={() => setVisible(current => !current)}
        title={visible ? 'Masquer le mot de passe' : 'Afficher le mot de passe'}
        aria-label={visible ? 'Masquer le mot de passe' : 'Afficher le mot de passe'} aria-pressed={visible}>
        {visible ? <EyeOff size={17} /> : <Eye size={17} />}
      </button>
    </div>
    {notice && <small role="status">{notice}</small>}
  </>;
}
