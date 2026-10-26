"""Local CV validation and extraction. Uploaded documents never leave this machine."""
import os
from pathlib import Path
import re
import subprocess
import tempfile
import time
import unicodedata

from django.conf import settings
import pymupdf
from rest_framework.exceptions import ValidationError

MAX_CV_BYTES = 10 * 1024 * 1024
MAX_PHOTO_BYTES = 5 * 1024 * 1024
CV_TYPES = {'.pdf': 'pdf', '.png': 'png', '.jpg': 'jpeg', '.jpeg': 'jpeg'}


def read_cv(upload, label='CV'):
    extension = Path(upload.name).suffix.lower()
    if extension not in CV_TYPES:
        raise ValidationError(f'Choisissez un {label} au format PDF, JPG ou PNG.')
    if upload.size > MAX_CV_BYTES:
        raise ValidationError(f'Le {label} ne doit pas dépasser 10 Mo.')
    upload.seek(0)
    data = upload.read(MAX_CV_BYTES + 1)
    upload.seek(0)
    if len(data) > MAX_CV_BYTES:
        raise ValidationError(f'Le {label} ne doit pas dépasser 10 Mo.')
    signatures = {'.pdf': b'%PDF-', '.png': b'\x89PNG\r\n\x1a\n', '.jpg': b'\xff\xd8\xff', '.jpeg': b'\xff\xd8\xff'}
    if not data.startswith(signatures[extension]):
        raise ValidationError(f'Le contenu du {label} ne correspond pas à son format.')
    try:
        with pymupdf.open(stream=data, filetype=CV_TYPES[extension]) as document:
            if document.needs_pass:
                raise ValidationError('Le PDF est protégé. Importez une copie sans mot de passe.')
            if not len(document):
                raise ValidationError(f'Le {label} ne contient aucune page lisible.')
            for page in document:
                if page.rect.is_empty or page.rect.is_infinite:
                    raise ValidationError(f'Une page du {label} est illisible.')
    except (RuntimeError, ValueError) as exc:
        raise ValidationError('Ce fichier est endommagé ou illisible.') from exc
    return data, CV_TYPES[extension]


def validate_cv(upload):
    read_cv(upload)
    return upload


def validate_profile_photo(upload):
    extension = Path(upload.name).suffix.lower()
    if extension not in {'.png', '.jpg', '.jpeg', '.jgp', '.webp', '.avif'}:
        raise ValidationError('Choisissez une photo au format PNG, WebP, JPG/JPEG ou AVIF.')
    if upload.size > MAX_PHOTO_BYTES:
        raise ValidationError('La photo ne doit pas dépasser 5 Mo.')
    upload.seek(0)
    data = upload.read(MAX_PHOTO_BYTES + 1)
    upload.seek(0)
    if len(data) > MAX_PHOTO_BYTES:
        raise ValidationError('La photo ne doit pas dépasser 5 Mo.')
    if extension == '.png':
        valid_signature = data.startswith(b'\x89PNG\r\n\x1a\n')
    elif extension in {'.jpg', '.jpeg', '.jgp'}:
        valid_signature = data.startswith(b'\xff\xd8\xff')
    elif extension == '.webp':
        valid_signature = len(data) >= 12 and data.startswith(b'RIFF') and data[8:12] == b'WEBP'
    else:
        valid_signature = len(data) >= 12 and data[4:8] == b'ftyp' and (b'avif' in data[8:32] or b'avis' in data[8:32])
    if not valid_signature:
        raise ValidationError('Le contenu de la photo ne correspond pas à son format.')
    if extension in {'.png', '.jpg', '.jpeg', '.jgp'}:
        try:
            filetype = 'png' if extension == '.png' else 'jpeg'
            with pymupdf.open(stream=data, filetype=filetype) as document:
                if not len(document) or document[0].rect.is_empty:
                    raise ValidationError('La photo ne contient aucune image lisible.')
        except (RuntimeError, ValueError) as exc:
            raise ValidationError('Cette photo est endommagée ou illisible.') from exc
    return upload


def validate_certificate(upload):
    read_cv(upload, label='certificat')
    return upload


def ocr_image(path, timeout):
    if os.name != 'nt':
        raise ValidationError('La lecture des images nécessite le moteur OCR Windows. Vous pouvez saisir l’expérience manuellement.')
    try:
        result = subprocess.run(
            ['powershell.exe', '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass',
             '-File', str(settings.BASE_DIR / 'scripts' / 'ocr-image.ps1'), '-ImagePath', str(path)],
            capture_output=True, encoding='utf-8', errors='replace', timeout=max(1, timeout),
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValidationError('La lecture du CV a échoué ou a pris trop de temps. Essayez un fichier plus court ou saisissez l’expérience.') from exc
    if result.returncode:
        raise ValidationError('La lecture de l’image est indisponible. Vérifiez le moteur OCR Windows ou saisissez l’expérience manuellement.')
    return result.stdout.strip()


def normalized(text):
    return ''.join(c for c in unicodedata.normalize('NFKD', text.lower()) if not unicodedata.combining(c))


EXPERIENCE_HEADING = re.compile(
    r'(?:experiences?(?:\s+(?:professionnelles?|de travail))?|parcours professionnel|professional experience|work experience|employment history)'
)
END_EXPERIENCE_HEADING = re.compile(
    r'(?:formations?(?:\s+(?:academiques?|professionnelles?))?|education|diplomes?|certificats?|certifications?|competences(?: techniques)?|(?:technical )?skills|langues?|languages?|loisirs|centres? d.interet|references|profil|contact)'
)


def _heading_match(line, pattern):
    folded = []
    positions = []
    for index, character in enumerate(line):
        for normalized_character in unicodedata.normalize('NFKD', character.lower()):
            if not unicodedata.combining(normalized_character):
                folded.append(normalized_character)
                positions.append(index)
    text = ''.join(folded).strip(' :–-•\t')
    offset = len(''.join(folded)) - len(''.join(folded).lstrip())
    match = pattern.search(text)
    if not match:
        return None
    start = positions[offset + match.start()]
    end = positions[offset + match.end() - 1] + 1
    return match, start, end


def experience_section(text):
    lines = text.splitlines()
    selected, collecting = [], False
    for line in lines:
        start = _heading_match(line, EXPERIENCE_HEADING)
        end = _heading_match(line, END_EXPERIENCE_HEADING)
        if start and (not end or start[0].start() <= end[0].start()):
            collecting = True
            inline_text = line[start[2]:].strip(' :–-•\t')
            if inline_text:
                selected.append(inline_text)
            continue
        if collecting and end:
            collecting = False
            continue
        if collecting:
            selected.append(line)
    return '\n'.join(selected).strip()


def pdf_experience_section(document):
    selected = []
    collecting = False
    for page in document:
        blocks = page.get_text('blocks')
        heading = next((block for block in blocks
                        if EXPERIENCE_HEADING.fullmatch(normalized(block[4]).strip().strip(' :–-•'))), None)
        if not collecting and heading is None:
            continue
        collecting = True
        # PDF blocks end in newlines. Match trimmed headings, then read only
        # their column so a sidebar cannot interrupt or contaminate the jobs.
        left, top, right = 0, 0, page.rect.width
        if heading is not None:
            left, top = max(0, heading[0] - 20), heading[3]
            for block in blocks:
                if (block[0] > heading[2] and
                        END_EXPERIENCE_HEADING.fullmatch(normalized(block[4]).strip().strip(' :–-•'))):
                    right = min(right, block[0])
        # A following page may continue the jobs using the full page width.
        # Stop at the next section in the selected column, preserving dates
        # aligned to the right of each job title.
        for block in sorted(blocks, key=lambda item: (item[1], item[0])):
            if block[1] < top - 2 or not left <= block[0] < right or block is heading:
                continue
            if END_EXPERIENCE_HEADING.fullmatch(normalized(block[4]).strip().strip(' :–-•')):
                text = page.get_text(clip=pymupdf.Rect(left, top, right, block[1]), sort=True).strip()
                if text:
                    selected.append(text)
                return '\n'.join(selected).strip()
        text = page.get_text(clip=pymupdf.Rect(left, top, right, page.rect.height), sort=True).strip()
        if text:
            selected.append(text)
    return '\n'.join(selected).strip()


def extract_cv(upload):
    data, filetype = read_cv(upload)
    pages = []
    experience = ''
    deadline = time.monotonic() + 60
    with pymupdf.open(stream=data, filetype=filetype) as document, tempfile.TemporaryDirectory(prefix='copet-cv-') as temp:
        for index, page in enumerate(document):
            text = page.get_text(sort=True).strip() if filetype == 'pdf' else ''
            if len(text) < 30:
                if time.monotonic() >= deadline:
                    raise ValidationError('La lecture a pris trop de temps. Essayez un CV plus court.')
                scale = min(2, 2400 / max(page.rect.width, page.rect.height))
                pixmap = page.get_pixmap(matrix=pymupdf.Matrix(scale, scale), colorspace=pymupdf.csRGB, alpha=False)
                path = Path(temp) / f'page-{index}.png'
                pixmap.save(path)
                text = ocr_image(path, deadline - time.monotonic())
            pages.append(text)
        if filetype == 'pdf':
            experience = pdf_experience_section(document)
    text = '\n\n'.join(pages).strip()
    if not text:
        raise ValidationError('Aucun texte lisible trouvé. Essayez un CV plus net ou saisissez l’expérience manuellement.')
    experience = experience or experience_section(text)
    return {
        'experience': experience[:20000],
        'extracted_text': text[:20000],
        'warning': '' if experience else 'La rubrique Expérience n’a pas été identifiée. Sélectionnez les passages utiles dans le texte extrait.',
    }


def extract_cv_photo(upload):
    data, filetype = read_cv(upload)
    candidates = []
    seen = set()
    with pymupdf.open(stream=data, filetype=filetype) as document:
        for page_number, page in enumerate(document, start=1):
            if filetype == 'pdf':
                images = [image[0] for image in page.get_images(full=True)]
            else:
                images = [None]
            for xref in images:
                if xref is None:
                    scale = min(1, 640 / max(page.rect.width, page.rect.height))
                    source = page.get_pixmap(matrix=pymupdf.Matrix(scale, scale))
                else:
                    if xref in seen:
                        continue
                    seen.add(xref)
                    try:
                        source = pymupdf.Pixmap(document, xref)
                    except (RuntimeError, ValueError):
                        continue
                    if source.width < 48 or source.height < 48:
                        continue
                if source.width < 48 or source.height < 48:
                    continue
                rects = page.get_image_rects(xref) if xref is not None else [page.rect]
                placement_area = max((rect.width * rect.height / (page.rect.width * page.rect.height)
                                      for rect in rects), default=1)
                if source.colorspace != pymupdf.csRGB:
                    try:
                        source = pymupdf.Pixmap(pymupdf.csRGB, source)
                    except (RuntimeError, ValueError):
                        continue
                scale = min(1, 640 / max(source.width, source.height))
                if scale < 1:
                    source = pymupdf.Pixmap(source, max(1, round(source.width * scale)),
                                            max(1, round(source.height * scale)))
                aspect_penalty = abs(source.width / source.height - 0.78)
                candidates.append(((placement_area > 0.55, aspect_penalty,
                                    -min(source.width * source.height, 640 * 640), page_number),
                                   source.tobytes('png')))
    return min(candidates, key=lambda candidate: candidate[0])[1] if candidates else None
