from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
import os
import base64
from io import BytesIO # Meskipun diimpor, BytesIO tidak secara eksplisit digunakan dalam kode ini.

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads' # Menentukan folder untuk menyimpan file yang diunggah
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True) # Membuat folder 'uploads' jika belum ada, tidak error jika sudah ada

def hex_to_hsv_color(hex_color_str):
    """Mengonversi string warna HEX menjadi tuple (H, S, V).""" # Mengubah komentar docstring fungsi
    hex_color_str = hex_color_str.lstrip('#') # Menghapus karakter '#' dari awal string
    rgb_color = tuple(int(hex_color_str[i:i+2], 16) for i in (0, 2, 4)) # Konversi HEX ke tuple RGB
    # Konversi RGB ke piksel BGR 1x1 untuk OpenCV
    bgr_pixel = np.uint8([[rgb_color[::-1]]]) # RGB ke BGR (OpenCV menggunakan BGR)
    hsv_pixel = cv2.cvtColor(bgr_pixel, cv2.COLOR_BGR2HSV) # Konversi BGR ke HSV
    return hsv_pixel[0][0] # Mengembalikan nilai HSV dari piksel

@app.route('/')
def index():
    return render_template('index.html') # Menampilkan halaman utama dari file index.html

@app.route('/process_image', methods=['POST'])
def process_image_route():
    if 'image' not in request.files:
        return jsonify({'error': 'Tidak ada file gambar yang diberikan'}), 400 # Error jika tidak ada file gambar
    
    # Menggunakan getlist untuk 'colors[]' atau fallback untuk 'colors'
    hex_colors_str_list = request.form.getlist('colors[]')
    if not hex_colors_str_list:
        hex_colors_flat = request.form.get('colors', '')
        if hex_colors_flat:
            hex_colors_str_list = hex_colors_flat.split(',')
        else:
             return jsonify({'error': 'Tidak ada warna yang diberikan'}), 400 # Error jika tidak ada warna yang diberikan


    image_file = request.files['image'] # Mendapatkan file gambar dari permintaan

    if not image_file.filename:
        return jsonify({'error': 'Tidak ada file yang dipilih'}), 400 # Error jika tidak ada nama file yang dipilih

    filename = os.path.join(app.config['UPLOAD_FOLDER'], image_file.filename) # Membuat path lengkap untuk menyimpan file
    image_file.save(filename) # Menyimpan file yang diunggah

    try:
        bgr_image = cv2.imread(filename) # Membaca gambar menggunakan OpenCV (format BGR)
        if bgr_image is None: # Jika gambar tidak bisa dibaca
            os.remove(filename) # Hapus file yang gagal dibaca
            return jsonify({'error': 'Tidak dapat membaca file gambar. Pastikan format gambar valid.'}), 400
        
        rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB) # Konversi gambar dari BGR ke RGB
        hsv_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2HSV) # Konversi gambar dari RGB ke HSV

        combined_mask = np.zeros((hsv_image.shape[0], hsv_image.shape[1]), dtype=np.uint8) # Membuat mask kosong (semua hitam) seukuran gambar

        # Mendefinisikan toleransi untuk thresholding HSV
        # Toleransi Hue: mis., +/- 10 (maks 179 untuk Hue OpenCV)
        # Toleransi Saturasi: mis., +/- 50 (maks 255)
        # Toleransi Value: mis., +/- 50 (maks 255)
        # Nilai-nilai ini mungkin perlu disesuaikan untuk sensitivitas yang diinginkan
        h_tolerance = 7 # Toleransi untuk Hue
        s_tolerance = 50  # Toleransi untuk Saturasi, ditingkatkan untuk pencocokan warna yang lebih baik
        v_tolerance = 50  # Toleransi untuk Value, ditingkatkan untuk pencocokan warna yang lebih baik

        for hex_c in hex_colors_str_list: # Loop untuk setiap warna HEX yang dipilih
            if not hex_c.startswith('#') or not (len(hex_c) == 7 or len(hex_c) == 4): # Validasi dasar format HEX
                print(f"Melewati warna HEX yang tidak valid: {hex_c}") # Cetak pesan jika format HEX tidak valid
                continue # Lanjutkan ke iterasi berikutnya

            hsv_target = hex_to_hsv_color(hex_c) # Konversi warna HEX target ke HSV
            H, S, V = int(hsv_target[0]), int(hsv_target[1]), int(hsv_target[2]) # Ekstrak komponen H, S, V

            # Mendefinisikan batas bawah dan atas untuk warna saat ini
            lower_bound = np.array([max(0, H - h_tolerance), max(0, S - s_tolerance), max(0, V - v_tolerance)])
            upper_bound = np.array([min(179, H + h_tolerance), min(255, S + s_tolerance), min(255, V + v_tolerance)])
            
            current_color_mask = None # Inisialisasi mask untuk warna saat ini
            # Menangani Hue wrapping (misalnya, untuk warna merah yang melintasi batas 0/179)
            if H - h_tolerance < 0: # Jika batas bawah Hue melintasi 0
                # Mask 1: (0, H + toleransi_hue)
                lower1 = np.array([0, lower_bound[1], lower_bound[2]])
                upper1 = np.array([H + h_tolerance, upper_bound[1], upper_bound[2]])
                mask1 = cv2.inRange(hsv_image, lower1, upper1)
                # Mask 2: (180 + (H - toleransi_hue), 179) -> (H_alternatif_bawah, 179)
                lower2 = np.array([max(0, 180 + (H - h_tolerance)), lower_bound[1], lower_bound[2]])
                upper2 = np.array([179, upper_bound[1], upper_bound[2]])
                mask2 = cv2.inRange(hsv_image, lower2, upper2)
                current_color_mask = cv2.bitwise_or(mask1, mask2) # Gabungkan kedua mask
            elif H + h_tolerance > 179: # Jika batas atas Hue melintasi 179
                # Mask 1: (H - toleransi_hue, 179)
                lower1 = np.array([H - h_tolerance, lower_bound[1], lower_bound[2]])
                upper1 = np.array([179, upper_bound[1], upper_bound[2]])
                mask1 = cv2.inRange(hsv_image, lower1, upper1)
                # Mask 2: (0, (H + toleransi_hue) - 180) -> (0, H_alternatif_atas)
                lower2 = np.array([0, lower_bound[1], lower_bound[2]])
                upper2 = np.array([min(179, (H + h_tolerance) - 180), upper_bound[1], upper_bound[2]])
                mask2 = cv2.inRange(hsv_image, lower2, upper2)
                current_color_mask = cv2.bitwise_or(mask1, mask2) # Gabungkan kedua mask
            else: # Jika tidak ada Hue wrapping
                current_color_mask = cv2.inRange(hsv_image, lower_bound, upper_bound) # Buat mask tunggal
            
            combined_mask = cv2.bitwise_or(combined_mask, current_color_mask) # Gabungkan mask warna saat ini ke mask gabungan

        # Membuat bagian berwarna dari gambar
        colored_part = cv2.bitwise_and(rgb_image, rgb_image, mask=combined_mask)

        # Membuat bagian grayscale dari gambar
        # Pertama, dapatkan inverse mask (area yang TIDAK akan diwarnai)
        inverse_mask = cv2.bitwise_not(combined_mask)
        # Ekstrak latar belakang dari gambar RGB asli menggunakan inverse mask
        background_rgb = cv2.bitwise_and(rgb_image, rgb_image, mask=inverse_mask)
        # Konversi latar belakang yang diekstrak ini ke grayscale
        gray_background_single_channel = cv2.cvtColor(background_rgb, cv2.COLOR_RGB2GRAY)
        # Konversi grayscale satu kanal kembali ke gambar BGR/RGB 3 kanal
        # sehingga dapat digabungkan dengan bagian berwarna.
        # Kita harus memastikan area yang awalnya hitam di background_rgb (karena masking)
        # tetap hitam, dan tidak berubah menjadi representasi abu-abu dari hitam.
        gray_background_rgb = cv2.cvtColor(gray_background_single_channel, cv2.COLOR_GRAY2RGB)
        
        # Sangat penting, terapkan kembali inverse_mask ke gambar grayscale 3 kanal.
        # Ini memastikan hanya area yang tidak dipilih yang benar-benar mendapatkan perlakuan grayscale,
        # dan area yang seharusnya berwarna (dan menjadi hitam di background_rgb setelah masking-nya)
        # tidak secara tidak sengaja diisi dengan representasi abu-abu dari hitam.
        gray_background_rgb = cv2.bitwise_and(gray_background_rgb, gray_background_rgb, mask=inverse_mask)


        # Gabungkan bagian berwarna dan bagian grayscale
        # Di mana combined_mask diatur, gunakan colored_part, jika tidak gunakan gray_background_rgb
        final_image_rgb = cv2.add(colored_part, gray_background_rgb)


        # Encode gambar yang diproses untuk dikirim kembali
        # Konversi gambar RGB final ke BGR untuk imencode OpenCV
        final_image_bgr = cv2.cvtColor(final_image_rgb, cv2.COLOR_RGB2BGR)
        _, img_encoded = cv2.imencode('.png', final_image_bgr) # Encode gambar ke format PNG
        img_base64 = base64.b64encode(img_encoded.tobytes()).decode('utf-8') # Encode ke Base64

        os.remove(filename) # Hapus file yang diunggah dari server

        return jsonify({'processed_image': f'data:image/png;base64,{img_base64}'}) # Kirim gambar hasil proses sebagai JSON

    except Exception as e: # Jika terjadi error selama proses
        app.logger.error(f"Error memproses gambar: {e}") # Catat error ke log server
        if os.path.exists(filename): # Pastikan file dibersihkan bahkan jika terjadi error
            os.remove(filename)
        return jsonify({'error': str(e)}), 500 # Kirim pesan error sebagai JSON

if __name__ == '__main__':
    app.run(debug=True) # Jalankan server Flask dalam mode debug