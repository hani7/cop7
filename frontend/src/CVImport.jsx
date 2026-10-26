import { useEffect, useRef, useState } from 'react';
import { FileUp, ImagePlus } from 'lucide-react';
import { api } from './api';
import { Field, Spinner } from './components';

export default function CVImport({ values, update }) {
  const [busy, setBusy] = useState(false);
  const [photoBusy, setPhotoBusy] = useState(false);
  const [error, setError] = useState('');
  const [preview, setPreview] = useState(null);
  const [warning, setWarning] = useState('');
  const [notice, setNotice] = useState('');
  const request = useRef(null);
  const fileInput = useRef(null);
  const currentExperience = useRef(values.experience);
  currentExperience.current = values.experience;
  useEffect(() => () => request.current?.abort(), []);

  function selectFile(event) {
    request.current?.abort(); request.current = null;
    setBusy(false); setError(''); setPreview(null); setWarning(''); setNotice('');
    const file = event.target.files?.[0];
    if (!file) return;
    if (!/\.(pdf|png|jpe?g)$/i.test(file.name) || file.size > 10 * 1024 * 1024) {
      setError('Choisissez un PDF, JPG ou PNG de 10 Mo maximum.');
      event.target.value = '';
      return;
    }
    update('cv', file);
  }

  async function extract() {
    const controller = new AbortController();
    request.current = controller;
    setBusy(true); setError(''); setPreview(null); setWarning(''); setNotice('');
    try {
      const hasNewFile = values.cv instanceof File && values.cv.size > 0;
      const options = { method: 'POST', signal: controller.signal };
      if (hasNewFile) {
        const body = new FormData();
        body.append('cv', values.cv);
        options.body = body;
      }
      const path = hasNewFile ? 'users/extract-cv/' : `users/${values.id}/extract-cv/`;
      const result = await api(path, options);
      if (!controller.signal.aborted) {
        if (result.experience?.trim() && !currentExperience.current?.trim()) {
          update('experience', result.experience);
          setNotice('Expérience ajoutée au champ ci-dessous. Vérifiez le texte, puis cliquez sur Enregistrer pour le sauvegarder.');
        } else {
          setPreview(result.experience || result.extracted_text || '');
        }
        setWarning(result.warning);
      }
    } catch (err) {
      if (!controller.signal.aborted) setError(err.message);
    } finally {
      if (!controller.signal.aborted) setBusy(false);
    }
  }

  async function extractPhoto() {
    setPhotoBusy(true); setError(''); setNotice('');
    try {
      const hasNewFile = values.cv instanceof File && values.cv.size > 0;
      const options = { method: 'POST' };
      if (hasNewFile) {
        const body = new FormData();
        body.append('cv', values.cv);
        options.body = body;
      }
      const path = hasNewFile ? 'users/extract-cv-photo/' : `users/${values.id}/extract-cv-photo/`;
      const result = await api(path, options);
      const bytes = Uint8Array.from(atob(result.photo), character => character.charCodeAt(0));
      update('photo', new File([bytes], 'photo-extraite-du-cv.png', { type: 'image/png' }));
      setNotice('Photo extraite du CV et ajoutée à l’aperçu. Cliquez sur Enregistrer pour la sauvegarder.');
    } catch (err) {
      setError(err.message);
    } finally {
      setPhotoBusy(false);
    }
  }

  return <section className="cv-import" aria-label="CV et extraction de l’expérience">
    <div className="cv-import-heading"><FileUp size={21} /><div><h3>Curriculum vitæ</h3><p>Importez le CV pour en extraire l’expérience professionnelle.</p></div></div>
    <p className="cv-save-reminder">L’extraction ne sauvegarde pas le fichier. Après l’avoir sélectionné, cliquez sur <strong>Enregistrer</strong> en bas du formulaire pour joindre le CV à la fiche.</p>
    <div className="field">
      <span>CV — PDF ou image</span>
      <button type="button" className="button secondary cv-file-picker" onClick={() => fileInput.current?.click()}>
        <FileUp size={16} />{values.cv instanceof File && values.cv.size > 0 ? 'Remplacer le CV' : 'Choisir le CV'}
      </button>
      <input ref={fileInput} className="cv-file-input" type="file" aria-label="Choisir le fichier CV" accept=".pdf,.png,.jpg,.jpeg,application/pdf,image/png,image/jpeg" onChange={selectFile} />
      <small>Facultatif · PDF, JPG ou PNG · 10 Mo maximum · Sans limite de pages</small>
    </div>
    {values.cv instanceof File && values.cv.size === 0 && <p className="small" role="status">Ce fichier est vide et ne sera pas joint. Vous pouvez enregistrer la fiche ou choisir un autre CV.</p>}
    {values.cv instanceof File && values.cv.size > 0 ? <p className="cv-selected-status" role="status">CV sélectionné : <strong>{values.cv.name}</strong>. Cliquez sur <strong>Enregistrer</strong> pour sauvegarder ce fichier.</p>
      : values.cv_url && <p className="small"><a href={values.cv_url}>Télécharger le CV enregistré : {values.cv_name}</a>. Le sélecteur de fichier ne peut pas afficher un fichier déjà enregistré.</p>}
    <button type="button" className="button secondary" disabled={busy || (!(values.cv instanceof File || values.cv_url) || (values.cv instanceof File && values.cv.size === 0))} onClick={extract}>
      {busy && <Spinner />}{busy ? 'Lecture du CV…' : values.cv_url && !(values.cv instanceof File) ? 'Extraire l’expérience du CV enregistré' : 'Extraire l’expérience du CV'}
    </button>
    <button type="button" className="button secondary" disabled={busy || photoBusy || (!(values.cv instanceof File || values.cv_url) || (values.cv instanceof File && values.cv.size === 0))} onClick={extractPhoto}>
      {photoBusy ? <Spinner /> : <ImagePlus size={16} />}{photoBusy ? 'Extraction de la photo…' : 'Utiliser la photo du CV'}
    </button>
    <div aria-live="polite">
      {error && <p className="alert error" role="alert">{error}</p>}
      {notice && <p className="cv-selected-status" role="status">{notice}</p>}
      {preview !== null && <div className="cv-preview">
        {warning && <p className="small">{warning}</p>}
        <Field label="Expérience extraite — à vérifier" hint="Corrigez le texte avant de l’utiliser dans la fiche.">
          <textarea rows={6} maxLength={20000} value={preview} onChange={event => setPreview(event.target.value)} />
        </Field>
        <button type="button" className="button secondary" disabled={!preview.trim()} onClick={() => { update('experience', preview); setPreview(null); setNotice('Expérience ajoutée au champ ci-dessous. Cliquez sur Enregistrer pour la sauvegarder.'); }}>
          {values.experience ? 'Remplacer l’expérience par ce texte' : 'Utiliser cette expérience'}
        </button>
      </div>}
    </div>
  </section>;
}
