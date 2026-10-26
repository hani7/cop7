import { Field, Modal, RecordForm } from './components';
import { Building2, HardHat } from 'lucide-react';
import CVImport from './CVImport';
import ExperienceEditor from './ExperienceEditor';
import CertificateUploads from './CertificateUploads';
import TechnicianPhoto from './TechnicianPhoto';
import ClientLogo from './ClientLogo';
import { date, duration, localDate, maxBirthDate, money, number, roleLabels } from './utils';

const options = (rows, label = 'name') => rows.map(r => ({ value: r.id, label: r[label] }));
const text = (name, label, required = false, extra = {}) => ({ name, label, required, ...extra });
const select = (name, label, values, required = true) => text(name, label, required, { type: 'select', options: values });
const amount = (name, label, required = false) => text(name, label, required, { type: 'number', min: 0, step: '0.01' });
const localDay = value => {
  const current = new Date(value);
  return `${current.getFullYear()}-${String(current.getMonth() + 1).padStart(2, '0')}-${String(current.getDate()).padStart(2, '0')}`;
};

export default function Editor({ modal, data, user, save, close }) {
  const row = modal.row;
  const editing = !!row;
  let title, fields, initial, resource, transform = x => x, extra, submitLabel;
  if (modal.type === 'client') {
    title = editing ? 'Modifier le Client' : 'Nouveau Client'; resource = 'clients';
    fields = [
      { name: 'logo', wide: true, render: (current, update) => <ClientLogo values={current} update={update} /> },
      text('name', 'Société', true, { maxLength: 160 }),
      text('contact_name', 'Personne à contacter', true),
      text('email', 'Email', true, { type: 'email' }),
      text('phone', 'Téléphone', true),
      text('rc', 'N° RC', true),
      text('nif', 'NIF', true),
      text('article_number', 'N° article', true),
      text('nis', 'NIS', true),
      text('billing_address', 'Adresse', true, { type: 'textarea', wide: true }),
      text('start_work_date', 'Date de début de travail', true, { type: 'date' }),
      text('is_active', 'Client actif', true, { type: 'switch', wide: true }),
    ];
    initial = row ? { ...row, logo: null } : { name: '', contact_name: '', email: '', phone: '', rc: '', nif: '', article_number: '', nis: '', billing_address: '', start_work_date: '', logo: null, is_active: true };
    transform = values => {
      const { id, logo_url, logo, ...client } = values;
      if (!(logo instanceof File) || logo.size === 0) return client;
      const body = new FormData();
      Object.entries(client).forEach(([key, value]) => body.append(key, value ?? ''));
      body.append('logo', logo);
      return body;
    };
  } else if (modal.type === 'holiday') {
    title = editing ? 'Modifier le jour férié' : 'Ajouter un jour férié'; resource = 'holidays';
    fields = [text('name', 'Nom du jour férié', true, { maxLength: 120 }), text('date', 'Date', true, { type: 'date' })];
    initial = row || { name: '', date: localDate() };
  } else if (modal.type === 'user' || modal.type === 'technician') {
    const technicianOnly = modal.type === 'technician';
    title = technicianOnly ? (editing ? 'Modifier le Technicien' : 'Nouveau Technicien') : (editing ? 'Modifier le collaborateur' : 'Nouveau collaborateur');
    resource = 'users';
    fields = values => [
      { name: 'technician_photo', hidden: values.role !== 'TECHNICIAN', render: (current, update) => <TechnicianPhoto values={current} update={update} /> },
      text('last_name', 'Nom', true, { className: 'technician-uppercase' }), text('first_name', 'Prénom', true, { className: 'technician-uppercase' }),
      { ...text('birth_date', 'Date de naissance', false, { type: 'date', max: maxBirthDate() }), hidden: values.role !== 'TECHNICIAN' },
      text('specialty', 'Poste / Spécialité', false, { maxLength: 120, className: 'technician-uppercase' }),
      { ...text('address', 'Adresse', false, { type: 'textarea', maxLength: 2000, wide: true, className: 'technician-uppercase' }), hidden: values.role !== 'TECHNICIAN' },
      text('phone', 'Téléphone', false, { type: 'tel', maxLength: 10, pattern: '[0-9]{10}', inputMode: 'numeric', hint: 'Saisissez 10 chiffres.' }),
      text('email', 'Email', false, { type: 'email' }),
      { ...text('assignment_date', 'Date d’affectation', false, { type: 'date' }), hidden: values.role !== 'TECHNICIAN', className: 'technician-assignment-date' },
      { name: 'employee_number', hidden: values.role !== 'TECHNICIAN', wide: false, render: current => <Field label="Matricule" hint="Généré automatiquement à l’enregistrement." className="technician-assignment-number"><input value={current.employee_number || ''} placeholder="Attribué automatiquement à la création" readOnly /></Field> },
      { name: 'cv_import', hidden: values.role !== 'TECHNICIAN', render: (current, update) => <CVImport values={current} update={update} /> },
      { name: 'experience', hidden: values.role !== 'TECHNICIAN', render: (current, update, busy) => <ExperienceEditor value={current.experience} onChange={value => update('experience', value)} disabled={busy} /> },
      { name: 'certificate_attachments', hidden: values.role !== 'TECHNICIAN', render: (current, update) => <CertificateUploads values={current} update={update} /> },
      text('username', 'Identifiant de connexion', true),
      text('password', editing ? 'Nouveau mot de passe (facultatif)' : 'Mot de passe', !editing, { type: 'password', autocomplete: 'new-password', generate: true }),
      { ...select('role', 'Rôle', Object.entries(roleLabels).map(([value, label]) => ({ value, label }))), hidden: technicianOnly },
      { ...select('client', 'Entreprise cliente', options(data.clients.filter(c => c.is_active))), hidden: technicianOnly || values.role !== 'PROJECT_MANAGER' },
      text('is_active', 'Compte actif', false, { type: 'switch' }),
    ];
    initial = row ? { ...row, password: '' } : { username: '', first_name: '', last_name: '', email: '', password: '', role: 'TECHNICIAN', client: '', specialty: '', phone: '', birth_date: '', assignment_date: '', address: '', experience: '', certificates: '', is_active: true };
    initial = { ...initial, certificate_uploads: [{ key: 'first-certificate', file: null }], remove_certificate_ids: [] };
    transform = values => {
      const role = technicianOnly ? 'TECHNICIAN' : values.role;
      const result = { ...values, role, client: role === 'PROJECT_MANAGER' ? Number(values.client) : null, birth_date: values.birth_date || null };
      if (role === 'TECHNICIAN') {
        for (const field of ['last_name', 'first_name', 'specialty', 'address']) {
          if (typeof result[field] === 'string') result[field] = result[field].toLocaleUpperCase();
        }
      }
      const certificateFiles = (values.certificate_uploads || []).map(row => row.file).filter(Boolean);
      for (const key of ['id', 'full_name', 'client_name', 'cv_name', 'cv_url', 'photo_url', 'employee_number', 'hourly_cost', 'certificate_documents', 'certificate_uploads', 'certificates']) delete result[key];
      if (!result.password) delete result.password;
      const cvSelected = values.cv instanceof File && values.cv.size > 0;
      if (!(result.cv instanceof File) || result.cv.size === 0) delete result.cv;
      if (!(result.photo instanceof File) || result.photo.size === 0) delete result.photo;
      if (cvSelected && !(result.cv instanceof File)) {
        throw new Error('Le CV sélectionné n’a pas été joint au formulaire. Choisissez-le à nouveau.');
      }
      if (result.cv instanceof File || result.photo instanceof File || certificateFiles.length) {
        const body = new FormData();
        Object.entries(result).forEach(([key, value]) => {
          if (Array.isArray(value)) value.forEach(item => body.append(key, item));
          else body.append(key, value ?? '');
        });
        certificateFiles.forEach(file => body.append('certificate_files', file));
        if (cvSelected && !body.has('cv')) {
          throw new Error('Le CV sélectionné n’a pas été joint au formulaire. Choisissez-le à nouveau.');
        }
        return body;
      }
      return result;
    };
  } else if (modal.type === 'project') {
    title = editing ? 'Modifier le projet' : 'Nouveau projet'; resource = 'projects';
    const technicians = data.users.filter(u => u.role === 'TECHNICIAN' && u.is_active).map(u => ({
      value: u.id,
      label: `${u.full_name || u.username}${u.specialty ? ` - ${u.specialty}` : ''}`,
    }));
    fields = [
      text('name', 'Nom du projet', true),
      text('client', 'Client', true, { type: 'searchable-select', options: options(data.clients.filter(c => c.is_active)) }),
      text('site', 'Site industriel', true),
      text('manager_name', 'Chef de projet client', true),
      text('purchase_order', 'Bon de commande'),
      text('description', 'Description', false, { type: 'textarea' }),
      text('technicians', 'Techniciens affectés', false, { type: 'searchable-multiselect', options: technicians, hint: 'Recherchez puis sélectionnez un ou plusieurs techniciens.', wide: true }),
      {
        name: 'commercial-info',
        type: 'group',
        label: 'Informations commerciales',
        className: 'project-commercial-info',
        fields: [
          amount('hourly_rate', `Tarif client / heure (${user.currency})`, true),
          amount('holiday_billing_day_rate', `Tarif facture journée fériée (${user.currency})`, true),
          amount('technician_hourly_rate', `Coût technicien / heure (${user.currency})`, true),
          amount('holiday_day_rate', `Coût technicien journée fériée (${user.currency})`, true),
        ],
      },
    ];
    initial = row ? { ...row, manager_name: row.manager_name || '' } : { name: '', client: '', site: '', manager_name: '', technicians: [], hourly_rate: '', holiday_billing_day_rate: '0', technician_hourly_rate: '0', holiday_day_rate: '0', purchase_order: '', description: '' };
    transform = values => {
      const { project_manager, ...project } = values;
      return { ...project, client: Number(values.client), technicians: (values.technicians || []).map(Number) };
    };
  } else if (modal.type === 'time') {
    title = editing ? 'Corriger le pointage' : 'Nouveau pointage'; resource = 'time-entries';
    const activeProjects = data.projects.filter(p => p.status === 'ACTIVE' && p.technicians.includes(user.id));
    fields = [
      select('project', 'Projet en cours', options(activeProjects)),
      text('work_date', 'Date de l’intervention', true, { type: 'date', max: localDate() }),
      text('hours', 'Nombre d’heures travaillées ce jour', true, { type: 'number', min: 0.02, max: 24, step: 0.01, inputMode: 'decimal' }),
      text('description', 'Travaux réalisés', true, { type: 'textarea' }),
    ];
    initial = row
      ? { project: row.project, work_date: localDay(row.start), hours: duration(row.start, row.end, row.break_minutes), description: row.description }
      : { project: activeProjects[0]?.id || '', work_date: localDate(), hours: '', description: '' };
    transform = values => {
      const hours = Number(values.hours);
      if (!values.work_date || !Number.isFinite(hours) || hours < 0.02 || hours > 24) {
        throw new Error('Saisissez une date et un nombre d’heures compris entre 0,02 et 24.');
      }
      const [year, month, day] = values.work_date.split('-').map(Number);
      const previousStart = editing ? new Date(row.start) : null;
      const start = new Date(
        year, month - 1, day,
        previousStart ? previousStart.getHours() : 8,
        previousStart ? previousStart.getMinutes() : 0,
        previousStart ? previousStart.getSeconds() : 0,
        previousStart ? previousStart.getMilliseconds() : 0,
      );
      if (localDay(start) !== values.work_date || start > new Date()) {
        throw new Error('La date de l’intervention ne peut pas être dans le futur.');
      }
      const end = new Date(start.getTime() + hours * 60 * 60 * 1000);
      if (end > new Date(Date.now() + 60_000)) {
        throw new Error('Le nombre d’heures dépasse le temps écoulé depuis le début de la journée.');
      }
      return { project: Number(values.project), start: start.toISOString(), end: end.toISOString(), break_minutes: 0, description: values.description };
    };
    extra = values => <div className="form-summary"><span>Heures déclarées ce jour</span><strong>{number(values.hours || 0)} h</strong></div>;
  } else if (modal.type === 'reject') {
    title = 'Refuser le pointage';
    fields = [text('reason', 'Motif du refus', true, { type: 'textarea', maxLength: 2000 })];
    initial = { reason: '' }; submitLabel = 'Refuser le pointage';
  } else if (modal.type === 'invoice') {
    title = 'Créer une facture'; resource = 'invoices';
    const due = new Date(); due.setDate(due.getDate() + 30);
    fields = [select('project', 'Projet à facturer', options(data.projects.filter(p => data.entries.some(e => e.project === p.id && e.status === 'APPROVED')))), text('due_date', 'Date d’échéance', true, { type: 'date', min: localDate() }), amount('tax_percent', 'Taxe (%)', true)];
    initial = { project: '', due_date: localDate(due), tax_percent: '0', entry_ids: [] };
    submitLabel = 'Émettre la facture';
    extra = (values, update) => {
      const entries = data.entries.filter(e => String(e.project) === String(values.project) && e.status === 'APPROVED');
      const project = data.projects.find(p => String(p.id) === String(values.project));
      const selected = entries.filter(e => values.entry_ids.includes(e.id));
      const holidayDates = new Set(data.holidays.map(holiday => holiday.date));
      const holidayEntries = new Set();
      let subtotal = 0;
      for (const entry of selected) {
        const workDate = localDay(entry.start);
        if (holidayDates.has(workDate)) holidayEntries.add(`${entry.technician}:${workDate}`);
        else subtotal += Math.round(Number(entry.hours) * Number(project?.hourly_rate || 0) * 100) / 100;
      }
      subtotal += holidayEntries.size * Number(project?.holiday_billing_day_rate || 0);
      return <div className="invoice-selection"><h3>Pointages validés à facturer</h3>{!entries.length && <p className="muted">Choisissez un projet avec des heures validées.</p>}{entries.map(e => <label className="check-row" key={e.id}><input type="checkbox" checked={values.entry_ids.includes(e.id)} onChange={event => update('entry_ids', event.target.checked ? [...values.entry_ids, e.id] : values.entry_ids.filter(id => id !== e.id))} /><span><strong>{e.technician_name}</strong><small>{date(e.start)} · {e.description}</small></span><b>{number(e.hours)} h</b></label>)}<div className="form-summary"><span>Total estimé TTC</span><strong>{money(subtotal * (1 + Number(values.tax_percent) / 100), user.currency)}</strong></div><p className="muted small">Les heures et les tarifs seront figés à l’émission.</p></div>;
    };
    transform = values => {
      const ids = values.entry_ids.filter(id => data.entries.some(e => e.id === id && String(e.project) === String(values.project)));
      if (!ids.length) throw new Error('Sélectionnez au moins un pointage validé.');
      return { ...values, project: Number(values.project), entry_ids: ids };
    };
  } else if (modal.type === 'payment') {
    title = 'Enregistrer un paiement'; resource = 'payments';
    fields = [select('invoice', 'Facture', data.invoices.filter(i => Number(i.balance) > 0).map(i => ({ value: i.id, label: `${i.number} · ${i.client_name} · ${money(i.balance, i.currency)}` }))), amount('amount', 'Montant reçu', true), text('date', 'Date du paiement', true, { type: 'date', max: localDate() }), select('method', 'Mode de paiement', [{ value: 'TRANSFER', label: 'Virement' }, { value: 'CHECK', label: 'Chèque' }, { value: 'CASH', label: 'Espèces' }]), text('reference', 'Référence du paiement')];
    initial = { invoice: modal.invoice?.id || '', amount: modal.invoice?.balance || '', date: localDate(), method: 'TRANSFER', reference: '' };
  }
  return <Modal title={title} titleIcon={modal.type === 'technician' ? <HardHat size={20} aria-hidden="true" /> : modal.type === 'client' ? <Building2 size={20} aria-hidden="true" /> : null} onClose={close}><RecordForm fields={fields} initial={initial} onClose={close} submitLabel={submitLabel} fullWidthActions={modal.type === 'technician' || modal.type === 'user'} fieldLabelsUppercase={modal.type === 'client'} onSave={values => modal.type === 'reject' ? save(`time-entries/${row.id}/reject/`, 'POST', values) : save(`${resource}/${editing ? row.id + '/' : ''}`, editing ? 'PATCH' : 'POST', transform(values))}>{extra}</RecordForm></Modal>;
}
