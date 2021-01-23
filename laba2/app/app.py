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
    color=''
    res=' '
    if request.method == 'POST':
        numb= request.form.get('number')
        numb=list(numb)
        n=numb[0]
        num=[]
        if " " in numb or "(" in numb or ")" in numb or "-" in numb or "." in numb or "+" in numb:
            for i in numb:
                if " " == i or "(" == i or ")" == i or "-" == i or "." == i or "+" == i :
                    pass
                elif "0" == i or "1" == i or "2" == i or "3" == i or "4" == i or "5" == i or "6" == i or "7" == i or "8" == i or "9" == i:
                    num.append(i)
                else:
                    msg_error="Недопустимый ввод. В номере телефона встречаются недопустимые символы"
                    color='is-invalid'
            if (len(num)==11 and numb[0]=='8') or (len(num)==11 and num[0]=='7' and numb[0]=='+') or len(num)==10:
                color='is-valid'
                if n=='+':
                    num=num[1:]
                elif n=='8':
                    num.remove('8')
                else:
                    pass
                num.insert(0,'8')
                num.insert(1,'-')
                num.insert(5,'-')
                num.insert(9,'-')
                num.insert(12,'-')
                res="".join(num)
            elif color=="is-invalid":
                pass
            else:
                msg_error="Недопустимый ввод. Неверное количество цифр"
                color='is-invalid'
    return render_template('number.html', msg_error=msg_error, color= color, res=res)

    


"""
@app.route('/calc')
def calc():
   try:
      result = None
      error_msg=None
      op1=float(request.args.get('operand1'))
      op2=float(request.args.get('operand2'))
      f=operation_functions[request.args.get('operation')]
      result=f(op1, op2)
    except ValueError: 
        error_msg= 'Пожалуйста, вводите только числа'
    except ZeroDivisionError:
        error_msg= 'На ноль делить нальзя'
    except KeyError:
        error_msg='Недопустимая операция'
    return render_template('calc.html', operations=operations, result=result, error_msg= error_msg)
"""
    