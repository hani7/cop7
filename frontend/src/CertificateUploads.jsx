import { useState } from 'react';
import { FileText, Plus, X } from 'lucide-react';
import { Field } from './components';

export default function CertificateUploads({ values, update }) {
  const [error, setError] = useState('');
  const uploads = values.certificate_uploads || [];
  const removed = values.remove_certificate_ids || [];
  const documents = values.certificate_documents || [];
  const firstUploadNumber = documents.length + 1;

  function selectFile(key, event) {
    const file = event.target.files?.[0];
    if (!file) return;
    setError('');
    if (!/\.(pdf|png|jpe?g)$/i.test(file.name) || file.size > 10 * 1024 * 1024) {
      setError('Choisissez un certificat PDF, JPG ou PNG de 10 Mo maximum.');
      event.target.value = '';
      update('certificate_uploads', uploads.map(row => row.key === key ? { ...row, file: null } : row));
      return;
    }
    update('certificate_uploads', uploads.map(row => row.key === key ? { ...row, file } : row));
  }

  return <section className="certificate-uploads" aria-label="Certificats et habilitations">
    <div className="cv-import-heading"><FileText size={21} /><div><h3>Certificats / Habilitations</h3><p>Ajoutez un fichier par certificat. PDF, JPG ou PNG · 10 Mo maximum par fichier · Sans limite de pages.</p></div></div>
    {documents.map(document => <div key={document.id} className={`certificate-saved${removed.includes(document.id) ? ' pending-removal' : ''}`}>
      <div><a href={document.url}>{document.name}</a><small>{removed.includes(document.id) ? 'Retrait à l’enregistrement' : 'Certificat enregistré'}</small></div>
      <button type="button" className="text-button" onClick={() => update('remove_certificate_ids', removed.includes(document.id) ? removed.filter(id => id !== document.id) : [...removed, document.id])}>
        {removed.includes(document.id) ? 'Conserver' : 'Retirer'}
      </button>
    </div>)}
    {uploads.map((row, index) => <div className="certificate-upload-row" key={row.key}>
      <Field label={`Certificat ${firstUploadNumber + index}`}>
        <input type="file" accept=".pdf,.png,.jpg,.jpeg,application/pdf,image/png,image/jpeg" onChange={event => selectFile(row.key, event)} />
      </Field>
      <button type="button" className="icon-button" aria-label={`Retirer le certificat ${firstUploadNumber + index}`} onClick={() => update('certificate_uploads', uploads.filter(item => item.key !== row.key))}><X size={18} /></button>
    </div>)}
    <button type="button" className="button secondary" disabled={uploads.length >= 20} onClick={() => update('certificate_uploads', [...uploads, { key: crypto.randomUUID(), file: null }])}>
      <Plus size={17} /> Ajouter un certificat
    </button>
    {error && <p className="alert error" role="alert">{error}</p>}
    {values.certificates && <p className="small prewrap">Informations déjà enregistrées : {values.certificates}</p>}
    <p className="muted small">Les ajouts et retraits seront appliqués en cliquant sur Enregistrer.</p>
  </section>;
}
