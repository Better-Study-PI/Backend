class btreeDriver:
    def __init__(self, id: int, driver=None):
        self.esquerda: btreeDriver = None
        self.direita: btreeDriver = None
        self.id: int = id
        self.driver = driver

    def setDriver(self, driver):
        self.driver = driver
    
    def getDriver(self):
        return self.driver
    
    def getId(self):
        return self.id

    def insere_no(self, id, driver=None):
        if id < self.id:
            if not self.esquerda:
                self.esquerda = btreeDriver(id)
                self.esquerda.driver = driver
            else:
                self.esquerda.insere(id, driver)
        else:
            if not self.direita:
                self.direita = btreeDriver(id)
                self.direita.driver = driver
            else:
                self.direita.insere(id, driver)

    def get_all_ordenado(self):
        if self.esquerda:
            self.esquerda.get_all_ordenado()
        print(f'ID: {self.id}, Driver: {self.driver}')
        if self.direita:
            self.direita.get_all_ordenado()

    def encontra(self, id):
        if id < self.id:
            if not self.esquerda:
                return None
            else:
                return self.esquerda.encontra(id)
        elif id > self.id:
            if not self.direita:
                return None
            else:
                return self.direita.encontra(id)
        elif id == self.id:
            return self