import subprocess
import sys
import os

def setup_environment():
    """
    Cria um ambiente virtual, ativa-o e instala as dependências.
    """
    venv_dir = "venv"
    requirements_file = "requirements.txt"

    print(f"1. Criando ambiente virtual em '{venv_dir}'...")
    try:
        subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
        print("Ambiente virtual criado com sucesso.")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao criar ambiente virtual: {e}")
        return

    # Ativação do ambiente (apenas para subprocessos subsequentes)
    # Para o script atual, usamos o python.exe dentro do venv para instalar.
    python_executable = os.path.join(venv_dir, "Scripts", "python.exe") if sys.platform == "win32" \
                        else os.path.join(venv_dir, "bin", "python")

    if not os.path.exists(python_executable):
        print(f"Erro: Executável Python não encontrado em '{python_executable}'. Verifique a criação do venv.")
        return

    print(f"2. Instalando dependências de '{requirements_file}'...")
    try:
        subprocess.run([python_executable, "-m", "pip", "install", "-r", requirements_file], check=True)
        print("Dependências instaladas com sucesso.")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao instalar dependências: {e}")
        return

    print("\nConfiguração do ambiente concluída!")
    print(f"Para ativar o ambiente virtual, execute:")
    if sys.platform == "win32":
        print(f".\\{venv_dir}\\Scripts\\activate")
    else:
        print(f"source ./{venv_dir}/bin/activate")
    print("Depois disso, você pode rodar seu projeto.")

if __name__ == "__main__":
    setup_environment()