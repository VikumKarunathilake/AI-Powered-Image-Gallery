from flask import Flask, render_template, abort, request, jsonify, redirect, url_for, flash
# from flask_wtf.csrf import CSRFProtect
import psycopg2
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')
# csrf = CSRFProtect(app)

def get_db_connection():
    conn_string = os.getenv('DATABASE_URL')
    if conn_string is None:
        raise Exception("Database connection string not found.")
    try:
        print("Connecting to database....")  # Debugging line
        conn = psycopg2.connect(conn_string)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")  # Debugging line
        raise
    
@app.route('/')
def index():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM images WHERE approved = TRUE LIMIT 12;')  # Show 6 images on the index page
        images = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")  # Debugging line
        abort(500, description="An error occurred while accessing the database.")
    return render_template('index.html', images=images)

@app.route('/gallery')
def gallery():
    # Pagination logic
    page = request.args.get('page', 1, type=int)
    per_page = 12  # Number of images per page
    offset = (page - 1) * per_page

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM images WHERE approved = TRUE;')
        total_images = cur.fetchone()[0]  # Get total count of images

        cur.execute('SELECT * FROM images WHERE approved = TRUE ORDER BY id LIMIT %s OFFSET %s;', (per_page, offset))
        paginated_images = cur.fetchall()

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")  # Debugging line
        abort(500, description="An error occurred while accessing the database.")

    return render_template('gallery.html', images=paginated_images, page=page,
                           total_images=total_images, per_page=per_page)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of images to display per page

    # Handle POST requests (Approve or Delete images)
    if request.method == 'POST':
        image_id = request.form.get('image_id')
        action = request.form.get('action')

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                if action == 'approve':
                    cur.execute('UPDATE images SET approved = TRUE WHERE id = %s', (image_id,))
                    flash('Image approved successfully', 'success')
                elif action == 'delete':
                    cur.execute('DELETE FROM images WHERE id = %s', (image_id,))
                    flash('Image deleted successfully', 'danger')

            conn.commit()

        return redirect(url_for('admin'))

    # Handle GET requests (Display unapproved images)
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT COUNT(*) FROM images WHERE approved = FALSE')
            total_images = cur.fetchone()[0]
            
            cur.execute('SELECT * FROM images WHERE approved = FALSE ORDER BY upload_time DESC LIMIT %s OFFSET %s',
                        (per_page, (page - 1) * per_page))
            images = cur.fetchall()

    # Pagination logic
    total_pages = (total_images + per_page - 1) // per_page

    return render_template('admin.html', images=images, page=page, total_pages=total_pages)



if __name__ == '__main__':
    app.run(debug=True)