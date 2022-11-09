#!/usr/bin/env python
"""
Berdasarkan kanal yutup Aadil Matlo0b 
youtube: https://www.youtube.com/channel/UCTXiHVtLmYCRr_xGoWeefqg
Pakai Tkinter untuk mencari folder
Tidak untuk file yang jumlahnya banyak, jadi hanya file kecil saja.
dibuat oleh Aadil Matloob jan
youtube: https://www.youtube.com/channel/UCTXiHVtLmYCRr_xGoWeefqg
Secara sederhana mengubah file menjadi hash dengan metode md5
file md5 yang dobel, dihapus. Dah gitu aja.
"""

from tkinter.filedialog import askdirectory
from tkinter import Tk
import os , hashlib
from pathlib import Path
Tk().withdraw()


path =  askdirectory(title="Pilih folder yang diduga banyak duplikatnya")

file_list = os.walk(path)

unique = dict()
for root,folders,files in file_list:
    for file in files:
        path = Path(os.path.join(root,file))
        fileHash = hashlib.md5(open(path,'rb').read()).hexdigest()
        print(len(fileHash))
        if fileHash not in unique:
            unique[fileHash] = path
            
        else:
            os.remove(path)
            print(f"file di {path} sudah terhapus")