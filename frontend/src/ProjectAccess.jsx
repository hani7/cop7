import { useEffect, useState } from 'react';
import { api } from './api';
import { Modal, RecordForm, Spinner } from './components';

export default function ProjectAccess({ project, save, onClose }) {
  const [access, setAccess] = useState(null);
  const [error, setError] = useState('');
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    let active = true;
    setError('');
    api(`projects/${project.id}/access/`).then(result => {
      if (active) setAccess(result);
    }).catch(err => { if (active) setError(err.message); });
    return () => { active = false; };
  }, [project.id, attempt]);
  return <Modal title={`Accès client · ${project.name}`} onClose={onClose}>
    {error ? <div className="detail alert error" role="alert">{error}<button className="text-button" onClick={() => setAttempt(value => value + 1)}>Réessayer</button></div>
      : !access ? <div className="detail" role="status"><Spinner /> Chargement de l’accès…</div>
      : <RecordForm initial={{ username: access.username || `projet-${project.id}`, password: '', is_active: access.configured ? access.is_active : true }} fields={[
        { name: 'link', wide: true, render: () => <div><p>Ce compte peut consulter et valider uniquement les pointages de ce projet.</p><a href={access.login_path} target="_blank" rel="noreferrer">{window.location.origin}{access.login_path}</a></div> },
        { name: 'username', label: 'Identifiant client', required: true },
        { name: 'password', label: access.configured ? 'Nouveau mot de passe (facultatif)' : 'Mot de passe', type: 'password', required: !access.configured, generate: true, hint: 'Notez le mot de passe pour le transmettre au client après enregistrement.' },
        { name: 'is_active', label: 'Accès actif', type: 'switch' },
      ]} submitLabel={access.configured ? 'Enregistrer l’accès' : 'Créer l’accès'} onClose={onClose} onSave={values => {
        const payload = { ...values };
        if (!payload.password) delete payload.password;
        return save(`projects/${project.id}/access/`, 'POST', payload);
      }} />}
  </Modal>;
}
