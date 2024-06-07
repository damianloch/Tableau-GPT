from sqlalchemy import create_engine, text

# Replace with your actual password
engine = create_engine('postgresql://postgres:postgres2024@localhost/GPT-Demo')

def test_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
            tables = [row[0] for row in result]
            print("Tables in the database:")
            for table in tables:
                print(table)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_connection()