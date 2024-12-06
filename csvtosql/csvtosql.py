import os
import pandas as pd
from sqlalchemy import create_engine

# Configuración de conexión a SQL Server
db_config = {
    'host': os.getenv('DB_HOST', 'sqlserver'),
    'port': os.getenv('DB_PORT', '1433'),
    'user': os.getenv('DB_USER', 'sa'),
    'password': os.getenv('DB_PASSWORD', 'iWZJM5j89{ez'),
    'database': os.getenv('DB_NAME', 'mydatabase')
}

# Crear motor de conexión con SQLAlchemy
engine = create_engine(
    f"mssql+pyodbc://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}?driver=ODBC%20Driver%2018%20for%20SQL%20Server&TrustServerCertificate=yes"
)

# Directorio de archivos CSV
csv_dir = '/csvtosql/csv'

def load_csv_to_sqlserver(file_path, table_name):
    """
    Carga un archivo CSV en SQL Server.
    """
    print(f"Importando {file_path} a la tabla {table_name}...")
    df = pd.read_csv(file_path)
    df.to_sql(table_name, con=engine, if_exists='append', index=False)
    print(f"Archivo {file_path} importado con éxito.")

def main():
    for file_name in os.listdir(csv_dir):
        if file_name.endswith('.csv'):
            file_path = os.path.join(csv_dir, file_name)
            table_name = os.path.splitext(file_name)[0]  # Nombre de la tabla basado en el archivo
            load_csv_to_sqlserver(file_path, table_name)

if __name__ == "__main__":
    main()
