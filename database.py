import sqlite3
import os
from datetime import datetime, timezone, timedelta

def get_brt_time():
    br_tz = timezone(timedelta(hours=-3))
    return datetime.now(br_tz).strftime('%Y-%m-%d %H:%M:%S')


DB_PATH = "tcc_assistant.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    """
    Initializes the SQLite database with the required schema.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            thesis_title TEXT NOT NULL,
            pdf_path TEXT NOT NULL,
            general_opinion TEXT DEFAULT '',
            status TEXT DEFAULT 'In Progress',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS annotations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            page_number INTEGER NOT NULL,
            selected_text TEXT,
            category TEXT,
            professor_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    
    # Handle DB migration for new columns
    cursor.execute("PRAGMA table_info(projects)")
    columns = [info[1] for info in cursor.fetchall()]
    if 'advisor_name' not in columns:
        cursor.execute("ALTER TABLE projects ADD COLUMN advisor_name TEXT DEFAULT ''")
    if 'advisor_email' not in columns:
        cursor.execute("ALTER TABLE projects ADD COLUMN advisor_email TEXT DEFAULT ''")
        
    conn.commit()
    conn.close()

# --- CRUD Operations for Projects ---

def create_project(student_name, thesis_title, advisor_name, advisor_email, pdf_path):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO projects (student_name, thesis_title, advisor_name, advisor_email, pdf_path, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (student_name, thesis_title, advisor_name, advisor_email, pdf_path, get_brt_time()))
    project_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return project_id

def update_project_details(project_id, student_name, thesis_title, advisor_name, advisor_email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE projects 
        SET student_name = ?, thesis_title = ?, advisor_name = ?, advisor_email = ?, updated_at = ?
        WHERE id = ?
    ''', (student_name, thesis_title, advisor_name, advisor_email, get_brt_time(), project_id))
    conn.commit()
    conn.close()

def get_projects():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM projects ORDER BY updated_at DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_project(project_id):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def delete_project(project_id):
    conn = get_connection()
    cursor = conn.cursor()
    # First delete annotations due to foreign key (even if ON DELETE CASCADE is set, it's safer if PRAGMA is off)
    cursor.execute('PRAGMA foreign_keys = ON')
    cursor.execute('DELETE FROM projects WHERE id = ?', (project_id,))
    conn.commit()
    conn.close()

def update_general_opinion(project_id, opinion):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE projects 
        SET general_opinion = ?, updated_at = ?
        WHERE id = ?
    ''', (opinion, get_brt_time(), project_id))
    conn.commit()
    conn.close()

def update_project_status(project_id, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE projects 
        SET status = ?, updated_at = ?
        WHERE id = ?
    ''', (status, get_brt_time(), project_id))
    conn.commit()
    conn.close()

# --- CRUD Operations for Annotations ---

def add_annotation(project_id, page_number, selected_text, category, professor_notes):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO annotations (project_id, page_number, selected_text, category, professor_notes)
        VALUES (?, ?, ?, ?, ?)
    ''', (project_id, page_number, selected_text, category, professor_notes))
    
    # Touch the project's updated_at timestamp
    cursor.execute('''
        UPDATE projects SET updated_at = ? WHERE id = ?
    ''', (get_brt_time(), project_id))
    
    conn.commit()
    conn.close()

def get_annotations(project_id):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM annotations WHERE project_id = ? ORDER BY page_number ASC', (project_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_annotation(annotation_id, page_number, selected_text, category, professor_notes):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE annotations
        SET page_number = ?, selected_text = ?, category = ?, professor_notes = ?
        WHERE id = ?
    ''', (page_number, selected_text, category, professor_notes, annotation_id))
    
    # Touch the project's updated_at timestamp based on annotation_id
    cursor.execute('''
        UPDATE projects 
        SET updated_at = ? 
        WHERE id = (SELECT project_id FROM annotations WHERE id = ?)
    ''', (get_brt_time(), annotation_id))
    
    conn.commit()
    conn.close()

def delete_annotation(annotation_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Touch the project's updated_at timestamp based on annotation_id
    cursor.execute('''
        UPDATE projects 
        SET updated_at = ? 
        WHERE id = (SELECT project_id FROM annotations WHERE id = ?)
    ''', (get_brt_time(), annotation_id))
    
    cursor.execute('DELETE FROM annotations WHERE id = ?', (annotation_id,))
    conn.commit()
    conn.close()

def touch_project(project_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE projects SET updated_at = ? WHERE id = ?
    ''', (get_brt_time(), project_id))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database structure generated successfully.")
