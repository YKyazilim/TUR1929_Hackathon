# İçe Aktarma
from flask import Flask, render_template, request
import jsonify
import ayrıştırma as np
import ayrıştırma as class_names
import ayrıştırma as os
import ayrıştırma as model
import ayrıştırma as prepare_image


app = Flask(__name__)

def result_calculate(size, lights, device):
    # Elektrikli cihazların enerji tüketimini hesaplamaya olanak tanıyan değişkenler
    home_coef = 100
    light_coef = 0.04
    devices_coef = 5   
    return size * home_coef + lights * light_coef + device * devices_coef 

# İlk sayfa
@app.route('/')
def index():
    return render_template('index.html')

# İkinci sayfa
@app.route('/<size>')
def lights(size):
    return render_template(
                            'lights.html', 
                            size=size
                           )

# Üçüncü sayfa
@app.route('/<size>/<lights>')
def electronics(size, lights):
    return render_template(
                            'electronics.html',                           
                            size=size, 
                            lights=lights                           
                           )

# Hesaplama
@app.route('/<size>/<lights>/<device>')
def end(size, lights, device):
    return render_template('end.html', 
                            result=result_calculate(int(size),
                                                    int(lights), 
                                                    int(device)
                                                    )
                        )

# Form
@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        name = request.form['name']
        date = request.form['date']
        address = request.form['address']
        email = request.form['email']

        with open('form.txt', 'a') as f:
            f.write(f"Name: {name}, Date: {date}, Address: {address}, Email: {email}\n")

        return render_template('form_result.html', 
                               name=name,
                               date=date,
                               address=address,
                               email=email,
                               )
    return render_template('form.html')

# Formun sonuçları
@app.route('/submit', methods=['POST'])
def submit_form():
    name = request.form['name']
    date = request.form['date']
    address = request.form['address']
    email = request.form['email']

    with open('form.txt', 'a') as f:
        f.write(f"Name: {name}, Date: {date}, Address: {address}, Email: {email}\n")

    return render_template('form_result.html', 
                           name=name,
                           date=date,
                           address=address,
                           email=email,
                           )
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Dosya var mı?
        if 'file' not in request.files:
            return jsonify({'error': 'Dosya bulunamadı.'})

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'Bir dosya seçin.'})

        # Dosyayı kaydetme
        try:
            file_path = os.path.join("static/uploads", file.filename)
            file.save(file_path)
        except Exception as e:
            return jsonify({'error': f'Dosya kaydedilemedi: {str(e)}'})

        # Resmi işle ve tahmin yap
        try:
            image_data = prepare_image(file_path)
            prediction = model.predict(image_data)
            index = np.argmax(prediction)
            class_name = class_names[index].strip()
            confidence_score = prediction[0][index]
        except Exception as e:
            return jsonify({'error': f'Tahmin yapılırken hata oluştu: {str(e)}'})

        # Sonuçları döndür
        result = {
            'class': class_name,
            'confidence_score': float(confidence_score)
        }
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': f'Bir hata oluştu: {str(e)}'})



if __name__ == "__main__":
    app.run(debug=True)
