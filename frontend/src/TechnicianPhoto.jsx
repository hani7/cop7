import { useEffect, useMemo, useRef, useState } from 'react';
import { ImagePlus } from 'lucide-react';
import { Field } from './components';

export default function TechnicianPhoto({ values, update }) {
  const [error, setError] = useState('');
  const photo = useMemo(() => values.photo instanceof File ? URL.createObjectURL(values.photo) : values.photo_url,
    [values.photo, values.photo_url]);

  useEffect(() => {
    setError('');
  }, [values.cv]);
  useEffect(() => () => {
    if (values.photo instanceof File && photo) URL.revokeObjectURL(photo);
  }, [values.photo, photo]);

  function selectPhoto(event) {
    const file = event.target.files?.[0];
    setError('');
    if (!file) return;
    if (!/\.(png|jpe?g|jgp|webp|avif)$/i.test(file.name) || file.size > 5 * 1024 * 1024) {
      setError('Choisissez une photo PNG, WebP, JPG/JPEG ou AVIF de 5 Mo maximum.');
      event.target.value = '';
      return;
    }
    update('photo', file);
  }

  return <section className="technician-photo" aria-label="Photo de profil du technicien">
    <div className="cv-import-heading"><ImagePlus size={21} /><div><h3>Photo du technicien</h3></div></div>
    <div className="technician-photo-content">
      {photo && <img className="technician-photo-preview" src={photo} alt="Aperçu de la photo de profil" />}
      <Field label="Photo — PNG, WebP, JPG/JPEG ou AVIF" hint="Facultatif · 5 Mo maximum · Une photo importée remplace l’image du CV">
        <input type="file" accept=".png,.webp,.jpg,.jpeg,.jgp,.avif,image/png,image/webp,image/jpeg,image/avif" onChange={selectPhoto} />
      </Field>
    </div>
    {values.photo instanceof File && <p className="small">Photo à enregistrer : <strong>{values.photo.name}</strong></p>}
    {error && <p className="alert error" role="alert">{error}</p>}
  </section>;
}
