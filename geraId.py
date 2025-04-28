from random import randint

class GeraId:
    """
    Classe responsável por gerar identificadores (IDs) únicos
    aleatórios no intervalo de 1 a 20.
    """

    def __init__(self):
        """Inicializa uma lista vazia para armazenar os IDs já gerados."""
        self._ids_gerados = []

    def gerar_id(self):
        """
        Gera um novo ID aleatório entre 1 e 20 que ainda não foi utilizado.
        
        Retorna:
            int: Um número único ainda não gerado.
        """

        while True:
            novo_id = randint(1, 20)
            if novo_id not in self._ids_gerados:
                self._ids_gerados.append(novo_id)
                return novo_id

    def get_all_id(self):
        """
        Retorna a lista de todos os IDs já gerados.

        Retorna:
            list: Lista de números inteiros já gerados.
        """
        return self._ids_gerados.copy()
