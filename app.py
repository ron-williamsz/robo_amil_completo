from flask import Flask, render_template, url_for, send_from_directory
import subprocess
import signal
import os

# Obtenha o caminho absoluto para o diretório do script atual
basedir = os.path.abspath(os.path.dirname(__file__))

# Configure o Flask com o caminho correto para a pasta static
app = Flask(__name__, static_folder=os.path.join(basedir, 'static'), static_url_path='/static')
robo_process = None
robo_paused = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/executar_robo')
def executar_robo():
    global robo_process
    if robo_process is None:
        robo_process = subprocess.Popen(['python', 'main.py'])
        return "Robô iniciado"
    else:
        return "Robô já está em execução"

@app.route('/parar_robo')
def parar_robo():
    global robo_process
    if robo_process is not None:
        os.kill(robo_process.pid, signal.SIGTERM)
        robo_process = None
        return "Robô parado"
    else:
        return "Robô não está em execução"

@app.route('/pausar_robo')
def pausar_robo():
    global robo_process, robo_paused
    if robo_process is not None:
        if not robo_paused:
            with open('pause.flag', 'w') as f:
                f.write('1')
            robo_paused = True
            return "Robô pausado"
        else:
            if os.path.exists('pause.flag'):
                os.remove('pause.flag')
            robo_paused = False
            return "Robô retomado"
    else:
        return "Robô não está em execução"

@app.route('/recarregar')
def recarregar():
    subprocess.Popen(['python', 'utilReloaded.py'])
    return "Recarregado"

@app.route('/test_image')
def test_image():
    return send_from_directory(app.static_folder, 'amil.png')

if __name__ == '__main__':
    print(f"Caminho da pasta static: {app.static_folder}")
    app.run(host='0.0.0.0',debug=True, port=3005)