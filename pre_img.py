import pytesseract
import urllib
import cv2
import math
import datetime
import re
import numpy as np
from unidecode import unidecode
from PIL import Image

now = datetime.datetime.now().strftime("%d-%m-%Y")

def process_image(path=None, name=None):
	# Jika ada gambar...
	if path != None:
		# Baca gambar
		original_image = cv2.imread(path) 
		# Mengambil panjang dan lebar gambar
		original_height, original_width = original_image.shape[:2]
		# Resize width gambar menjadi 640, dan height mengikuti sesuai dengan aspect ratio
		image = cv2.resize(original_image, (int(math.floor(original_width*1000/original_height)), 1000)) 
		# Mengambil panjang dan lebar gambar yang telah diresize
		resized_height, resized_width = image.shape[:2]
		# Menyimpan gambar yang telah diresize 
		cv2.imwrite('./static/uploads/tmp/resized.jpg', image)
		cv2.imwrite("./static/uploads/{}/resized_{}".format(now, name), image)
	# Jika tidak...
	else:
		return "Mohon masukkan gambar terlebih dahulu"
	
	# Variabel pendukung lainnya
	result = []
	temp = ""

	print ("Membaca paspor, harap menunggu...")
	try:
		# print(x) # DEBUG
		# Mengambil Region of Interest dari gambar yang di resize
		roi = image[resized_height-216:resized_height, 0:resized_width]
		# Menyimpan ROI
		cv2.imwrite('./static/uploads/tmp/roi.jpg', roi)
		# Membuat Grayscale ROI dari ROI
		gray = cv2.cvtColor(roi,cv2.COLOR_RGB2GRAY)
		# Menyimpan Grayscale ROI
		cv2.imwrite('./static/uploads/tmp/bw.jpg', gray)
		# Membuat Binary ROI dari Grayscale ROI
		ret2,th2 = cv2.threshold(gray,240,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
		# Menyimpan Binary ROI
		cv2.imwrite('./static/uploads/tmp/th.jpg', th2)
		# Membuat Denoised ROI dari Binary ROI
		dst = cv2.fastNlMeansDenoising(th2,10,10,7)
		# Menyimpan Denoised ROI
		cv2.imwrite('./static/uploads/tmp/denoised.jpg', dst)
		# # Membuat Dilated ROI dari Denoised ROI
		# dil = cv2.dilate(dst, np.ones((3,3), np.uint8), iterations=1)
		# # Menyimpan Dilated ROI 
		# cv2.imwrite('./static/uploads/tmp/dilated.jpg', dil)
		# Pembacaan teks dengan pytesseract
		# ocr_string = pytesseract.image_to_string(Image.open('./static/uploads/tmp/dilated.jpg'),lang='eng').strip().replace(" ", "")
		ocr_string = pytesseract.image_to_string(Image.open('./static/uploads/tmp/denoised.jpg'),lang='eng').strip().replace(" ", "")
		# Menghilangkan spaces yang ada di dalam pembacaan
		re.sub('[\s\t+]', '', ocr_string)
		# Memisahkan barcode baris pertama dan kedua
		split = ocr_string.split('\n')
		# Pembacaan baris pertama
		first_row = re.split("<", split[0])
		first_row = list(filter(None, first_row))
		# Pembacaan baris pertama - Jenis Paspor
		result.append(first_row[0])
		# Pembacaan baris pertama - Negara yang Mengeluarkan
		result.append(first_row[1][:3])
		# Pembacaan baris pertama - Nama
		for x in first_row[2:]:
			temp += x + " "
		result.append(temp + first_row[1][3:])
		# Pembacaan baris kedua
		second_row = re.split("<", split[1])
		second_row = list(filter(None, second_row))
		# Pembacaan baris kedua - Nomor Passport
		result.append(second_row[0])
		# Pembacaan baris kedua - Kewarganegaraan
		result.append(second_row[1][1:4])
		# Pembacaan baris kedua - Tanggal Lahir
		result.append(second_row[1][4:10])
		# Pembacaan baris kedua - Jenis Kelamin
		result.append(second_row[1][11])
		# Pembacaan baris kedua - Tanggal kadaluarsa
		result.append(second_row[1][12:18])
	except:
		raise

	# Memberikan hasil
	return result 