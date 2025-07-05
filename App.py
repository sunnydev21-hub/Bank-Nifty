from flask import Flask, render_template, request
import pickle

app = Flask(__name__)

# Load the trained models
with open('linear_regression_model_high.pkl', 'rb') as f_high:
    model_high = pickle.load(f_high)

with open('linear_regression_model_low.pkl', 'rb') as f_low:
    model_low = pickle.load(f_low)

# Define the function to predict HIGH and LOW results
def predict_high(upcrt, open_val):
    return model_high.predict([[upcrt, open_val]])[0]

def predict_low(lwcrt, open_val):
    return model_low.predict([[lwcrt, open_val]])[0]

@app.route('/', methods=['GET', 'POST'])
def index():
    results_high = {i: None for i in range(1, 11)}
    results_low = {i: None for i in range(1, 11)}
    form_data = {f'upcrt{i}': '' for i in range(1, 11)}
    form_data.update({f'lwcrt{i}': '' for i in range(1, 11)})
    form_data.update({f'open{i}': '' for i in range(1, 11)})

    if request.method == 'POST':
        for i in range(1, 11):
            upcrt_key = f'upcrt{i}'
            lwcrt_key = f'lwcrt{i}'
            open_key = f'open{i}'
            predict_key = f'predict{i}'
            clear_key = f'clear{i}'

            if request.form.get(predict_key):
                upcrt = request.form[upcrt_key]
                lwcrt = request.form[lwcrt_key]
                open_val = request.form[open_key]

                if upcrt and open_val:
                    results_high[i] = predict_high(float(upcrt), float(open_val))
                if lwcrt and open_val:
                    results_low[i] = predict_low(float(lwcrt), float(open_val))

            if request.form.get(clear_key):
                results_high[i] = None
                results_low[i] = None
                form_data[upcrt_key] = ''
                form_data[lwcrt_key] = ''
                form_data[open_key] = ''
            else:
                # Preserve form data and results
                form_data[upcrt_key] = request.form.get(upcrt_key, form_data[upcrt_key])
                form_data[lwcrt_key] = request.form.get(lwcrt_key, form_data[lwcrt_key])
                form_data[open_key] = request.form.get(open_key, form_data[open_key])
                if results_high[i] is not None:
                    form_data[f'result_high{i}'] = results_high[i]
                if results_low[i] is not None:
                    form_data[f'result_low{i}'] = results_low[i]

    return render_template('index.html', results_high=results_high, results_low=results_low, form_data=form_data)

if __name__ == '__main__':
    app.run(debug=True)
