#!/usr/bin/env python

"""
Algoritma tercepat mencari file duplikat
cara pakai: python3 hapus_duplikat_cepat.py <folder_asal_duplikat> [<folder_tujuan_bebersih>...]

Dari https://stackoverflow.com/a/36113168/300783
Dimodifikasi dari python2 ke python3 dengan beberapa tambahan kode

Konsep 
- Buat tabel hash file, di mana ukuran file adalah kuncinya.
- Untuk file dengan ukuran yang sama, buat tabel hash dengan hash 1024 byte pertama untuk membuat penomoran unik.
- Untuk file dengan hash yang sama pada 1k byte pertama, hitung hash pada konten lengkap - file yang cocok TIDAK unik.

Saya pakai untuk mengecek duplikasi data 5tb di external HDD jadul.
"""

import os
import sys
import hashlib
from collections import defaultdict


def chunk_reader(fobj, chunk_size=1024):
    """ fungsi untuk mengubah file menjadi byte """
    while True:
        chunk = fobj.read(chunk_size)
        if not chunk:
            return
        yield chunk


def get_hash(filename, first_chunk_only=False, hash_algo=hashlib.sha1):
    hashobj = hash_algo()
    with open(filename, "rb") as f:
        if first_chunk_only:
            hashobj.update(f.read(1024))
        else:
            for chunk in chunk_reader(f):
                hashobj.update(chunk)
    return hashobj.digest()


def check_for_duplicates(paths):
    files_by_size = defaultdict(list)
    files_by_small_hash = defaultdict(list)
    files_by_full_hash = dict()

    for path in paths:
        for dirpath, _, filenames in os.walk(path):
            for filename in filenames:
                full_path = os.path.join(dirpath, filename)
                try:
                    # Jika target adalah symlink (soft) maka ini akan mencari target dengan value lain
                    # apa itu symlink? File yang memiliki ketergantungan dgn file lain
                    # baca https://ostechnix.com/explaining-soft-link-and-hard-link-in-linux-with-examples/
                    full_path = os.path.realpath(full_path)
                    file_size = os.path.getsize(full_path)
                except OSError:
                    # Jika file tidak bisa diakses karena ijin dsb maka akan lanjut
                    continue
                files_by_size[file_size].append(full_path)

    # Untuk semua file dengan ukuran file yang sama, dapatkan hashnya pada 1024 byte pertama
    for file_size, files in files_by_size.items():
        if len(files) < 2:
            continue  # Jika ukuran file unik, tidak perlu menghabiskan cpu. Boros listrik dan buang waktu aja.

        for filename in files:
            try:
                small_hash = get_hash(filename, first_chunk_only=True)
            except OSError:
                # akses file mungkin telah berubah jika titik exec ada di sini
                continue
            files_by_small_hash[(file_size, small_hash)].append(filename)


    # Untuk mendapatkan semua file dengan hash 1024 byte pertama - 
    # hash yang sama akan dirubah menjadi duplikat
    for files in files_by_small_hash.values():
        if len(files) < 2:
            # hash yang memili 1k byte pertama adalah unik -> skip aja file ini.
            continue

        for filename in files:
            try:
                full_hash = get_hash(filename, first_chunk_only=False)
            except OSError:
                # akses file mungkin telah berubah jika titik exec ada di sini
                continue

            if full_hash in files_by_full_hash:
                duplicate = files_by_full_hash[full_hash]
                print("File ganda:\n - %s\n - %s\n" % (filename, duplicate))
            else:
                files_by_full_hash[full_hash] = filename


if __name__ == "__main__":
    if sys.argv[1:]:
        check_for_duplicates(sys.argv[1:])
    else:
        print("Usage: %s <folder> [<folder>...]" % sys.argv[0])