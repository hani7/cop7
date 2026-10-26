import { useEffect, useMemo, useRef, useState } from 'react';
import { ImagePlus } from 'lucide-react';
import { Field } from './components';

export default function ClientLogo({ values, update }) {
  const input = useRef(null);
  const [error, setError] = useState('');
  const preview = useMemo(() => values.logo instanceof File
    ? URL.createObjectURL(values.logo)
    : values.logo_url || '', [values.logo, values.logo_url]);

  useEffect(() => () => {
    if (values.logo instanceof File && preview) URL.revokeObjectURL(preview);
  }, [values.logo, preview]);

  function selectLogo(event) {
    const file = event.target.files?.[0];
    setError('');
    if (!file) return;
    if (!/\.(png|jpe?g|jgp|webp|avif)$/i.test(file.name) || file.size > 5 * 1024 * 1024) {
      setError('Choisissez un logo PNG, WebP, JPG/JPEG ou AVIF de 5 Mo maximum.');
      event.target.value = '';
      return;
    }
    update('logo', file);
  }

  return <section className="technician-photo client-logo-upload" aria-label="Logo de l’entreprise">
    <div className="cv-import-heading"><ImagePlus size={21} /><div><h3>Logo de l’entreprise</h3><p>Ajoutez le logo pour identifier votre entreprise cliente.</p></div></div>
    <div className="technician-photo-content">
      {preview && <img className="client-logo-preview" src={preview} alt="Aperçu du logo de l’entreprise" />}
      <Field label="Logo — PNG, WebP, JPG/JPEG ou AVIF" hint="Facultatif · 5 Mo maximum">
        <input ref={input} type="file" accept=".png,.webp,.jpg,.jpeg,.jgp,.avif,image/png,image/webp,image/jpeg,image/avif" onChange={selectLogo} />
      </Field>
    </div>
    {values.logo instanceof File && <p className="small">Logo à enregistrer : <strong>{values.logo.name}</strong></p>}
    {error && <p className="alert error" role="alert">{error}</p>}
  </section>;
}
