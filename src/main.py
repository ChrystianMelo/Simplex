import matplotlib.pyplot as plt


def main():
    x = [0, 1, 2, 3, 4]
    y = [0, 1, 4, 9, 16]

    plt.figure()
    plt.plot(x, y, marker='o')
    plt.title('Gráfico simples')
    plt.xlabel('x')
    plt.ylabel('y = x²')
    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    main()
