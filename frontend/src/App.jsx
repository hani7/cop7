import { Fragment, useCallback, useEffect, useState } from 'react';
import { ArrowDownLeft, ArrowRight, ArrowUpRight, BriefcaseBusiness, Building2, CalendarDays, Check, CheckCheck, ChevronDown, ChevronRight, Clock3, CreditCard, Download, Eye, FileText, HardHat, LayoutDashboard, LogOut, Pencil, Plus, RefreshCw, Search, Send, Settings, ShieldCheck, Trash2, Users, X } from 'lucide-react';
import { api, listAll } from './api';
import { Badge, Empty, Field, Modal, Spinner, Table } from './components';
import Editor from './forms';
import { ExperienceText } from './ExperienceEditor';
import DeleteTechnician from './DeleteTechnician';
import ProjectAccess from './ProjectAccess';
import headerLogo from './assets/CO-1-1-1.png';
import reportLogo from './assets/copetroelite-report-logo.png';
import welcomeVideo from './assets/video-welcome.mp4';
import welcomePoster from './assets/inspection-refinery.jpg';
import { age, date, money, number, roleLabels, statusLabels, time } from './utils';

const NAV = [
  { id: 'dashboard', label: 'Vue d’ensemble', icon: LayoutDashboard },
  { id: 'projects', label: 'Projets', icon: BriefcaseBusiness },
  { id: 'entries', label: 'Pointages', icon: Clock3 },
  { id: 'technicians', label: 'Techniciens', icon: HardHat, roles: ['ADMIN', 'SUPERVISOR', 'PROJECT_MANAGER'] },
  { id: 'users', label: 'Équipe', icon: Users, roles: ['ADMIN', 'SUPERVISOR'] },
  { id: 'clients', label: 'Clients', icon: Building2, roles: ['ADMIN', 'SUPERVISOR'] },
  { id: 'holidays', label: 'Calendrier', icon: CalendarDays, roles: ['ADMIN'] },
  { id: 'invoices', label: 'Facturation', icon: FileText, roles: ['ADMIN'] },
  { id: 'payments', label: 'Paiements', icon: CreditCard, roles: ['ADMIN', 'TECHNICIAN'] },
  { id: 'technician-payments', label: 'Charges techniciens', icon: CreditCard, roles: ['ADMIN'] },
];
const FINANCE_NAV = [
  { id: 'invoices', label: 'Facturation', icon: FileText, roles: ['ADMIN'] },
  { id: 'payments', label: 'Paiements', icon: CreditCard, roles: ['ADMIN', 'TECHNICIAN'] },
  { id: 'technician-payments', label: 'Charges techniciens', icon: CreditCard, roles: ['ADMIN'] },
];
const descriptions = { dashboard: 'Le suivi de vos équipes et de vos interventions, en un seul endroit.', projects: 'Organisez les interventions et affectez les bonnes équipes.', entries: 'Des heures saisies sur le terrain aux heures validées par le client.', technicians: 'Retrouvez les fiches, spécialités et affectations de vos techniciens.', users: 'Les personnes qui font avancer vos projets.', clients: 'Retrouvez vos entreprises clientes et leurs coordonnées.', holidays: 'Gérez les jours fériés utilisés pour calculer les coûts de main-d’œuvre.', specialties: 'Ajoutez les spécialités disponibles pour les techniciens.', trash: 'Restaurez les projets, techniciens et clients archivés.', invoices: 'Transformez les heures validées en factures.', payments: 'Gardez une vision claire des règlements reçus.' };
descriptions['technician-payments'] = 'Suivez les paiements et charges versés aux techniciens.';
const emptyData = { projects: [], entries: [], users: [], clients: [], holidays: [], specialties: [], invoices: [], payments: [], technicianPayments: [], trash: { projects: [], technicians: [], clients: [] }, dashboard: {} };
const PAGE_STORAGE_KEY = 'copetrolite-current-page';
const technicianLogin = window.location.pathname.replace(/\/+$/, '') === '/tech/login';
const projectLogin = window.location.pathname.replace(/\/+$/, '') === '/project/login';
function Brand() { return <div className="brand"><img className="login-brand-logo" src={headerLogo} alt="Copetrolite" /></div>; }

function Login({ onLogin, initialError, retry, technicianOnly = false, projectOnly = false }) {
  const [username, setUsername] = useState(''); const [password, setPassword] = useState('');
  const [error, setError] = useState(''); const [busy, setBusy] = useState(false);
  async function submit(event) {
    event.preventDefault(); setBusy(true); setError('');
    try {
      await api('auth/session/');
      const response = await api(projectOnly ? 'auth/project-login/' : 'auth/login/', { method: 'POST', body: { username, password } });
      if (technicianOnly && response.user.role !== 'TECHNICIAN') {
        await api('auth/logout/', { method: 'POST', body: {} });
        throw new Error('Cet accès est réservé aux comptes techniciens.');
      }
      onLogin(response.user);
    }
    catch (err) { setError(err.message); } finally { setBusy(false); }
  }
  return <main className={`login${technicianOnly || projectOnly ? ' login-technician' : ''}`}>
    <section className="login-story"><video className="login-story-video" autoPlay loop muted playsInline poster={welcomePoster} aria-hidden="true"><source src={welcomeVideo} type="video/mp4" /></video><Brand /><div className="story-content"><span className="eyebrow">LE TERRAIN. LES ÉQUIPES. LE SUIVI.</span><h1>Chaque heure<br />compte.</h1><p>Connectez vos équipes et vos clients.<br />Du premier pointage au dernier règlement.</p><div className="story-line"><Clock3 size={20} /><span>Pointer</span><i /><ShieldCheck size={20} /><span>Valider</span><i /><FileText size={20} /><span>Facturer</span></div></div><footer>Votre activité industrielle, en toute clarté.</footer></section>
    <section className="login-panel">
      {(technicianOnly || projectOnly) && <div className="tech-login-brand"><img className="tech-login-logo" src={headerLogo} alt="Copetro Elite" /><small>{projectOnly ? 'ESPACE CLIENT · PROJET' : 'ESPACE TECHNICIEN'}</small></div>}
      <div className="login-box">
        <span className="eyebrow green">{technicianOnly ? 'ACCÈS SÉCURISÉ' : 'VOTRE ESPACE DE TRAVAIL'}</span>
        <h2>{projectOnly ? 'Validation des pointages' : technicianOnly ? 'Bonjour.' : 'Bon retour.'}</h2>
        <p className="muted">{projectOnly ? 'Connectez-vous avec les identifiants de votre projet pour valider les heures des techniciens.' : technicianOnly ? 'Connectez-vous pour consulter vos projets et saisir vos heures.' : 'Connectez-vous pour retrouver vos projets.'}</p>
        {initialError && <div className="alert error" role="alert">{initialError}<button className="text-button" onClick={retry}>Réessayer</button></div>}
        <form onSubmit={submit}>
          <Field label="Identifiant"><input autoComplete="username" autoCapitalize="none" required value={username} onChange={e => setUsername(e.target.value)} placeholder="Votre identifiant" /></Field>
          <Field label="Mot de passe"><input type="password" autoComplete="current-password" required value={password} onChange={e => setPassword(e.target.value)} placeholder="Votre mot de passe" /></Field>
          {error && <p className="alert error" role="alert">{error}</p>}
          <button className="button login-submit" disabled={busy}>{busy ? <Spinner /> : <>Se connecter <ArrowRight size={18} /></>}</button>
        </form>
        <p className="login-help">{projectOnly ? 'Un identifiant et un mot de passe propres à chaque projet.' : technicianOnly ? 'Accès réservé aux techniciens autorisés.' : 'Besoin d’un accès ? Contactez votre administrateur.'}</p>
      </div>
    </section>
  </main>;
}

export default function App() {
  const [user, setUser] = useState(null), [booting, setBooting] = useState(true), [sessionError, setSessionError] = useState('');
  const [page, setPage] = useState(() => {
    if (projectLogin) return 'entries';
    const storedPage = sessionStorage.getItem(PAGE_STORAGE_KEY);
    return NAV.some(item => item.id === storedPage) || FINANCE_NAV.some(item => item.id === storedPage) ? storedPage : 'dashboard';
  }), [data, setData] = useState(emptyData), [loading, setLoading] = useState(false), [lastRefreshAt, setLastRefreshAt] = useState(null);
  const [error, setError] = useState(''), [notice, setNotice] = useState(''), [query, setQuery] = useState(''), [filter, setFilter] = useState('ALL'), [specialtyFilter, setSpecialtyFilter] = useState('ALL'), [projectFilter, setProjectFilter] = useState('ALL'), [technicianFilter, setTechnicianFilter] = useState('ALL'), [trashTab, setTrashTab] = useState('projects'), [settingsOpen, setSettingsOpen] = useState(false), [financeOpen, setFinanceOpen] = useState(false);
  const [modal, setModal] = useState(null), [report, setReport] = useState(null), [globalReport, setGlobalReport] = useState(null), [working, setWorking] = useState(false), [deleteClientError, setDeleteClientError] = useState('');
  const bootstrap = useCallback(async () => {
    setBooting(true); setSessionError('');
    try {
      const session = await api('auth/session/');
      if (technicianLogin && session.user && session.user.role !== 'TECHNICIAN') {
        await api('auth/logout/', { method: 'POST', body: {} });
        setSessionError('Cet accès est réservé aux comptes techniciens.');
        setUser(null);
      } else if (projectLogin && session.user && (session.user.role !== 'PROJECT_MANAGER' || !session.user.project_access)) {
        await api('auth/logout/', { method: 'POST', body: {} });
        setSessionError('Cet accès est réservé aux comptes clients des projets.');
        setUser(null);
      } else setUser(session.user);
    }
    catch (err) { setSessionError(err.message); } finally { setBooting(false); }
  }, []);
  useEffect(() => { bootstrap(); }, [bootstrap]);
  useEffect(() => {
    if (!user) return;
    const currentPage = NAV.find(item => item.id === page);
    if ((['invoices', 'technician-payments', 'specialties', 'trash'].includes(page) && user.role !== 'ADMIN') || (page === 'payments' && !['ADMIN', 'TECHNICIAN'].includes(user.role))) {
      setPage('dashboard');
      return;
    }
    if (currentPage?.roles && !currentPage.roles.includes(user.role)) {
      setPage('dashboard');
      return;
    }
    sessionStorage.setItem(PAGE_STORAGE_KEY, page);
  }, [page, user]);
  const refresh = useCallback(async () => {
    if (!user) return;
    setLoading(true); setError('');
    try {
      const [dashboard, projects, entries, users, clients, holidays, specialties, invoices, payments, technicianPayments] = await Promise.all([
        api('dashboard/'), listAll('projects/'), listAll('time-entries/'), listAll('users/'),
        ['ADMIN', 'SUPERVISOR'].includes(user.role) ? listAll('clients/') : Promise.resolve([]),
        user.role === 'ADMIN' ? listAll('holidays/') : Promise.resolve([]),
        user.role === 'ADMIN' ? listAll('technician-specialties/') : Promise.resolve([]),
        user.role === 'ADMIN' ? listAll('invoices/') : Promise.resolve([]), user.role === 'ADMIN' ? listAll('payments/') : user.role === 'TECHNICIAN' ? listAll('projects/earnings/') : Promise.resolve([]), user.role === 'ADMIN' ? listAll('technician-payments/') : Promise.resolve([]),
      ]);
      const trash = user.role === 'ADMIN' ? Object.fromEntries(await Promise.all(['projects', 'technicians', 'clients'].map(async type => [type, await listAll(`trash/?type=${type}`)]))) : emptyData.trash;
      setData({ dashboard, projects, entries, users, clients, holidays, specialties, invoices, payments, technicianPayments, trash });
      setLastRefreshAt(new Date());
    } catch (err) { setError(err.message); } finally { setLoading(false); }
  }, [user]);
  useEffect(() => { refresh(); }, [refresh]);
  useEffect(() => {
    if (!user || page !== 'entries') return undefined;
    const timer = window.setInterval(refresh, 120000);
    return () => window.clearInterval(timer);
  }, [page, refresh, user]);
  useEffect(() => { if (!notice) return; const timer = setTimeout(() => setNotice(''), 5000); return () => clearTimeout(timer); }, [notice]);
  function navigate(id) { setPage(id); setQuery(''); setFilter('ALL'); setSpecialtyFilter('ALL'); setProjectFilter('ALL'); setTechnicianFilter('ALL'); setTrashTab('projects'); setSettingsOpen(false); setFinanceOpen(false); }
  async function restoreTrash(kind, id) {
    setWorking(true); setError('');
    try { await api(`trash/${id}/restore/?type=${kind}`, { method: 'POST', body: {} }); setNotice('Élément restauré.'); await refresh(); }
    catch (err) { setError(err.message); } finally { setWorking(false); }
  }
  async function save(path, method, body) {
    const result = await api(path, { method, body });
    if (path.startsWith('users/') && body instanceof FormData
      && body.has('cv') && !result.cv_url) {
      throw new Error('Le serveur n’a pas confirmé l’enregistrement du CV. Le fichier reste sélectionné ; réessayez.');
    }
    setModal(null); setNotice('Enregistrement effectué.'); await refresh();
    return result;
  }
  async function deleteTechnician(technician) {
    await api(`users/${technician.id}/`, { method: 'DELETE' });
    setData(current => ({ ...current, users: current.users.filter(person => person.id !== technician.id) }));
    setModal(null); setNotice('Technicien supprimé.');
    await refresh();
  }
  async function deleteHoliday(holiday) {
    if (!window.confirm(`Supprimer le jour férié « ${holiday.name} » ?`)) return;
    setWorking(true); setError('');
    try { await api(`holidays/${holiday.id}/`, { method: 'DELETE' }); setNotice('Jour férié supprimé.'); await refresh(); }
    catch (err) { setError(err.message); } finally { setWorking(false); }
  }
  async function deleteProject(project) {
    if (!window.confirm(`Supprimer le projet « ${project.name} » ?`)) return;
    setWorking(true); setError('');
    try { await api(`projects/${project.id}/`, { method: 'DELETE' }); setNotice('Projet supprimé.'); await refresh(); }
    catch (err) { setError(err.message); } finally { setWorking(false); }
  }
  async function act(entry, action) {
    setWorking(true); setError('');
    try { await api(`time-entries/${entry.id}/${action}/`, { method: 'POST', body: {} }); setNotice(action === 'submit' ? 'Pointage transmis au chef de projet.' : 'Pointage validé.'); await refresh(); }
    catch (err) { setError(err.message); } finally { setWorking(false); }
  }
  async function signOut() {
    try { await api('auth/logout/', { method: 'POST', body: {} }); sessionStorage.removeItem(PAGE_STORAGE_KEY); setUser(null); setData(emptyData); setModal(null); setPage('dashboard'); setNotice(''); }
    catch (err) { setError(err.message); }
  }
  const internal = user && ['ADMIN', 'SUPERVISOR'].includes(user.role);
  const isAdmin = user?.role === 'ADMIN';
  const isTechnician = user?.role === 'TECHNICIAN';
  const nav = NAV.filter(item => (!item.roles || item.roles.includes(user?.role))
    && !['invoices', 'payments', 'technician-payments'].includes(item.id)
    && !(user?.role === 'ADMIN' && ['users', 'holidays'].includes(item.id)));
  const financeItems = FINANCE_NAV.filter(item => item.roles.includes(user?.role));
  const search = rows => rows.filter(row => Object.values(row).some(value => typeof value === 'string' && value.toLocaleLowerCase().includes(query.toLocaleLowerCase())));
  const technicians = data.users.filter(person => person.role === 'TECHNICIAN');
  const visibleRows = search(page === 'technicians' ? technicians : page === 'technician-payments' ? data.technicianPayments : data[page] instanceof Array ? data[page] : []).filter(row => {
    if (page === 'entries' && projectFilter !== 'ALL' && String(row.project) !== String(projectFilter)) return false;
    if (page === 'entries' && technicianFilter !== 'ALL' && String(row.technician) !== String(technicianFilter)) return false;
    if (page === 'technicians' && specialtyFilter !== 'ALL' && row.specialty !== specialtyFilter) return false;
    if (filter === 'ALL') return true;
    if (page === 'technicians') return row.is_active === (filter === 'ACTIVE');
    return page !== 'entries' || row.status === filter;
  }).sort((a, b) => page === 'entries' ? new Date(a.start) - new Date(b.start) : 0);
  const numberedTechnicians = visibleRows.map((technician, index) => ({ ...technician, listNumber: index + 1 }));
  const edit = (type, row) => <button className="icon-button" title="Modifier" aria-label={`Modifier ${row.name || row.full_name || 'le pointage'}`} onClick={() => setModal({ type, row })}><Pencil size={16} /></button>;
  const add = (type, label, iconOnly = false) => <button className="button" aria-label={iconOnly ? label : undefined} title={iconOnly ? label : undefined} onClick={() => setModal({ type })}>{iconOnly && type === 'time' ? <Clock3 size={17} aria-hidden="true" /> : <Plus size={17} aria-hidden="true" />}{!iconOnly && label}</button>;
  const selectedProject = data.projects.find(project => String(project.id) === String(projectFilter));
  const technicianOptions = data.users.filter(person => person.role === 'TECHNICIAN' && person.is_active
    && (projectFilter === 'ALL' || selectedProject?.technicians.includes(person.id)));
  const reportRows = visibleRows;
  const openGlobalReport = compact => setGlobalReport({ rows: reportRows, compact });
  const projectById = new Map(data.projects.map(project => [project.id, project]));
  const entryAmounts = entry => {
    const project = projectById.get(entry.project);
    const hours = Number(entry.hours || 0);
    const clientCost = hours * Number(project?.hourly_rate || 0);
    const technicianCost = hours * Number(project?.technician_hourly_rate || 0);
    return { clientCost, benefit: clientCost - technicianCost };
  };
  const entryColumns = [
    { label: 'Technicien / Projet', render: e => <div className="cell-stack"><strong>{e.technician_name}</strong><span>{e.project_name}</span></div> },
    { label: 'Intervention', render: e => <div className="cell-stack"><strong>{date(e.start)}</strong>{!isTechnician && <span>{time(e.start)} – {time(e.end)} · {e.break_minutes} min de pause</span>}</div> },
    { label: 'Heures', render: e => <b className="tabular">{number(e.hours)} h</b> },
    ...(!isTechnician ? [{ label: 'Statut', render: e => <Badge status={e.status} /> }] : []),
    ...(!isTechnician ? [{ label: 'Coût client', render: e => money(entryAmounts(e).clientCost, user.currency) }, { label: 'Bénéfice', render: e => money(entryAmounts(e).benefit, user.currency) }] : []),
    { label: 'Actions', render: e => <div className="row-actions"><button className="text-button" onClick={() => setModal({ type: 'entry-detail', row: e })}>Détail</button>{user?.role === 'ADMIN' && e.status === 'REJECTED' && <button className="icon-button" title="Saisir un nouveau pointage" aria-label={`Saisir un nouveau pointage pour ${e.technician_name}`} onClick={() => setModal({ type: 'admin-time', row: e })}><Plus size={16} /></button>}{user?.role === 'TECHNICIAN' && ['DRAFT', 'REJECTED'].includes(e.status) && <>{edit('time', e)}<button className="button compact" disabled={working} onClick={() => act(e, 'submit')}><Send size={14} />Soumettre</button></>}{user?.role === 'PROJECT_MANAGER' && e.status === 'SUBMITTED' && <><button className="button compact" disabled={working} onClick={() => act(e, 'approve')}><Check size={14} />Valider</button><button className="icon-button danger" aria-label="Refuser le pointage" disabled={working} onClick={() => setModal({ type: 'reject', row: e })}><X size={17} /></button></>}</div> },
  ];
  if (booting) return <div className="boot"><Spinner /><span>Ouverture de votre espace…</span></div>;
  if (!user) return <Login onLogin={account => { setUser(account); if (account.project_access) { setPage('entries'); setFilter('SUBMITTED'); } }} initialError={sessionError} retry={bootstrap} technicianOnly={technicianLogin} projectOnly={projectLogin} />;
  const primaryAction = page === 'technicians' && isAdmin ? add('technician', 'Ajouter un technicien') : page === 'projects' && internal ? add('project', 'Nouveau projet') : page === 'clients' && internal ? add('client', 'Nouveau client') : page === 'holidays' && isAdmin ? add('holiday', 'Ajouter un jour férié') : page === 'specialties' && isAdmin ? add('specialty', 'Ajouter une spécialité') : page === 'users' && isAdmin ? add('user', 'Ajouter un collaborateur') : page === 'entries' && user.role === 'TECHNICIAN' ? add('time', 'Saisir mes heures', true) : page === 'invoices' && isAdmin ? add('invoice', 'Créer une facture') : page === 'payments' && isAdmin ? add('payment', 'Enregistrer un paiement') : page === 'technician-payments' && isAdmin ? add('technician-payment', 'Enregistrer une charge') : page === 'dashboard' && user.role === 'TECHNICIAN' ? add('time', 'Saisir mes heures', true) : null;
  return <div className={`app-shell${isTechnician ? ' technician-shell' : ''}${isTechnician && modal ? ' technician-modal-open' : ''}`}>
    <header className="app-header">
      <div className="header-content">
        <div className="header-main">
          <div className="header-logo"><img src={headerLogo} alt="Copetrolite" width="419" height="296" /></div>
          <nav className="topnav" aria-label="Navigation principale">
            {nav.map(item => <Fragment key={item.id}>
              <button className={page === item.id ? 'topnav-link active' : 'topnav-link'} aria-current={page === item.id ? 'page' : undefined} onClick={() => navigate(item.id)}>
                <item.icon size={18} /><span>{item.label}</span>
                {item.id === 'entries' && !isTechnician && data.dashboard.pending_entries > 0 && <small>{data.dashboard.pending_entries}</small>}
              </button>
              {item.id === 'clients' && isAdmin && <div className="nav-dropdown"><button className={settingsOpen || ['holidays', 'users', 'specialties'].includes(page) ? 'topnav-link active' : 'topnav-link'} aria-expanded={settingsOpen} aria-controls="settings-subnav" onClick={() => { setSettingsOpen(open => !open); setFinanceOpen(false); }}>
                <Settings size={18} /><span>Paramètres</span><ChevronDown size={15} />
              </button>{settingsOpen && <nav className="settings-subnav" id="settings-subnav" aria-label="Paramètres">
                {[{ id: 'holidays', label: 'Calendrier', icon: CalendarDays }, { id: 'users', label: 'Équipe', icon: Users }, { id: 'specialties', label: 'Spécialités', icon: HardHat }, { id: 'trash', label: 'Corbeille', icon: Trash2 }].map(item =>
                  <button key={item.id} className={page === item.id ? 'settings-subnav-link active' : 'settings-subnav-link'} aria-current={page === item.id ? 'page' : undefined} onClick={() => navigate(item.id)}>
                    <item.icon size={17} /><span>{item.label}</span>
                  </button>
                )}
              </nav>}</div>}
              {item.id === 'clients' && financeItems.length > 0 && <div className="nav-dropdown"><button className={financeOpen || ['invoices', 'payments'].includes(page) ? 'topnav-link active' : 'topnav-link'} aria-expanded={financeOpen} aria-controls="finance-subnav" onClick={() => { setFinanceOpen(open => !open); setSettingsOpen(false); }}>
                <CreditCard size={18} /><span>Finances</span><ChevronDown size={15} />
              </button>{financeOpen && <nav className="settings-subnav finance-subnav" id="finance-subnav" aria-label="Finances">
                {financeItems.map(item => <button key={item.id} className={page === item.id ? 'settings-subnav-link active' : 'settings-subnav-link'} aria-current={page === item.id ? 'page' : undefined} onClick={() => navigate(item.id)}>
                  <item.icon size={17} /><span>{item.label}</span>
                </button>)}
              </nav>}</div>}
            </Fragment>)}
          </nav>
          <div className="header-profile">
            <span className="avatar">{user.full_name.slice(0, 2).toUpperCase()}</span>
            <div className="header-user"><strong>{user.full_name}</strong><small>{roleLabels[user.role]}</small><small className="header-date">{new Date().toLocaleDateString('fr-FR', { day: 'numeric', month: 'long' })}</small></div>
            <button className="icon-button" onClick={signOut} aria-label="Se déconnecter" title="Se déconnecter"><LogOut size={18} /></button>
          </div>
        </div>
      </div>
    </header>
    {report && <TechnicianReport technician={report.technician} rows={report.rows} projects={data.projects} close={() => setReport(null)} />}
    {globalReport && <GlobalReport rows={globalReport.rows} projects={data.projects} compact={globalReport.compact} close={() => setGlobalReport(null)} />}
    <div className="workspace">
      <main className="main"><div className={`page-heading${isTechnician && page === 'dashboard' ? ' technician-dashboard-heading' : isTechnician && page === 'entries' ? ' technician-entries-heading' : ''}`}><div>{!isTechnician && <span className="eyebrow green">{'COPETROLITE / ' + (page === 'dashboard' ? 'TABLEAU DE BORD' : 'GESTION')}</span>}<h1>{isTechnician && page === 'dashboard' ? `Bonjour, ${user.full_name.split(' ')[0]}` : page === 'specialties' ? 'Spécialités techniciens' : page === 'trash' ? 'Corbeille' : NAV.find(n => n.id === page)?.label}</h1>{!(isTechnician && page === 'entries') && <p>{isTechnician && page === 'dashboard' ? 'Prêt pour votre prochaine intervention ?' : isTechnician && page === 'payments' ? 'Retrouvez vos gains par projet.' : descriptions[page]}</p>}</div>{primaryAction}</div>
        {notice && <div className="alert success" role="status"><CheckCheck size={18} />{notice}</div>}
        {error && <div className="alert error" role="alert">{error}<button className="text-button" onClick={refresh}>Réessayer</button></div>}
        {loading && <div className="loading-bar" role="status"><Spinner /> Actualisation des données…</div>}
        {page === 'dashboard' ? <>
          <div className="metrics"><Metric icon={Clock3} label="Heures pointées" value={`${number(data.dashboard.total_hours)} h`} note="Total des interventions" /><Metric icon={ShieldCheck} label="Pointages à valider" value={data.dashboard.pending_entries || 0} note="En attente du chef de projet" amber /><Metric icon={BriefcaseBusiness} label="Projets en cours" value={data.dashboard.active_projects || 0} note="Interventions actives" /><Metric icon={isAdmin ? CreditCard : CheckCheck} label={isAdmin ? 'Reste à encaisser' : 'Heures validées'} value={isAdmin ? money(data.dashboard.outstanding, user.currency) : `${number(data.dashboard.approved_hours)} h`} note={isAdmin ? 'Solde des factures émises' : 'Prêtes pour la facturation'} /></div>
          <div className="dashboard-grid"><section className="panel"><div className="panel-heading"><div><h2>{isTechnician ? 'Mes projets en cours' : 'Les projets en cours'}</h2><p>Vos interventions actives</p></div><button className="text-button" onClick={() => navigate('projects')}>Tous les projets <ArrowUpRight size={16} /></button></div>{data.projects.filter(p => p.status === 'ACTIVE').length ? <div className="project-list">{data.projects.filter(p => p.status === 'ACTIVE').slice(0, 4).map(p => <button key={p.id} className="project-row" onClick={() => navigate('projects')}><span className="project-symbol"><BriefcaseBusiness size={20} /></span><span><strong>{p.name}</strong><small>{p.client_name} · {p.site}</small></span><Badge status={p.status} /><ChevronRight size={16} /></button>)}</div> : <Empty title={isTechnician ? 'Aucun projet actif' : 'Votre premier projet commence ici'} text={isTechnician ? 'Vos affectations actives apparaîtront ici.' : 'Créez un client, son chef de projet, puis affectez vos techniciens.'} action={internal && add('project', 'Créer un projet')} />}</section>{!isTechnician && <section className="workflow-card"><span className="eyebrow">UN SUIVI SANS RUPTURE</span><h2>Du terrain<br />à la facturation.</h2><p>Chaque intervention suit un parcours clair et partagé.</p><ol><li><span>01</span>Le technicien saisit ses heures</li><li><span>02</span>Le chef de projet client valide</li><li><span>03</span>L’administrateur facture</li></ol><button onClick={() => navigate('entries')}>Consulter les pointages <ArrowRight size={18} /></button></section>}</div>
          <section className="panel"><div className="panel-heading"><div><h2>{isTechnician ? 'Mes derniers pointages' : 'Derniers pointages'}</h2><p>Les interventions les plus récentes</p></div><button className="text-button" onClick={() => navigate('entries')}>Tout consulter <ArrowUpRight size={16} /></button></div>{isTechnician && <div className="tech-entry-cards dashboard-entry-cards">{data.entries.slice(0, 4).map(entry => <TechnicianEntryCard key={entry.id} entry={entry} hideStatus={isTechnician} onDetail={() => setModal({ type: 'entry-detail', row: entry })} />)}{!data.entries.length && <Empty title="Aucun pointage" text="Vos interventions récentes apparaîtront ici." />}</div>}<div className={isTechnician ? 'technician-desktop-table' : ''}><Table columns={entryColumns} rows={data.entries.slice(0, 5)} empty={<Empty title="Aucun pointage pour le moment" text="Les heures saisies par les techniciens apparaîtront ici." />} /></div></section>
        </> : <section className="panel"><div className="list-toolbar"><label className="search"><Search size={18} /><input aria-label="Rechercher dans la liste" placeholder="Rechercher…" value={query} onChange={e => setQuery(e.target.value)} /></label>{page === 'entries' && !isTechnician && <select aria-label="Filtrer les pointages" value={filter} onChange={e => setFilter(e.target.value)}><option value="ALL">Tous les statuts</option>{['DRAFT', 'SUBMITTED', 'APPROVED', 'REJECTED', 'INVOICED'].map(s => <option value={s} key={s}>{statusLabels[s]}</option>)}</select>}{page === 'technicians' && <select aria-label="Filtrer les techniciens" value={filter} onChange={e => setFilter(e.target.value)}><option value="ALL">Tous les techniciens</option><option value="ACTIVE">Actifs</option><option value="INACTIVE">Désactivés</option></select>}<span className="muted small">{visibleRows.length} résultat(s)</span></div>
          {page === 'entries' && <div className="project-filter-bar"><label htmlFor="entries-project-filter">Filtrer par projet</label><select id="entries-project-filter" value={projectFilter} onChange={e => { setProjectFilter(e.target.value); setTechnicianFilter('ALL'); }}><option value="ALL">Tous les projets</option>{data.projects.map(project => <option value={project.id} key={project.id}>{project.name}</option>)}</select><label htmlFor="entries-technician-filter">Filtrer par technicien</label><select id="entries-technician-filter" value={technicianFilter} onChange={e => setTechnicianFilter(e.target.value)}><option value="ALL">Tous les techniciens</option>{technicianOptions.map(technician => <option value={technician.id} key={technician.id}>{technician.full_name}</option>)}</select><span className="last-refresh">Dernière actualisation : {lastRefreshAt ? lastRefreshAt.toLocaleString('fr-FR', { dateStyle: 'short', timeStyle: 'short' }) : '—'}</span><button className="icon-button" title="Actualiser les pointages" aria-label="Actualiser les pointages" disabled={loading} onClick={refresh}><RefreshCw size={16} className={loading ? 'spin' : ''} /></button>{isAdmin && <div className="report-filter-actions"><button className="icon-button" title="Générer le PDF détaillé" aria-label="Générer le PDF détaillé" onClick={() => openGlobalReport(false)}><Download size={16} /></button><button className="icon-button" title="Générer le PDF résumé" aria-label="Générer le PDF résumé" onClick={() => openGlobalReport(true)}><FileText size={16} /></button></div>}</div>}
          {page === 'entries' && <>
            {isTechnician && <div className="tech-entry-cards">{visibleRows.map(entry => <TechnicianEntryCard key={entry.id} entry={entry} hideStatus={isTechnician} onDetail={() => setModal({ type: 'entry-detail', row: entry })} onEdit={['DRAFT', 'REJECTED'].includes(entry.status) ? () => setModal({ type: 'time', row: entry }) : undefined} onSubmit={['DRAFT', 'REJECTED'].includes(entry.status) ? () => act(entry, 'submit') : undefined} working={working} />)}{!visibleRows.length && <Empty title="Aucun pointage" text="Saisissez vos heures pour commencer à suivre vos interventions." action={add('time', 'Saisir mes heures')} />}</div>}
            <div className={isTechnician ? 'technician-desktop-table' : ''}><Table columns={entryColumns} rows={visibleRows} /></div>
          </>}
          {page === 'holidays' && <Table rows={visibleRows} empty={<Empty title="Aucun jour férié" text="Ajoutez les dates fériées pour les utiliser dans le calcul des coûts techniciens." />} columns={[
            { label: 'Date', render: holiday => date(holiday.date) },
            { label: 'Jour férié', render: holiday => holiday.name },
            { label: 'Actions', render: holiday => <div className="row-actions">{edit('holiday', holiday)}<button className="icon-button danger" title="Supprimer" aria-label={`Supprimer ${holiday.name}`} disabled={working} onClick={() => deleteHoliday(holiday)}><Trash2 size={16} /></button></div> },
          ]} />}
          {page === 'technicians' && isAdmin && <div className="specialty-filter-inline"><label htmlFor="technician-specialty-filter">Spécialité</label><select id="technician-specialty-filter" aria-label="Filtrer par spécialité" value={specialtyFilter} onChange={e => setSpecialtyFilter(e.target.value)}><option value="ALL">Toutes les spécialités</option>{data.specialties.map(specialty => <option value={specialty.name} key={specialty.id}>{specialty.name}</option>)}</select></div>}
          {page === 'technicians' && <Table rows={numberedTechnicians} empty={<Empty
            title={technicians.length ? 'Aucun technicien trouvé' : 'Aucun technicien pour le moment'}
            text={technicians.length ? 'Modifiez votre recherche ou le filtre de statut.' : isAdmin ? 'Ajoutez un technicien pour préparer ses affectations et ses pointages.' : 'Les techniciens accessibles dans vos projets apparaîtront ici.'}
            action={!technicians.length && isAdmin && add('technician', 'Ajouter un technicien')}
          />} columns={[
            { label: 'Technicien', render: t => <div className="person-cell"><span className="technician-row-number">{t.listNumber}</span>{t.photo_url ? <img className="avatar light technician-list-photo" src={t.photo_url} alt="" /> : <span className="avatar light">{t.full_name.slice(0, 2).toUpperCase()}</span>}<div className="cell-stack"><strong>{t.full_name}</strong>{t.employee_number && <span className="technician-matricule">{t.employee_number}</span>}</div></div> },
            { label: 'Spécialité', render: t => t.specialty || '—' },
            ...(internal ? [{ label: 'Coordonnées', render: t => <div className="cell-stack"><span>{t.email || '—'}</span><span>{t.phone || '—'}</span></div> }] : []),
            { label: 'Projets en cours', render: t => {
              const assigned = data.projects.filter(p => p.status === 'ACTIVE' && p.technicians.includes(t.id));
              return <div className="cell-stack"><strong>{assigned.length} projet(s)</strong><span>{assigned.map(p => p.name).join(', ') || 'Aucune affectation'}</span></div>;
            } },
            { label: 'Compte', render: t => <span className={`badge ${t.is_active ? 'status-active' : 'status-completed'}`}>{t.is_active ? 'Actif' : 'Désactivé'}</span> },
            { label: 'Actions', render: t => <div className="row-actions">
              <button className="icon-button" title="Voir le profil complet" aria-label={`Voir le profil complet de ${t.full_name}`} onClick={() => setModal({ type: 'technician-profile', row: t })}><Eye size={17} /></button>
              {isAdmin && <>{edit('technician', t)}<button className="icon-button danger" title="Supprimer" aria-label={`Supprimer ${t.full_name}`} onClick={() => setModal({ type: 'delete-technician', row: t })}><Trash2 size={16} /></button></>}
            </div> },
          ]} />}
          {page === 'projects' && <>{isTechnician && <div className="tech-project-cards">{search(data.projects).map(project => <article className="tech-project-card" key={project.id}><div className="tech-project-icon"><BriefcaseBusiness size={20} /></div><div className="tech-project-main"><div className="tech-project-title"><h2>{project.name}</h2><Badge status={project.status} /></div><p>{project.client_name}</p><div className="tech-project-meta"><span><Building2 size={15} />{project.site}</span>{project.manager_name && <span><Users size={15} />{project.manager_name}</span>}</div></div></article>)}{!search(data.projects).length && <Empty title="Aucun projet affecté" text="Vos projets s’afficheront ici dès qu’ils vous seront attribués." />}</div>}<div className={isTechnician ? 'technician-desktop-table' : ''}><Table rows={search(data.projects)} columns={[
            { label: 'Projet / Site', render: p => <div className="cell-stack"><strong>{p.name}</strong><span>{p.site}</span></div> }, { label: 'Client', render: p => p.client_name }, { label: 'Chef de projet', render: p => p.manager_name }, { label: 'Équipe', render: p => <div className="cell-stack"><strong>{p.technicians.length} technicien(s)</strong><span>{p.technician_names.join(', ') || 'À affecter'}</span></div> }, { label: 'Statut', render: p => <Badge status={p.status} /> }, ...(internal ? [{ label: 'Tarif / h', render: p => money(p.hourly_rate, user.currency) }, { label: 'Coût techniciens', render: p => money(p.technician_labor_cost, user.currency) }, { label: 'Actions', render: p => <div className="row-actions">{edit('project', p)}{isAdmin && <><button className="text-button" onClick={() => setModal({ type: 'project-access', row: p })}>Accès client</button><button className="icon-button danger" title="Supprimer" aria-label={`Supprimer le projet ${p.name}`} disabled={working} onClick={() => deleteProject(p)}><Trash2 size={16} /></button></>}</div> }] : []),
          ]} /></div></>}
          {page === 'users' && <Table rows={search(data.users)} columns={[
            { label: 'Collaborateur', render: u => <div className="person-cell"><span className="avatar light">{u.full_name.slice(0, 2).toUpperCase()}</span><div className="cell-stack"><strong>{u.full_name}</strong><span>{u.email || u.specialty || '—'}</span></div></div> }, { label: 'Rôle', render: u => roleLabels[u.role] }, { label: 'Client / Spécialité', render: u => u.client_name || u.specialty || '—' }, { label: 'Compte', render: u => <span className={`badge ${u.is_active ? 'status-active' : 'status-completed'}`}>{u.is_active ? 'Actif' : 'Désactivé'}</span> }, ...(isAdmin ? [{ label: 'Actions', render: u => edit('user', u) }] : []),
          ]} />}
          {page === 'clients' && <Table rows={search(data.clients)} columns={[
            { label: 'Entreprise', render: c => <div className="person-cell">{c.logo_url ? <img className="client-list-logo" src={c.logo_url} alt="" /> : <span className="project-symbol"><Building2 size={18} /></span>}<div className="cell-stack"><strong>{c.name}</strong><span>{[['RC', c.rc], ['NIF', c.nif], ['N° article', c.article_number], ['NIS', c.nis]].filter(([, value]) => value).map(([label, value]) => `${label} : ${value}`).join(' · ') || '—'}</span></div></div> }, { label: 'Contact', render: c => c.contact_name || '—' }, { label: 'Coordonnées', render: c => <div className="cell-stack"><span>{c.email || '—'}</span><span>{c.phone || '—'}</span><span>{c.billing_address || '—'}</span></div> }, { label: 'Statut', render: c => <span className={`badge ${c.is_active ? 'status-active' : 'status-completed'}`}>{c.is_active ? 'Actif' : 'Désactivé'}</span> }, { label: 'Actions', render: c => <div className="row-actions">
              <button className="icon-button" title="Voir le client" aria-label={`Voir le client ${c.name}`} onClick={() => setModal({ type: 'client-detail', row: c })}><Eye size={17} /></button>
              {edit('client', c)}
              {isAdmin && <button className="icon-button danger" title="Supprimer" aria-label={`Supprimer le client ${c.name}`} onClick={() => { setDeleteClientError(''); setModal({ type: 'delete-client', row: c }); }}><Trash2 size={16} /></button>}
            </div> },
          ]} />}
          {page === 'specialties' && <Table rows={data.specialties} empty={<Empty title="Aucune spécialité" text="Ajoutez une spécialité, puis affectez vos techniciens depuis cette page." action={add('specialty', 'Ajouter une spécialité')} />} columns={[{ label: 'Spécialité', render: specialty => <strong>{specialty.name}</strong> }, { label: 'Techniciens affectés', render: specialty => { const assigned = data.users.filter(technician => technician.role === 'TECHNICIAN' && technician.specialty === specialty.name); return <div className="cell-stack"><strong>{assigned.length} technicien(s)</strong><span>{assigned.map(technician => technician.full_name).join(', ') || 'Aucun technicien affecté'}</span></div>; } }, { label: 'Actions', render: specialty => <button className="icon-button" title={`Modifier ${specialty.name}`} aria-label={`Modifier ${specialty.name}`} onClick={() => setModal({ type: 'specialty', row: specialty })}><Pencil size={16} /></button> }]} />}
          {page === 'trash' && <><div className="trash-tabs" role="tablist" aria-label="Éléments supprimés">{[{ id: 'projects', label: 'Projets' }, { id: 'technicians', label: 'Techniciens' }, { id: 'clients', label: 'Clients' }].map(tab => <button key={tab.id} className={trashTab === tab.id ? 'trash-tab active' : 'trash-tab'} role="tab" aria-selected={trashTab === tab.id} onClick={() => setTrashTab(tab.id)}>{tab.label} ({data.trash[tab.id].length})</button>)}</div><Table rows={data.trash[trashTab]} empty={<Empty title="Corbeille vide" text="Aucun élément supprimé dans cette catégorie." />} columns={[{ label: 'Élément', render: item => <strong>{item.name}</strong> }, { label: 'Supprimé le', render: item => date(item.deleted_at) }, { label: 'Actions', render: item => <button className="button compact" disabled={working} onClick={() => restoreTrash(trashTab, item.id)}>Restaurer</button> }]} /></>}
          {page === 'invoices' && <Table rows={search(data.invoices)} columns={[
            { label: 'Facture', render: i => <div className="cell-stack"><strong>{i.number}</strong><span>{i.project_name}</span></div> }, { label: 'Client', render: i => i.client_name }, { label: 'Échéance', render: i => date(i.due_date) }, { label: 'Total TTC', render: i => <strong>{money(i.total, i.currency)}</strong> }, { label: 'Solde', render: i => money(i.balance, i.currency) }, { label: 'Statut', render: i => <Badge status={i.status} /> }, { label: 'Actions', render: i => <div className="row-actions"><button className="text-button" onClick={() => setModal({ type: 'invoice-detail', row: i })}>Consulter</button>{Number(i.balance) > 0 && <button className="icon-button" title="Enregistrer un paiement" aria-label="Enregistrer un paiement" onClick={() => setModal({ type: 'payment', invoice: i })}><ArrowDownLeft size={18} /></button>}</div> },
          ]} />}
          {page === 'payments' && isTechnician && <div className="technician-earnings">
            {visibleRows.map(project => <article className="tech-entry-card" key={project.id}>
              <div className="tech-project-title"><h2>{project.name}</h2><Badge status={project.status} /></div>
              <p className="muted small">{project.client_name} · {project.site}</p>
              <dl className="earnings-details">
                <div><dt>Heures validées</dt><dd>{number(project.hours)} h</dd></div>
                <div><dt>Tarif horaire</dt><dd>{money(project.hourly_rate, project.currency)}</dd></div>
                <div><dt>Journée fériée</dt><dd>{money(project.holiday_day_rate, project.currency)}</dd></div>
              </dl>
              <div className="tech-entry-card-bottom"><span>Montant calculé</span><strong className="green">{money(project.amount, project.currency)}</strong></div>
            </article>)}
            {!visibleRows.length && <Empty title={query ? 'Aucun projet trouvé' : 'Aucun projet affecté'} text={query ? 'Essayez une autre recherche.' : 'Vos gains par projet apparaîtront ici dès votre affectation.'} />}
          </div>}
          {page === 'payments' && isAdmin && <Table rows={search(data.payments)} columns={[
            { label: 'Date', render: p => date(p.date) }, { label: 'Facture', render: p => data.invoices.find(i => i.id === p.invoice)?.number || '—' }, { label: 'Montant reçu', render: p => <strong className="green">{money(p.amount, user.currency)}</strong> }, { label: 'Mode', render: p => ({ TRANSFER: 'Virement', CASH: 'Espèces', CHECK: 'Chèque' })[p.method] }, { label: 'Référence', render: p => p.reference || '—' }, { label: 'État', render: p => { const invoice = data.invoices.find(i => i.id === p.invoice); const total = Number(invoice?.total || 0); const balance = Number(invoice?.balance || 0); const paid = total - balance; const percentage = total ? Math.min(100, Math.round((paid / total) * 100)) : 0; return balance <= 0 ? <span className="badge status-paid">Payé</span> : <div className="cell-stack"><span>{percentage} % payé</span><strong className="muted">Reste : {money(balance, user.currency)}</strong></div>; } },
          ]} />}
          {page === 'technician-payments' && isAdmin && <Table rows={search(data.technicianPayments)} columns={[
            { label: 'Date', render: p => date(p.date) }, { label: 'Technicien', render: p => p.technician_name }, { label: 'Montant versé', render: p => <strong className="green">{money(p.amount, user.currency)}</strong> }, { label: 'Mode', render: p => p.method_label || ({ TRANSFER: 'Virement', CASH: 'Espèces', CHECK: 'Chèque' })[p.method] }, { label: 'Référence', render: p => p.reference || '—' }, { label: 'Note', render: p => p.note || '—' },
          ]} />}
        </section>}
        <footer className="main-footer"><span>Copetrolite · Gestion des interventions industrielles</span><span>Votre espace, votre équipe.</span></footer>
      </main>
    </div>
    {isTechnician && <nav className="technician-bottom-nav" aria-label="Navigation technicien">
      {NAV.filter(item => ['dashboard', 'projects', 'entries', 'payments'].includes(item.id)).map(item => <button key={item.id} className={page === item.id ? 'technician-tab active' : 'technician-tab'} aria-current={page === item.id ? 'page' : undefined} onClick={() => navigate(item.id)}>
        <item.icon size={21} /><span>{item.id === 'dashboard' ? 'Accueil' : item.id === 'entries' ? 'Pointages' : item.label}</span>
      </button>)}
    </nav>}
    {modal?.type === 'project-access' ? <ProjectAccess project={modal.row} save={save} onClose={() => setModal(null)} /> : modal?.type === 'delete-technician' ? <DeleteTechnician technician={modal.row} onDelete={deleteTechnician} onClose={() => setModal(null)} /> : modal?.type === 'client-detail' ? <Modal title="Détail du Client" titleIcon={<Building2 size={20} aria-hidden="true" />} onClose={() => setModal(null)}><div className="detail client-detail">
      <div className={`client-detail-heading${modal.row.logo_url ? ' has-logo' : ''}`}>
        {modal.row.logo_url && <img className="client-detail-logo" src={modal.row.logo_url} alt={`Logo de ${modal.row.name}`} />}
        <h2>{modal.row.name}</h2>
      </div>
      <dl className="client-detail-fields">{[['Société', modal.row.name], ['Personne à contacter', modal.row.contact_name], ['Email', modal.row.email], ['Téléphone', modal.row.phone], ['N° RC', modal.row.rc], ['NIF', modal.row.nif], ['N° article', modal.row.article_number], ['NIS', modal.row.nis], ['Adresse', modal.row.billing_address], ['Date de début de travail', date(modal.row.start_work_date)], ['Statut', modal.row.is_active ? 'Actif' : 'Désactivé']].map(([label, value]) => <div key={label}><dt>{label}</dt><dd>{value || '—'}</dd></div>)}</dl>
    </div></Modal> : modal?.type === 'delete-client' ? <Modal title="Supprimer le Client" titleIcon={<Building2 size={20} aria-hidden="true" />} onClose={() => setModal(null)}><div className="detail"><p>Voulez-vous déplacer le client <strong>{modal.row.name}</strong> vers la corbeille ? Il pourra être restauré depuis Paramètres → Corbeille.</p>{deleteClientError && <div className="alert error" role="alert">{deleteClientError}</div>}<footer className="form-footer"><button className="button secondary" onClick={() => setModal(null)} disabled={working}>Annuler</button><button className="button" onClick={async () => {
      setWorking(true); setDeleteClientError('');
      try { await api(`clients/${modal.row.id}/`, { method: 'DELETE' }); setData(current => ({ ...current, clients: current.clients.filter(client => client.id !== modal.row.id) })); setModal(null); setNotice('Client supprimé.'); await refresh(); }
      catch (err) { setDeleteClientError(err.message); }
      finally { setWorking(false); }
    }} disabled={working}>{working ? <Spinner /> : <Trash2 size={16} />}Supprimer</button></footer></div></Modal> : modal?.type === 'technician-profile' ? <TechnicianProfile technician={modal.row} projects={data.projects} onClose={() => setModal(null)} /> : modal?.type === 'entry-detail' ? <Modal title="Détail du pointage" onClose={() => setModal(null)}><div className="detail">{!isTechnician && <Badge status={modal.row.status} />}<h3>{modal.row.technician_name} · {modal.row.project_name}</h3><p>{date(modal.row.start)} · {isTechnician ? `${number(modal.row.hours)} h` : `${time(modal.row.start)} – ${time(modal.row.end)} · ${number(modal.row.hours)} h`}</p>{modal.row.description?.trim() && modal.row.description.trim().toLowerCase() !== 'h' && <p className="prewrap">{modal.row.description}</p>}{modal.row.rejection_reason && <div className="alert error">{modal.row.rejection_reason}</div>}<h3>Historique</h3><ol className="timeline">{modal.row.events.map(e => <li key={e.id}><strong>{statusLabels[e.status]}</strong><span>{e.actor_name} · {date(e.created_at)} à {time(e.created_at)}</span>{e.comment && <p>{e.comment}</p>}</li>)}</ol></div></Modal> : modal?.type === 'invoice-detail' ? <InvoiceDetail invoice={modal.row} close={() => setModal(null)} /> : modal && <Editor key={`${modal.type}-${modal.row?.id || 'new'}`} modal={modal} data={data} user={user} save={save} close={() => setModal(null)} />}
  </div>;
}

function Metric({ icon: Icon, label, value, note, amber }) {
  return <article className="metric"><div><span>{label}</span><span className={`metric-icon ${amber ? 'amber' : ''}`}><Icon size={19} /></span></div><strong>{value}</strong><small>{note}</small></article>;
}

function TechnicianEntryCard({ entry, onDetail, onEdit, onSubmit, working = false, hideStatus = false }) {
  return <article className="tech-entry-card">
    <div className="tech-entry-card-top">
      <div className="tech-entry-card-info">
        <span className="tech-entry-date">{date(entry.start)}</span><span className="tech-entry-time">Pointage journalier</span>
        {!hideStatus && <Badge status={entry.status} />}
        <div className="tech-entry-project"><BriefcaseBusiness size={17} /><strong>{entry.project_name}</strong></div>
      </div>
      <div className="tech-entry-card-summary">
        <span className="tech-entry-hours">{number(entry.hours)} h</span>
        <button className="text-button" onClick={onDetail}>Détail <ChevronRight size={15} /></button>
      </div>
    </div>
    {(onEdit || onSubmit) && <div className="tech-entry-card-bottom">
      <div className="tech-entry-actions">
        {onEdit && <button className="icon-button" onClick={onEdit} aria-label="Modifier le pointage"><Pencil size={16} /></button>}
        {onSubmit && <button className="button compact" onClick={onSubmit} disabled={working}><Send size={14} />Soumettre</button>}
      </div>
    </div>}
  </article>;
}

function TechnicianProfile({ technician, projects, onClose }) {
  const technicianAge = age(technician.birth_date);
  const profileFields = [
    ['Identifiant', technician.username],
    ['Email', technician.email],
    ['Téléphone', technician.phone],
    ['Date de naissance', <span className="profile-birth-date"><span>{date(technician.birth_date)}</span>{technicianAge !== null && <span className="profile-age">Âge : {technicianAge} {technicianAge > 1 ? 'ans' : 'an'}</span>}</span>],
    ['Matricule', technician.employee_number],
    ['Date d’affectation', technician.assignment_date ? date(technician.assignment_date) : '—'],
    ['Adresse', technician.address],
    ['Projets travaillés', `${projects.filter(project => project.technicians.includes(technician.id)).length} projet(s)`],
  ].filter(([, value]) => value !== undefined);

  const activeProjects = projects.filter(project => project.status === 'ACTIVE' && project.technicians.includes(technician.id));
  const activeProjectCount = activeProjects.length;
  const projectsLabel = `${activeProjectCount} projet${activeProjectCount === 1 ? '' : 's'} en cours`;
  return <Modal title="Profil du Technicien" titleIcon={<HardHat size={20} aria-hidden="true" />} headerExtra={activeProjects.length > 0 && <div className="technician-project-summary">
    {activeProjects.map(project => <span className="technician-mission-status" key={project.id}><HardHat size={12} aria-hidden="true" />En cours - {project.site}</span>)}
  </div>} onClose={onClose} wide>
    <div className="technician-profile">
      <div className="technician-profile-heading">
        {technician.photo_url
          ? <img className="technician-profile-photo" src={technician.photo_url} alt={`Photo de ${technician.full_name}`} />
          : <span className="avatar light">{technician.full_name.slice(0, 2).toUpperCase()}</span>}
        <div className="technician-profile-identity"><h3>{technician.full_name}</h3><span>{technician.is_active ? 'Compte actif' : 'Compte désactivé'}</span>{activeProjects.length > 0 && <span className="technician-mission-status">En mission</span>}</div>
        {technician.specialty && <span className="technician-specialty-badge"><HardHat size={16} />{technician.specialty}</span>}
      </div>
      <dl className="technician-profile-fields">
        {profileFields.map(([label, value]) => <div key={label}><dt>{label}</dt><dd>{value || '—'}</dd></div>)}
      </dl>
      {technician.cv_url !== undefined && <section className="technician-profile-section">
        <h3>Curriculum vitæ</h3>
        {technician.cv_url
          ? <ul className="profile-documents"><ProfileDocument url={technician.cv_url} name={technician.cv_name || 'Curriculum vitæ'} /></ul>
          : <p>Aucun CV enregistré.</p>}
      </section>}
      {technician.experience !== undefined && <section className="technician-profile-section experience-card">
        <h3><BriefcaseBusiness size={19} aria-hidden="true" />Expérience professionnelle</h3>
        <ExperienceText value={technician.experience || 'Aucune expérience renseignée.'} />
      </section>}
      {technician.certificates !== undefined && <section className="technician-profile-section">
        <h3>Certificats / Habilitations</h3>
        {technician.certificate_documents?.length > 0
          ? <ul className="profile-documents">{technician.certificate_documents.map(document => <ProfileDocument key={document.id} url={document.url} name={document.name} />)}</ul>
          : <p>{technician.certificates || 'Aucun certificat renseigné.'}</p>}
      </section>}
    </div>
  </Modal>;
}

function ProfileDocument({ url, name }) {
  return <li className="profile-document">
    <a className="profile-document-name" href={url}><FileText size={19} aria-hidden="true" /><span>{name}</span></a>
    <span className="profile-document-actions">
      <a className="button profile-download profile-view" href={`${url}${url.includes('?') ? '&' : '?'}preview=1`} target="_blank" rel="noopener noreferrer" aria-label={`Voir ${name} dans un nouvel onglet`}>
        <Eye size={17} aria-hidden="true" />Voir
      </a>
      <a className="button profile-download" href={url} download aria-label={`Télécharger ${name}`}>
        <Download size={17} aria-hidden="true" />Télécharger
      </a>
    </span>
  </li>;
}

const frenchUnits = ['zéro', 'un', 'deux', 'trois', 'quatre', 'cinq', 'six', 'sept', 'huit', 'neuf', 'dix', 'onze', 'douze', 'treize', 'quatorze', 'quinze', 'seize'];
function frenchNumber(value) {
  const numberValue = Math.floor(Math.max(0, Number(value) || 0));
  if (numberValue < 17) return frenchUnits[numberValue];
  if (numberValue < 20) return `dix-${frenchUnits[numberValue - 10]}`;
  if (numberValue < 70) { const tens = ['vingt', 'trente', 'quarante', 'cinquante', 'soixante'][Math.floor(numberValue / 10) - 2]; const rest = numberValue % 10; return `${tens}${rest ? rest === 1 ? ' et un' : `-${frenchUnits[rest]}` : ''}`; }
  if (numberValue < 80) return `soixante-${frenchNumber(numberValue - 60)}`;
  if (numberValue < 100) return `quatre-vingt${numberValue % 10 ? `-${frenchUnits[numberValue % 10]}` : 's'}`;
  if (numberValue < 1000) { const hundreds = Math.floor(numberValue / 100); const rest = numberValue % 100; return `${hundreds === 1 ? 'cent' : `${frenchUnits[hundreds]} cent`}${rest ? ` ${frenchNumber(rest)}` : hundreds > 1 ? 's' : ''}`; }
  if (numberValue < 1000000) { const thousands = Math.floor(numberValue / 1000); const rest = numberValue % 1000; return `${thousands === 1 ? 'mille' : `${frenchNumber(thousands)} mille`}${rest ? ` ${frenchNumber(rest)}` : ''}`; }
  const millions = Math.floor(numberValue / 1000000); const rest = numberValue % 1000000;
  return `${millions === 1 ? 'un million' : `${frenchNumber(millions)} millions`}${rest ? ` ${frenchNumber(rest)}` : ''}`;
}
function amountInFrenchDinars(value) {
  const amount = Number(value) || 0; const dinars = Math.floor(amount); const centimes = Math.round((amount - dinars) * 100);
  return `${frenchNumber(dinars)} dinars${centimes ? ` et ${frenchNumber(centimes)} centimes` : ''}`.toUpperCase();
}

function InvoiceDetail({ invoice, close }) {
  return <Modal title={invoice.number} onClose={close} wide>
    <div className="invoice-document exact-invoice">
      <header className="exact-invoice-header"><img src={reportLogo} alt="Copetro Elite" /><div><span className="eyebrow green">FACTURE</span><h2>{invoice.number}</h2><p>Émise le {date(invoice.issued_at)} · Échéance : {date(invoice.due_date)}</p></div><Badge status={invoice.status} /></header>
      <section className="exact-invoice-client"><h3>{invoice.client_name}</h3><p>{invoice.billing_address || '—'}</p><div><span>RC : {invoice.client_rc || '—'}</span><span>NIF : {invoice.client_nif || '—'}</span><span>N° article : {invoice.client_article_number || '—'}</span><span>NIS : {invoice.client_nis || '—'}</span></div></section>
      <section className="exact-invoice-project"><strong>Projet : {invoice.project_name}</strong></section>
      <table className="exact-invoice-table"><thead><tr><th>N°</th><th>Réf.</th><th>Désignation</th><th>P.U.</th><th>Quantité</th><th>Jour</th><th>Unité</th><th>TVA</th><th>Montant</th></tr></thead><tbody>{invoice.lines.map((line, index) => <tr key={line.id}><td>{index + 1}</td><td>{invoice.project_name}</td><td><strong>{line.technician_name}</strong><br />{line.description}</td><td>{money(line.rate, invoice.currency)}</td><td>{number(line.hours)}</td><td>{date(line.work_date)}</td><td>HEURES</td><td>{number(invoice.tax_percent)} %</td><td>{money(line.amount, invoice.currency)}</td></tr>)}</tbody><tfoot><tr><td colSpan="8">Total HT</td><td>{money(invoice.subtotal, invoice.currency)}</td></tr><tr><td colSpan="8">Total TVA</td><td>{money(invoice.tax_amount, invoice.currency)}</td></tr><tr><td colSpan="8">Total TTC</td><td>{money(invoice.total, invoice.currency)}</td></tr></tfoot></table>
      <p className="invoice-total-words">Arrêté la présente facture à la somme de : <strong>{amountInFrenchDinars(invoice.total)}</strong></p>
      <div className="invoice-signature-space">Signature et cachet</div>
    </div>
    <footer className="form-footer"><button className="button secondary" onClick={close}>Fermer</button><button className="button" onClick={() => window.print()}><FileText size={16} />Imprimer / PDF</button></footer>
  </Modal>;
  /* Legacy layout retained below for reference. */
  return <Modal title={invoice.number} onClose={close} wide>
    <div className="invoice-document">
      <div className="invoice-top"><div><span className="eyebrow green">FACTURE</span><h2>{invoice.number}</h2><p>Émise le {date(invoice.issued_at)}<br />Échéance : {date(invoice.due_date)}</p></div><Badge status={invoice.status} /></div>
      <div className="invoice-parties"><div><small>FACTURÉ À</small><h3>{invoice.client_name}</h3><p className="prewrap">{invoice.billing_address}</p></div><div><small>PROJET</small><h3>{invoice.project_name}</h3><p>Bon de commande : {invoice.purchase_order || '—'}</p></div></div>
      <Table rows={invoice.lines} columns={[
        { label: 'Intervention', render: l => <div className="cell-stack"><strong>{l.technician_name} · {date(l.work_date)}</strong><span>{l.description}</span></div> },
        { label: 'Heures', render: l => number(l.hours) },
        { label: 'Tarif', render: l => money(l.rate, invoice.currency) },
        { label: 'Montant', render: l => money(l.amount, invoice.currency) },
      ]} />
      <div className="invoice-totals">
        <p><span>Total HT</span><b>{money(invoice.subtotal, invoice.currency)}</b></p>
        <p><span>Taxe ({number(invoice.tax_percent)} %)</span><b>{money(invoice.tax_amount, invoice.currency)}</b></p>
        <p className="grand-total"><span>Total TTC</span><b>{money(invoice.total, invoice.currency)}</b></p>
        <p><span>Déjà réglé</span><b>{money(invoice.paid, invoice.currency)}</b></p>
        <p><span>Reste à régler</span><b>{money(invoice.balance, invoice.currency)}</b></p>
      </div>
      {invoice.payments.length > 0 && <><h3>Règlements</h3>{invoice.payments.map(p => <p key={p.id}>{date(p.date)} · {money(p.amount, invoice.currency)} · {p.reference || 'Sans référence'}</p>)}</>}
    </div>
    <footer className="form-footer"><button className="button secondary" onClick={close}>Fermer</button><button className="button" onClick={() => window.print()}><FileText size={16} />Imprimer / PDF</button></footer>
  </Modal>;
}

function TechnicianReport({ technician, rows, projects, close }) {
  const projectById = new Map(projects.map(project => [project.id, project]));
  const reportRows = rows.map((entry, index) => {
    const project = projectById.get(entry.project);
    const rate = Number(project?.technician_hourly_rate || 0);
    const hours = Number(entry.hours || 0);
    return { entry, project, index: index + 1, rate, amount: rate * hours };
  });
  const clients = [...new Map(reportRows.map(row => [row.project?.client_details?.name, row.project?.client_details]).filter(([name, details]) => name && details)).values()];
  const subtotal = reportRows.reduce((total, row) => total + row.amount, 0);
  const total = subtotal;
  return <Modal title={`Relevé des pointages · ${technician.name}`} onClose={close} wide>
    <div className="technician-report">
      <header className="technician-report-header">
        <img src={reportLogo} alt="Copetro Elite" />
        <div><span className="eyebrow green">RELEVÉ DES POINTAGES</span><h2>{technician.name}</h2><p>Édité le {date(new Date())}</p></div>
      </header>
      <section className="technician-report-client"><h3>Informations client</h3>{clients.length ? clients.map(client => <div className="report-client-grid" key={client.name}>
        <strong>{client.name}</strong><span>RC : {client.rc || '—'}</span><span>NIF : {client.nif || '—'}</span><span>N° article : {client.article_number || '—'}</span><span>NIS : {client.nis || '—'}</span><span className="report-client-address">Adresse : {client.billing_address || '—'}</span>
      </div>) : <p className="muted">Informations client indisponibles.</p>}</section>
      <table className="technician-report-table"><thead><tr><th>N°</th><th>Réf.</th><th>Désignation</th><th>P.U.</th><th>Quantité</th><th>Jour</th><th>Unité</th><th>TVA</th><th>Montant</th></tr></thead><tbody>
        {reportRows.map(({ entry, project, index, rate, amount }) => <tr key={entry.id}><td>{index}</td><td>{project?.name || entry.project_name}</td><td>{entry.description || 'Heures standard'}</td><td>{rate ? money(rate, 'DZD') : '—'}</td><td>{number(entry.hours)}</td><td>{date(entry.start)}</td><td>HEURES</td><td>19 %</td><td>{rate ? money(amount, 'DZD') : '—'}</td></tr>)}
      </tbody><tfoot><tr><td colSpan="8">Total HT</td><td>{money(subtotal, 'DZD')}</td></tr><tr><td colSpan="8">Total TVA</td><td>{money(tax, 'DZD')}</td></tr><tr><td colSpan="8">Total TTC</td><td>{money(total, 'DZD')}</td></tr></tfoot></table>
    </div>
    <footer className="form-footer technician-report-actions"><button className="button secondary" onClick={close}>Fermer</button><button className="button" onClick={() => window.print()}><Download size={16} />Télécharger en PDF</button></footer>
  </Modal>;
}

function GlobalReport({ rows, projects, compact = false, close }) {
  const projectById = new Map(projects.map(project => [project.id, project]));
  const reportRows = rows.map((entry, index) => {
    const project = projectById.get(entry.project);
    const quantity = Number(entry.hours || 0);
    const clientRate = Number(project?.hourly_rate || 0);
    const clientCost = quantity * clientRate;
    const benefit = clientCost - quantity * Number(project?.technician_hourly_rate || 0);
    return { entry, project, index: index + 1, quantity, clientRate, clientCost, benefit };
  });
  const hours = reportRows.reduce((total, row) => total + Number(row.entry.hours || 0), 0);
  const totalClientCost = reportRows.reduce((sum, row) => sum + row.clientCost, 0);
  const totalBenefit = reportRows.reduce((sum, row) => sum + row.benefit, 0);
  return <Modal title={compact ? 'Résumé des pointages' : 'Fiche détaillée des pointages'} onClose={close} wide>
    <div className="technician-report">
      <header className="technician-report-header"><img src={reportLogo} alt="Copetro Elite" /><div><span className="eyebrow green">{compact ? 'RÉSUMÉ DES POINTAGES' : 'RELEVÉ GLOBAL'}</span><h2>{compact ? 'Techniciens sélectionnés' : 'Tous les techniciens'}</h2><p>{date(new Date())} · {number(hours)} h au total</p></div></header>
      <table className="technician-report-table"><thead><tr>{compact ? <><th>N°</th><th>Technicien</th><th>Projet</th><th>Quantité</th><th>Jour</th></> : <><th>N°</th><th>Technicien</th><th>Projet</th><th>P.U. client</th><th>Quantité</th><th>Jour</th><th>Coût client</th><th>Bénéfice</th></>}</tr></thead><tbody>{reportRows.map(({ entry, project, index, quantity, clientRate, clientCost, benefit }) => <tr key={entry.id}>{compact ? <><td>{index}</td><td>{entry.technician_name}</td><td>{project?.name || entry.project_name}</td><td>{number(quantity)} h</td><td>{date(entry.start)}</td></> : <><td>{index}</td><td>{entry.technician_name}</td><td>{project?.name || entry.project_name}</td><td>{clientRate ? money(clientRate, 'DZD') : '—'}</td><td>{number(quantity)} h</td><td>{date(entry.start)}</td><td>{money(clientCost, 'DZD')}</td><td>{money(benefit, 'DZD')}</td></>}</tr>)}</tbody>{!compact && <tfoot><tr><td colSpan="6">Total coût client</td><td>{money(totalClientCost, 'DZD')}</td><td>{money(totalBenefit, 'DZD')}</td></tr></tfoot>}</table>
    </div>
    <footer className="form-footer technician-report-actions"><button className="button secondary" onClick={close}>Fermer</button><button className="button" onClick={() => window.print()}><Download size={16} />Télécharger en PDF</button></footer>
  </Modal>;
}
