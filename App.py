from flask import Flask, render_template, request
import pickle

app = Flask(__name__)

# Load the trained models
with open('linear_regression_model_high.pkl', 'rb') as f:
    model_high = pickle.load(f)
with open('linear_regression_model_low.pkl', 'rb') as f:
    model_low  = pickle.load(f)

def predict_high(upcrt, open_val):
    return model_high.predict([[upcrt, open_val]])[0]

def predict_low(lwcrt, open_val):
    return model_low.predict([[lwcrt, open_val]])[0]

@app.route('/', methods=['GET', 'POST'])
def index():
    # initialize
    results_high = {i: None for i in range(1, 11)}
    results_low  = {i: None for i in range(1, 11)}
    form_data    = {f'upcrt{i}': '' for i in range(1, 11)}
    form_data.update({f'lwcrt{i}': '' for i in range(1, 11)})
    form_data.update({f'open{i}': ''  for i in range(1, 11)})
    errors       = {i: '' for i in range(1, 11)}

    if request.method == 'POST':
        # 1) Preserve inputs
        for i in range(1, 11):
            form_data[f'upcrt{i}'] = request.form.get(f'upcrt{i}', '').strip()
            form_data[f'lwcrt{i}'] = request.form.get(f'lwcrt{i}', '').strip()
            form_data[f'open{i}']  = request.form.get(f'open{i}', '').strip()

        # 2) Reload any previous results from hidden fields
        for i in range(1, 11):
            rh = request.form.get(f'result_high{i}')
            rl = request.form.get(f'result_low{i}')
            if rh:
                try:    results_high[i] = float(rh)
                except: results_high[i] = rh
            if rl:
                try:    results_low[i] = float(rl)
                except: results_low[i] = rl

        # 3) Clear All Results?
        if 'clear_all' in request.form:
            results_high = {i: None for i in range(1, 11)}
            results_low  = {i: None for i in range(1, 11)}
            errors       = {i: ''   for i in range(1, 11)}

        # 4) Predict button?
        elif 'predict' in request.form:
            row = int(request.form['predict'])
            u   = form_data[f'upcrt{row}']
            l   = form_data[f'lwcrt{row}']
            o   = form_data[f'open{row}']

            # validate
            if not u:
                errors[row] = 'Please enter value under UPCRT'
            elif not l:
                errors[row] = 'Please enter value under LWCRT'
            elif not o:
                errors[row] = 'Please enter value under Open'
            else:
                try:
                    uh = float(u)
                    lw = float(l)
                    op = float(o)
                    results_high[row] = predict_high(uh, op)
                    results_low[row]  = predict_low(lw, op)
                    errors[row] = ''
                except Exception as ex:
                    errors[row] = f'Prediction error: {ex}'

    return render_template(
        'index.html',
        form_data=form_data,
        results_high=results_high,
        results_low=results_low,
        errors=errors
    )

if __name__ == '__main__':
    app.run(debug=True)