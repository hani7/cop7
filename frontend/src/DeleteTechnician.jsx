import { useState } from 'react';
import { Modal, Spinner } from './components';

export default function DeleteTechnician({ technician, onDelete, onClose }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  async function remove(event) {
    event.preventDefault();
    if (busy) return;
    setBusy(true); setError('');
    try { await onDelete(technician); }
    catch (err) { setError(err.message); setBusy(false); }
  }
  return <Modal title="Supprimer le technicien" onClose={() => { if (!busy) onClose(); }}>
    <form className="record-form" onSubmit={remove}>
      <p>Déplacer <strong>{technician.full_name}</strong> vers la corbeille ?</p>
      <p className="muted small">Le technicien pourra être restauré depuis Paramètres → Corbeille.</p>
      {error && <div className="alert error" role="alert">{error}</div>}
      <footer className="form-footer"><button type="button" className="button secondary" disabled={busy} onClick={onClose} autoFocus>Annuler</button><button type="submit" className="button" disabled={busy}>{busy && <Spinner />}Supprimer</button></footer>
    </form>
  </Modal>;
}
