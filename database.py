from firebase import firebase

# URL de tu Realtime Database
firebase_url = 'https://proyecto-mapa-25804-default-rtdb.firebaseio.com/'

# Inicializar la conexión sin credenciales JSON
firebase_db = firebase.FirebaseApplication(firebase_url, None)

# Clase localitation
class localitation:
    def __init__(self, latitud, longitud, descripcion, tipo):
        self.latitud = latitud
        self.longitud = longitud
        self.descripcion = descripcion
        self.tipo = tipo

    def save(self):
        data = {
            'latitud': self.latitud,
            'longitud': self.longitud,
            'descripcion': self.descripcion,
            'tipo': self.tipo
        }
        result = firebase_db.post('/localizaciones', data)
        return result  # El resultado de la operación contiene la clave de Firebase

