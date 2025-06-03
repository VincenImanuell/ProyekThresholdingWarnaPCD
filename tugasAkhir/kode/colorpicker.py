import streamlit as st
from PIL import Image
import numpy as np
import io

# Fungsi untuk mengambil RGB dari koordinat (x, y) di gambar
def get_color_from_image(image, x, y):
    return image.getpixel((x, y))

# Web Interface dengan Streamlit
def main():
    st.title("Pilih Warna dari Gambar")

    # Upload gambar
    uploaded_file = st.file_uploader("Unggah gambar", type=["jpg", "png", "jpeg"])
    
    if uploaded_file is not None:
        # Buka gambar menggunakan PIL
        image = Image.open(uploaded_file)
        st.image(image, caption="Gambar yang diunggah", use_column_width=True)

        # Mendapatkan data gambar dalam format array NumPy
        image_np = np.array(image)

        # Membuat fungsi untuk memilih koordinat dari gambar (dengan menekan mouse)
        st.write("Klik pada gambar untuk memilih warna")
        
        # Interaksi mouse untuk memilih warna
        mouse_position = st.experimental_get_query_params()

        if mouse_position:
            x, y = mouse_position.get('x')[0], mouse_position.get('y')[0]
            selected_color = get_color_from_image(image, x, y)
            st.write(f"Warna yang dipilih: {selected_color}")

if __name__ == "__main__":
    main()
