import psycopg2
from psycopg2.extras import execute_values
import numpy as np

def test_pgvector(connection_string):
    try:
        # Connect to the database
        conn = psycopg2.connect(connection_string)
        cur = conn.cursor()
        
        # Enable pgvector extension if not already enabled
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        
        # Create a test table
        cur.execute("""
            DROP TABLE IF EXISTS vector_test;
            CREATE TABLE vector_test (
                id serial PRIMARY KEY,
                description text,
                embedding vector(3)
            );
        """)
        
        # Generate some test data
        test_data = [
            ("red", [1.0, 0.0, 0.0]),
            ("green", [0.0, 1.0, 0.0]),
            ("blue", [0.0, 0.0, 1.0]),
            ("yellow", [1.0, 1.0, 0.0])
        ]
        
        # Insert test data
        execute_values(
            cur,
            "INSERT INTO vector_test (description, embedding) VALUES %s",
            [(desc, embedding) for desc, embedding in test_data],
            template="(%s, %s::vector)"
        )
        
        # Perform a vector similarity search
        query_vector = [1.0, 0.0, 0.0]  # Search for vectors similar to "red"
        cur.execute("""
            SELECT description, embedding <-> %s::vector AS distance
            FROM vector_test
            ORDER BY distance
            LIMIT 3;
        """, (query_vector,))
        
        print("\nVector similarity search results:")
        results = cur.fetchall()
        for desc, distance in results:
            print(f"Color: {desc}, Distance: {distance}")
        
        conn.commit()
        print("\nAll pgvector operations completed successfully!")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    # Replace this with your actual connection string
    connection_string = "postgres://postgres:qr7wjSV3qBgxHIv@localhost:5432/postgres"
    test_pgvector(connection_string)
