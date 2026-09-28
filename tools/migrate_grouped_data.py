"""Convert the five legacy files into three grouped files, with a ZIP backup.

Run once with: python tools/migrate_grouped_data.py
Legacy 4-column registrations are treated as graded, matching the old reader.
"""
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path
import os
import zipfile


LEGACY = ('MonHoc.txt', 'Lop.txt', 'SinhVien.txt', 'LopTinChi.txt', 'DangKy.txt')


def rows(raw):
    return [line for line in raw.decode('utf-8-sig').splitlines() if line.strip()]


def convert(originals):
    subjects = rows(originals['MonHoc.txt'])
    classes = rows(originals['Lop.txt'])
    students = rows(originals['SinhVien.txt'])
    credits = rows(originals['LopTinChi.txt'])
    registrations = rows(originals['DangKy.txt'])
    class_children, credit_children = {}, {}
    for line in classes:
        fields = line.split('|')
        if len(fields) != 2 or fields[0] in class_children:
            raise ValueError('Invalid or duplicate class header: ' + line)
        class_children[fields[0]] = []
    student_ids = set()
    for line in students:
        fields = line.split('|')
        if len(fields) != 6 or fields[0] not in class_children or fields[1] in student_ids:
            raise ValueError('Invalid, orphaned or duplicate student: ' + line)
        student_ids.add(fields[1])
        class_children[fields[0]].append('|'.join(fields[1:]))
    subject_ids = {line.split('|')[0] for line in subjects}
    if len(subject_ids) != len(subjects) or any(len(line.split('|')) != 4 for line in subjects):
        raise ValueError('Invalid or duplicate subjects')
    for line in credits:
        fields = line.split('|')
        if len(fields) != 8 or fields[0] in credit_children or fields[1] not in subject_ids:
            raise ValueError('Invalid, orphaned or duplicate credit class: ' + line)
        credit_children[fields[0]] = []
    registration_ids = set()
    for line in registrations:
        fields = line.split('|')
        if len(fields) == 4:
            fields.append('1')
        if len(fields) != 5 or fields[0] not in credit_children or fields[1] not in student_ids:
            raise ValueError('Invalid or orphaned registration: ' + line)
        key = tuple(fields[:2])
        if key in registration_ids:
            raise ValueError('Duplicate registration: ' + line)
        registration_ids.add(key)
        credit_children[fields[0]].append('|'.join(fields[1:]))

    def grouped(headers, children):
        result = []
        for header in headers:
            result.extend([header, *children[header.split('|')[0]], '#'])
        return '\n'.join(result) + ('\n' if result else '')

    outputs = {
        'monhoc.txt': '\n'.join(subjects) + ('\n' if subjects else ''),
        'lopsinhvien.txt': grouped(classes, class_children),
        'loptinchi.txt': grouped(credits, credit_children),
    }
    counts = dict(subjects=len(subjects), classes=len(classes), students=len(students),
                  credit_classes=len(credits), registrations=len(registrations))
    return outputs, counts


def migrate(data_dir, backup_dir):
    if (data_dir / 'lopsinhvien.txt').exists():
        raise ValueError('lopsinhvien.txt already exists; refusing to overwrite grouped data')
    originals = {name: (data_dir / name).read_bytes() for name in LEGACY}
    outputs, counts = convert(originals)
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup = backup_dir / ('data-before-grouping-' + datetime.now().strftime('%Y%m%d-%H%M%S-%f') + '.zip')
    with zipfile.ZipFile(backup, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        for name, raw in originals.items():
            archive.writestr(name, raw)
    with zipfile.ZipFile(backup) as archive:
        assert all(archive.read(name) == raw for name, raw in originals.items())
    try:
        for name, value in outputs.items():
            temporary = data_dir / (name + '.migration.tmp')
            temporary.write_text(value, encoding='utf-8', newline='\n')
            os.replace(temporary, data_dir / name)
        # On case-sensitive filesystems the two old capitalized files are distinct.
        for name in LEGACY:
            old = data_dir / name
            new = data_dir / name.lower()
            if name in ('MonHoc.txt', 'LopTinChi.txt'):
                if old.exists() and not old.samefile(new):
                    old.unlink()
            else:
                old.unlink()
    except Exception:
        for name, raw in originals.items():
            (data_dir / name).write_bytes(raw)
        raise
    return backup, counts


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, default=root / 'backend/data')
    parser.add_argument('--backup-dir', type=Path, default=root / 'backups')
    args = parser.parse_args()
    backup, counts = migrate(args.data_dir, args.backup_dir)
    print('Backup:', backup)
    print('Migrated:', counts)
