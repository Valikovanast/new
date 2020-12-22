from flask import Flask, render_template, request, make_response 
import operator as op
app=Flask(__name__)

operations=['+', '-', '*', '/']
operation_functions={'+': op.add, '-': op.sub, '*': op.mul, '/':op.truediv }
signs=[' ', '(', ')', '-', '.', '+']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/args')
def args():
    return render_template('args.html')

@app.route('/headers')
def headers():
    return render_template('headers.html')

@app.route('/cookies')
def cookies():
    resp = make_response(render_template('cookies.html'))
    if 'username' in request.cookies:
        resp.set_cookie('username', 'some name', expires=0)
    else:
        resp.set_cookie('username', 'some name')
    return resp

@app.route('/form', methods=['GET', 'POST'] )
def form():
    return render_template('form.html')

@app.route('/number', methods= ['GET','POST'])
def number():
    msg_error= None
    if request.method == 'POST':
        numb= request.form.get('number')
        counting = 0
        while len(str(numb)) !=0:
            counting+=1
            str(numb)[:-1]
        if numb in signs:
            pass
        elif counting!=10 or counting!=11:
            msg_error="Недопустимый ввод. Неверное количество цифр"
        else:
            msg_error="Недопустимый ввод. В номере телефона встречаются недопустимые символы"
    return render_template('number.html', msg_error=msg_error)

    

#@app.route('/calc')
#def calc():
#   try:
#      result = None
#       error_msg=None
#       op1=float(request.args.get('operand1'))
#       op2=float(request.args.get('operand2'))
#       f=operation_functions[request.args.get('operation')]
#       result=f(op1, op2)
#    except ValueError: 
#        error_msg= 'Пожалуйста, вводите только числа'
#    except ZeroDivisionError:
#        error_msg= 'На ноль делить нальзя'
#    except KeyError:
#        error_msg='Недопустимая операция'
#    return render_template('calc.html', operations=operations, result=result, error_msg= error_msg)

    