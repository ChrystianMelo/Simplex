import subprocess
import sys

packages = ["networkx", "matplotlib"]

try:
    import networkx as nx
    import matplotlib.pyplot as plt
    print("Pacotes de plotagem de grafico já instalados.")
except ImportError:
    print("Instalando pacotes de plotagem de grafico...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", *packages])
    import networkx as nx
    import matplotlib.pyplot as plt
    print("Pacotes instalados com sucesso.")

G = nx.path_graph(4)
print("Grafico criado para teste:", list(G.edges()))
print("Ambiente pronto para plotar graficos.")
