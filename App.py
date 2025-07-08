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
    # Initialize two tables' state
    call_fd = {i: {'upcrt':'','lwcrt':'','open':''} for i in range(1,11)}
    put_fd  = {i: {'upcrt':'','lwcrt':'','open':''} for i in range(1,11)}
    call_rh = {i: None for i in range(1,11)}
    call_rl = {i: None for i in range(1,11)}
    put_rh  = {i: None for i in range(1,11)}
    put_rl  = {i: None for i in range(1,11)}
    call_err= {i: ''   for i in range(1,11)}
    put_err = {i: ''   for i in range(1,11)}

    if request.method == 'POST':
        # 1) Preserve raw inputs for both tables
        for tbl,fd in [('call',call_fd), ('put',put_fd)]:
            for i in range(1,11):
                fd[i]['upcrt'] = request.form.get(f'upcrt_{tbl}{i}', '').strip()
                fd[i]['lwcrt'] = request.form.get(f'lwcrt_{tbl}{i}', '').strip()
                fd[i]['open']  = request.form.get(f'open_{tbl}{i}',  '').strip()

        # 2) Reload prior results from hidden inputs
        for tbl, rh, rl in [
            ('call', call_rh, call_rl),
            ('put',  put_rh,  put_rl)
        ]:
            for i in range(1,11):
                v1 = request.form.get(f'result_high_{tbl}{i}')
                v2 = request.form.get(f'result_low_{tbl}{i}')
                if v1:
                    try:    rh[i] = float(v1)
                    except: rh[i] = v1
                if v2:
                    try:    rl[i] = float(v2)
                    except: rl[i] = v2

        # 3) Clear All: wipe both tables' inputs & results & errors
        if 'clear_all' in request.form:
            # reinitialize
            call_fd = {i: {'upcrt':'','lwcrt':'','open':''} for i in range(1,11)}
            put_fd  = {i: {'upcrt':'','lwcrt':'','open':''} for i in range(1,11)}
            call_rh = {i: None for i in range(1,11)}
            call_rl = {i: None for i in range(1,11)}
            put_rh  = {i: None for i in range(1,11)}
            put_rl  = {i: None for i in range(1,11)}
            call_err= {i: ''   for i in range(1,11)}
            put_err = {i: ''   for i in range(1,11)}

        # 4) Predict Call?
        elif 'predict_call' in request.form:
            r = int(request.form['predict_call'])
            u = call_fd[r]['upcrt']
            l = call_fd[r]['lwcrt']
            o = call_fd[r]['open']
            if not u:
                call_err[r] = 'Please enter value under UPCRT'
            elif not l:
                call_err[r] = 'Please enter value under LWCRT'
            elif not o:
                call_err[r] = 'Please enter value under Open'
            else:
                try:
                    uh = float(u); lw = float(l); op = float(o)
                    call_rh[r] = predict_high(uh, op)
                    call_rl[r] = predict_low(lw, op)
                    call_err[r] = ''
                except Exception as ex:
                    call_err[r] = f'Prediction error: {ex}'

        # 5) Predict Put?
        elif 'predict_put' in request.form:
            r = int(request.form['predict_put'])
            u = put_fd[r]['upcrt']
            l = put_fd[r]['lwcrt']
            o = put_fd[r]['open']
            if not u:
                put_err[r] = 'Please enter value under UPCRT'
            elif not l:
                put_err[r] = 'Please enter value under LWCRT'
            elif not o:
                put_err[r] = 'Please enter value under Open'
            else:
                try:
                    uh = float(u); lw = float(l); op = float(o)
                    put_rh[r] = predict_high(uh, op)
                    put_rl[r] = predict_low(lw, op)
                    put_err[r] = ''
                except Exception as ex:
                    put_err[r] = f'Prediction error: {ex}'

    return render_template(
        'index.html',
        call_fd=call_fd,  put_fd=put_fd,
        call_rh=call_rh,  call_rl=call_rl,
        put_rh=put_rh,    put_rl=put_rl,
        call_err=call_err, put_err=put_err
    )

if __name__ == '__main__':
    app.run(debug=True)