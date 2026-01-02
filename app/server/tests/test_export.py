"""
Unit tests for CSV export endpoints
"""

import pytest
import sqlite3
import tempfile
import os
import csv
import io
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Save reference to real sqlite3.connect before any mocking
_real_sqlite3_connect = sqlite3.connect


@pytest.fixture
def test_db():
    """Create a test database with sample data"""
    db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    db_file.close()

    conn = sqlite3.connect(db_file.name)
    cursor = conn.cursor()

    # Create test tables
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT,
            age INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL
        )
    ''')

    cursor.execute('''
        CREATE TABLE empty_table (
            id INTEGER PRIMARY KEY,
            name TEXT
        )
    ''')

    # Insert test data
    cursor.execute("INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
                   ('Alice', 'alice@example.com', 30))
    cursor.execute("INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
                   ('Bob', 'bob@example.com', 25))
    cursor.execute("INSERT INTO products (name, price) VALUES (?, ?)",
                   ('Widget', 19.99))

    conn.commit()
    conn.close()

    yield db_file.name

    # Cleanup
    os.unlink(db_file.name)


@pytest.fixture
def client(test_db):
    """Create a test client with mocked database path"""
    with patch('server.sqlite3.connect') as mock_connect:
        def connect_to_test_db(path):
            return sqlite3.connect(test_db)
        mock_connect.side_effect = connect_to_test_db

        from server import app
        with TestClient(app) as c:
            yield c


class TestTableExportEndpoint:
    """Tests for GET /api/table/{table_name}/export endpoint"""

    def test_export_table_success(self, test_db):
        """Test successful table export returns valid CSV with correct data"""
        with patch('server.sqlite3.connect') as mock_connect:
            # Use side_effect with the saved real connect function
            mock_connect.side_effect = lambda path: _real_sqlite3_connect(test_db)

            from server import app
            with TestClient(app) as client:
                response = client.get("/api/table/users/export")

                assert response.status_code == 200
                assert response.headers["content-type"] == "text/csv; charset=utf-8"
                assert 'attachment; filename="users.csv"' in response.headers["content-disposition"]

                # Parse CSV content
                csv_content = response.content.decode('utf-8')
                reader = csv.reader(io.StringIO(csv_content))
                rows = list(reader)

                # Check headers
                assert rows[0] == ['id', 'name', 'email', 'age']

                # Check data rows
                assert len(rows) == 3  # header + 2 data rows
                assert rows[1][1] == 'Alice'
                assert rows[2][1] == 'Bob'

    def test_export_table_not_found(self, test_db):
        """Test export of non-existent table returns 404"""
        with patch('server.sqlite3.connect') as mock_connect:
            mock_connect.side_effect = lambda path: _real_sqlite3_connect(test_db)

            from server import app
            with TestClient(app) as client:
                response = client.get("/api/table/nonexistent_table/export")

                assert response.status_code == 404
                assert "not found" in response.json()["detail"].lower()

    def test_export_table_invalid_name_sql_injection(self, test_db):
        """Test export with SQL injection attempt in table name returns 400"""
        with patch('server.sqlite3.connect') as mock_connect:
            mock_connect.side_effect = lambda path: _real_sqlite3_connect(test_db)

            from server import app
            with TestClient(app) as client:
                # SQL injection attempt
                response = client.get("/api/table/users'; DROP TABLE users; --/export")

                assert response.status_code == 400
                assert "invalid" in response.json()["detail"].lower()

    def test_export_empty_table(self, test_db):
        """Test export of empty table returns CSV with headers only"""
        with patch('server.sqlite3.connect') as mock_connect:
            mock_connect.side_effect = lambda path: _real_sqlite3_connect(test_db)

            from server import app
            with TestClient(app) as client:
                response = client.get("/api/table/empty_table/export")

                assert response.status_code == 200

                # Parse CSV content
                csv_content = response.content.decode('utf-8')
                reader = csv.reader(io.StringIO(csv_content))
                rows = list(reader)

                # Should have headers only
                assert len(rows) == 1
                assert rows[0] == ['id', 'name']

    def test_csv_format_correct(self, test_db):
        """Test CSV has correct format (RFC 4180 compliant)"""
        with patch('server.sqlite3.connect') as mock_connect:
            mock_connect.side_effect = lambda path: _real_sqlite3_connect(test_db)

            from server import app
            with TestClient(app) as client:
                response = client.get("/api/table/users/export")

                csv_content = response.content.decode('utf-8')

                # Verify it's valid CSV by parsing
                reader = csv.reader(io.StringIO(csv_content))
                rows = list(reader)

                # All rows should have the same number of columns
                num_columns = len(rows[0])
                for row in rows:
                    assert len(row) == num_columns


class TestQueryExportEndpoint:
    """Tests for POST /api/query/export endpoint"""

    @patch('server.generate_sql')
    @patch('server.execute_sql_safely')
    @patch('server.get_database_schema')
    def test_export_query_success(self, mock_schema, mock_execute, mock_generate):
        """Test successful query export returns valid CSV"""
        mock_schema.return_value = {'tables': {'users': {'columns': {'id': 'INTEGER'}}}}
        mock_generate.return_value = "SELECT * FROM users"
        mock_execute.return_value = {
            'results': [
                {'id': 1, 'name': 'Alice', 'email': 'alice@example.com'},
                {'id': 2, 'name': 'Bob', 'email': 'bob@example.com'}
            ],
            'columns': ['id', 'name', 'email'],
            'error': None
        }

        from server import app
        with TestClient(app) as client:
            response = client.post(
                "/api/query/export",
                json={"query": "Show me all users"}
            )

            assert response.status_code == 200
            assert response.headers["content-type"] == "text/csv; charset=utf-8"
            assert 'attachment; filename="query_results.csv"' in response.headers["content-disposition"]

            # Parse CSV content
            csv_content = response.content.decode('utf-8')
            reader = csv.reader(io.StringIO(csv_content))
            rows = list(reader)

            # Check headers
            assert rows[0] == ['id', 'name', 'email']

            # Check data rows
            assert len(rows) == 3  # header + 2 data rows

    @patch('server.generate_sql')
    @patch('server.execute_sql_safely')
    @patch('server.get_database_schema')
    def test_export_query_empty_results(self, mock_schema, mock_execute, mock_generate):
        """Test query with no results returns empty CSV (just headers)"""
        mock_schema.return_value = {'tables': {'users': {'columns': {'id': 'INTEGER'}}}}
        mock_generate.return_value = "SELECT * FROM users WHERE id = -1"
        mock_execute.return_value = {
            'results': [],
            'columns': ['id', 'name', 'email'],
            'error': None
        }

        from server import app
        with TestClient(app) as client:
            response = client.post(
                "/api/query/export",
                json={"query": "Show me user with id -1"}
            )

            assert response.status_code == 200

            # Parse CSV content
            csv_content = response.content.decode('utf-8')
            reader = csv.reader(io.StringIO(csv_content))
            rows = list(reader)

            # Should have headers only
            assert len(rows) == 1
            assert rows[0] == ['id', 'name', 'email']

    @patch('server.generate_sql')
    @patch('server.execute_sql_safely')
    @patch('server.get_database_schema')
    def test_export_query_error(self, mock_schema, mock_execute, mock_generate):
        """Test query with error returns appropriate error response"""
        mock_schema.return_value = {'tables': {'users': {'columns': {'id': 'INTEGER'}}}}
        mock_generate.return_value = "SELECT * FROM nonexistent"
        mock_execute.return_value = {
            'results': [],
            'columns': [],
            'error': 'Table not found'
        }

        from server import app
        with TestClient(app) as client:
            response = client.post(
                "/api/query/export",
                json={"query": "Show me data from nonexistent"}
            )

            assert response.status_code == 400

    @patch('server.generate_sql')
    @patch('server.execute_sql_safely')
    @patch('server.get_database_schema')
    def test_export_query_csv_format(self, mock_schema, mock_execute, mock_generate):
        """Test query export CSV has correct format"""
        mock_schema.return_value = {'tables': {'users': {'columns': {'id': 'INTEGER'}}}}
        mock_generate.return_value = "SELECT id, name FROM users"
        mock_execute.return_value = {
            'results': [
                {'id': 1, 'name': 'Alice'},
                {'id': 2, 'name': 'Bob'}
            ],
            'columns': ['id', 'name'],
            'error': None
        }

        from server import app
        with TestClient(app) as client:
            response = client.post(
                "/api/query/export",
                json={"query": "Show me user names"}
            )

            csv_content = response.content.decode('utf-8')

            # Verify it's valid CSV
            reader = csv.reader(io.StringIO(csv_content))
            rows = list(reader)

            # All rows should have the same number of columns
            num_columns = len(rows[0])
            for row in rows:
                assert len(row) == num_columns
